#!/dls_sw/tools/bin/dls-python2.4

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


if __name__ == '__main__':
    from pkg_resources import require as Require
    Require('numpy==1.1.0')
    Require('cothread==1.15')
    Require('matplotlib == 0.91.1')



import sys
DEBUG = 'D' in sys.argv

if DEBUG:
    PMDIR = '/tmp/rfpm'
else:
    # Values for operation
    PMDIR = '/dls/ops-data/Postmortems/RF_Postmortems'
    
RFPMS = ['SR-RF-PM-%02d' % (id+1) for id in range(3)]


# Sets the max waveform size for EPICS.  This needs to be set *before* we
# load the cothread library so that CA pays attention to it!
import os, datetime, time
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '3000000'

from cothread import *
from cothread.cothread import Timer
from cothread.catools import *
from numpy import *
from scipy.io import savemat
import elog
import plotserv

FNAME = 'rf_postmortem'


# Each instance of this class monitors a single BPM and writes the postmortem
# file for that BPM.
class Saver:
    def __init__(self, id, pv_list, wf_len, on_event):
        self.id = id
        self.pv_list = pv_list
        self.on_event = on_event
        self.pv_count = len(pv_list)
        self.results = zeros((self.pv_count, wf_len), dtype = float)
        # lookup index name from channel name
        self.stamps = zeros(self.pv_count)
        self.seen = zeros(self.pv_count, dtype = bool)
        self.triggered = False
        #connect pvs
        camonitor(self.pv_list, self.update_array_entry,
            format = FORMAT_TIME, notify_disconnect = False)
            
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
                    Timer(5, self.reset)

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
            savemat(filename, data, appendmat=True)

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
    def __init__(self, count):
        self.count = count
        self.reset()
        self.timer = None

    def reset(self):
        self.pms = [zeros([4, 2000])] * self.count
        self.seen = [False] * self.count
        self.filenames = [''] * self.count
        
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
        if all(self.seen):
            self.log_new_event()
        elif not self.timer:
            self.timer = Timer(10, self.log_new_event)

    # All events have arrived, or at least we've given up waiting.
    def log_new_event(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

        
        buf = plotserv.display_waveforms(self.time, *self.pms)
        message = 'RF Postmortem.  Files written to:\n%s' % \
            '\n'.join([f for f in self.filenames if f])
        elog.entry('RF Postmortem', message, buf, DEBUG)
        print 'Logged RF Postmortem'

        self.reset()
        
            
  
# epics channels for RF
pv_lists = [
    ['%s:PM:WF%c%c' % (rfpm, button, iq)
        for button in 'ABCD'
        for iq in 'IQ']
    for rfpm in RFPMS]


# save task
if __name__ == '__main__':
    logger = Logger(len(RFPMS))
    savers = [
        Saver(id + 1, pv_list, 2**14, logger.log_event(id))
        for id, pv_list in enumerate(pv_lists)]
    WaitForQuit()
