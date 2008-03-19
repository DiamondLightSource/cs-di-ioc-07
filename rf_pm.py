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


if __name__ == "__main__":
    from pkg_resources import require as Require
    Require('cothread==1.5')

# Sets the max waveform size for EPICS.  This needs to be set *before* we
# load the cothread library so that CA pays attention to it!
import os, datetime, time
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "3000000"

from cothread import *
from cothread.catools import *
from numpy import *
from scipy.io import savemat

PMDIR = "/home/ops/rf/RF-libera/RF_Postmortems"
FNAME = "rf_postmortem"



class Saver:

    # object constructor
    def __init__(self, id, pv_list, wf_len):
        self.id = id
        self.pv_list = pv_list
        self.pv_count = len(pv_list)
        self.results = zeros((self.pv_count, wf_len), dtype = float)
        # lookup index name from channel name
        self.stamps = zeros(self.pv_count)
        self.seen = zeros(self.pv_count, dtype = bool)
        #connect pvs
        camonitor(self.pv_list, self.update_array_entry, format = FORMAT_TIME)
            
    def update_array_entry(self, new_value, index):
        # Record the incoming data.
        self.results[index] = new_value
        self.stamps[index] = new_value.timestamp
        self.seen[index] = True
              
        if self.seen.all():
            # If we've seen them all then check that they've all got the same
            # timestamp.
            if (self.stamps == self.stamps[0]).all():
                # Compute the filename as the timestamp in UTC format in
                # seconds.
                self.write_result(
                    new_value.timestamp, self.filename(new_value))
            else:
                # If the timestamps don't match keep on watching until they
                # do.
                print 'Timestamps don\'t match'


    def filename(self, new_value):
        # Computes the filename from the timestamp.
        datestring = new_value.datetime.replace(microsecond = 0).isoformat()
        return os.path.join(PMDIR,
            '%s-%02d-%s.mat' % (FNAME, self.id, datestring))

            
    def write_result(self, time, filename):
        # Convert the results into complex numbers
        result = self.results.reshape(self.pv_count/2, 2, -1)
        result = result[:, 0] + 1j * result[:, 1]
        
        # we've got all the channels
        if os.path.isfile(filename):
            print 'File %s already exists' % filename
        else:
            print 'Writing pm', filename
            savemat(filename, {'pm': result, 'time': time} , appendmat=True)
        
        Sleep(5)
        self.results[:] = 0
        self.seen[:] = False
            
  
# epics channels for RF
pv_lists = [
    (id, ['SR-RF-PM-%02d:PM:WF%c%c' % (id, button, iq)
        for button in 'ABCD'
        for iq in 'IQ'])
    for id in [1, 2, 3]]


# save task
if __name__ == "__main__":
    savers = [
        Saver(id, pv_list, 2**14)
        for id, pv_list in pv_lists]
    WaitForQuit()
