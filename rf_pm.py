# This is the postmortem back end for the RF(and BPMs)
#
# The program waits for a reponse on all the monitored channels, then it
# checks the time stamps are all the smae. If not it will continue waiting
# checking the timestamps each time a channel is updated. Once all timestamps
# agree the data is written to a mat file (not yet it isn't). The program then
# waits for 5 sec before looking again.  this should work for both the BPM and
# RF post mortems (with differing tollerances on the timestamping and delay).
# Need to add a time out so it can cope with a missing signal (does camonitor
# throw an error in that case?) Apparently not it just sits there. Is there a
# timeout option on camonitor?

import sys
import os

# This needs to be set before loading matplotlib so that it uses the correct
# temporary workspace for its files.
# Note that this needs to be set before calling require() below as it turns out
# that require() triggers some module loading events!
os.environ['MPLCONFIGDIR'] = '/tmp'

# Sets the max waveform size for EPICS.  This needs to be set *before* we
# load the cothread library so that CA pays attention to it.
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '3000000'


from pkg_resources import require
require('cothread==2.10')
require('matplotlib==0.99.3-r0')
require('scipy==0.10.1')
require('iocbuilder==3.45')


import datetime, time
import cothread
from cothread import catools
import numpy
import scipy.io
import elog
import plotserv
from softioc import builder
from softioc import pvlog

from config import *


RFPMS = ['SR-RF-PM-%02d' % id for id in VALID_PMS]

FNAME = 'rf_postmortem'


# Routine for invoking a fork with all the appropriate precautions
# Actually, in principle even this isn't safe, see:
#   http://www.linuxprogrammingblog.com/\
#       threads-and-fork-think-twice-before-using-them
# Never mind.  We'll do it anyway...
def safe_fork(fn, *args, **kargs):
    pid = os.fork()
    if pid == 0:
        try:
            fn(*args, **kargs)
        except:
            import traceback
            traceback.print_exc()

        # Rather important that we exit immediately, even if anything
        # above fails.  Also we don't want to do any extra cleaning up,
        # that's the parent process's job.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
    else:
        # We'd better wait for the fork to complete, otherwise we'll spawn
        # innumerable zombies.
        os.waitpid(pid, 0)


# Each instance of this class monitors a single BPM and writes the postmortem
# file for that BPM.
class Saver:
    def __init__(self, id, pv_list, wf_len, on_event):
        self.id = id
        self.pv_list = pv_list
        self.on_event = on_event
        self.pv_count = len(pv_list)
        self.results = numpy.zeros((self.pv_count, wf_len), dtype = float)
        # lookup index name from channel name
        self.stamps = numpy.zeros(self.pv_count)
        self.seen = numpy.zeros(self.pv_count, dtype = bool)
        self.triggered = False
        #connect pvs
        catools.camonitor(self.pv_list, self.update_array_entry,
            format = catools.FORMAT_TIME, notify_disconnect = False)

    def update_array_entry(self, new_value, index):
        # Record the incoming data.
        self.results[index] = new_value
        self.stamps[index] = new_value.timestamp
        self.seen[index] = True

        if self.seen.all():
            # If we've seen them all then check that they've all got the same
            # timestamp.
            if (self.stamps == self.stamps[0]).all():
                if self.triggered:
                    print 'Ignoring trigger at time', new_value.timestamp
                else:
                    self.triggered = True
                    self.write_result(new_value)
                    # Refuse to trigger for another five seconds
                    cothread.Timer(5, self.reset)

                # Once we've processed (or discarded) a complete consistent
                # sample reset all the flags until next time.
                self.results[:] = 0
                self.seen[:] = False
            else:
                # If the timestamps don't match keep on watching until they
                # do.
                print 'Timestamps don\'t match'


    def filename(self, new_value):
        # Computes the filename from the timestamp in UTC format in seconds.
        dt = datetime.datetime.utcfromtimestamp(new_value.timestamp)
        dirname = '%4d-%02d' % (dt.year, dt.month)
        dirname = os.path.join(PMDIR, dirname)
        datestring = dt.replace(microsecond = 0).isoformat()
        filename = os.path.join(dirname,
            '%s-%02d-%s.mat' % (FNAME, self.id, datestring))
        return dirname, filename, dt


    # we've got all the channels
    def write_result(self, new_value):
        dirname, filename, dt = self.filename(new_value)

        if os.path.isfile(filename):
            print 'File %s already exists' % filename
        else:
            # Convert the results into complex numbers
            result = self.results.reshape(self.pv_count/2, 2, -1)
            result = result[:, 0] + 1j * result[:, 1]

            if not os.path.isdir(dirname):
                print 'Creating', dirname
                os.mkdir(dirname)
            print 'Writing pm', filename
            data = dict(pm = result, time = new_value.timestamp)
            scipy.io.savemat(filename, data, appendmat=True, oned_as='column')

            # Notify the logger
            self.on_event(dt, result, filename)


    def reset(self):
        self.triggered = False


# The following message is written to e-log on successful writing of a group
# of postmortem files.
PM_MESSAGE = \
    'Saved in %(filename)s\n' + \
    'Run the following command in a terminal window to view it:\n' + \
    '%(where)s/rf_pm_frontend.py %(filename)s'


# This class aggregates updates from all of the reported postmortems.
class Logger:
    def __init__(self, valid_ids):
        self.valid_ids = valid_ids
        self.reset()
        self.timer = None

    def reset(self):
        self.pms = dict(
            [(id, numpy.zeros([4, 2000])) for id in self.valid_ids])
        self.seen = dict([(id, False) for id in self.valid_ids])
        self.filenames = dict([(id, '') for id in self.valid_ids])

    def log_event(self, id):
        return lambda *args: self.process_one_event(id, *args)

    def process_one_event(self, id, time, result, filename):
        if self.seen[id]:
            print 'PM %d already seen!' % id
        else:
            self.time = time
            self.pms[id] = result
            self.seen[id] = True
            self.filenames[id] = filename
        if all(self.seen.values()):
            self.log_new_event()
        elif not self.timer:
            self.timer = cothread.Timer(10, self.log_new_event)

    # All events have arrived, or at least we've given up waiting.
    def log_new_event(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

        # Because the plotting library shows a memory leak, we fork the process
        # of generating the elog entry.
        safe_fork(self.write_elog_entry)
        self.reset()

    def write_elog_entry(self):
        buf = plotserv.display_waveforms(
            self.time, *[self.pms[id] for id in self.valid_ids])
        message = 'RF Postmortem.  Files written to:\n%s' % \
            '\n'.join([self.filenames[id] for id in self.valid_ids])
        elog.entry('RF Postmortem', message, buf, DEBUG)
        print 'Logged RF Postmortem'




# epics channels for RF
pv_lists = [
    ['%s:PM:WF%c%c' % (rfpm, button, iq)
        for button in 'ABCD'
        for iq in 'IQ']
    for rfpm in RFPMS]


# save task
logger = Logger(VALID_PMS)
savers = [
    Saver(id, pv_list, 2**14, logger.log_event(id))
    for id, pv_list in zip(VALID_PMS, pv_lists)]


# A couple of identification PVs
builder.SetDeviceName('CS-DI-IOC-07')
builder.stringIn('WHOAMI', VAL = 'RF Postmortem Server')
builder.stringIn('HOSTNAME', VAL = os.uname()[1])

builder.LoadDatabase()

from softioc import softioc
softioc.iocInit()

softioc.interactive_ioc(globals())
