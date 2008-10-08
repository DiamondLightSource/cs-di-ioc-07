#!/dls_sw/tools/bin/python2.4

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
#
# Author Alun Morgan


# Values for testing
#RFPMS = ['TS-DI-EBPM-%02d' % (id+1) for id in range(3)]

DEBUG = 'D' in sys.argv

if DEBUG:
    PMDIR = "/tmp/rfpm"
else:
    # Values for operation
    PMDIR = "/dls/ops-data/Postmortems/RF_Postmortems"
    
RFPMS = ['SR-RF-PM-%02d' % (id+1) for id in range(3)]


if __name__ == "__main__":
    from pkg_resources import require as Require
    Require('numpy==1.1.0')
    Require('cothread==1.9')

# Sets the max waveform size for EPICS.  This needs to be set *before* we
# load the cothread library so that CA pays attention to it!
import os, datetime, time
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "3000000"

from cothread import *
from cothread.cothread import Timer
from cothread.catools import *
from numpy import *
from scipy.io import savemat

FNAME = "rf_postmortem"


class Saver:
    def __init__(self, id, pv_list, wf_len):
        self.id = id
        self.pv_list = pv_list
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
        return dirname, filename

            
    def write_result(self, new_value)
        dirname, filename = self.filename(new_value)
        time = new_value.timestamp
        # Convert the results into complex numbers
        result = self.results.reshape(self.pv_count/2, 2, -1)
        result = result[:, 0] + 1j * result[:, 1]
        
        # we've got all the channels
        if os.path.isfile(filename):
            print 'File %s already exists' % filename
        else:
            if not os.path.isdir(dirname):
                print 'Creating', dirname
                os.mkdir(dirname)
            print 'Writing pm', filename
            data = dict(pm = result, time = new_value.timestamp)
            savemat(filename, data, appendmat=True)

    def reset(self):
        self.triggered = False
            
  
# epics channels for RF
pv_lists = [
    (id+1, ['%s:PM:WF%c%c' % (rfpm, button, iq)
        for button in 'ABCD'
        for iq in 'IQ'])
    for id, rfpm in enumerate(RFPMS)]


# save task
if __name__ == "__main__":
    savers = [
        Saver(id, pv_list, 2**14)
        for id, pv_list in pv_lists]
    WaitForQuit()
