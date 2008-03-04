#!/usr/bin/env python2.4

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

DEBUG = True

if __name__ == "__main__":
    if DEBUG:
        import sys
        sys.path.append('/home/mga83/epics/cothread/build/lib.linux-i686-2.4')
    else:
        from pkg_resources import require as Require
        Require('cothread')

# Sets the max waveform size for EPICS.  This needs to be set *before* we
# load the cothread library so that CA pays attention to it!
import os, datetime, time
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "3000000"

from cothread import *
from cothread.catools import *
from numpy import *
from scipy.io import savemat

PMDIR = "/tmp"
FNAME = "rf_postmortem_"
#FNAME = "bpm_postmortem_"

class saver:

    # object constructor
    def __init__(self, pv_list, wf_len):
        self.pv_list = pv_list
        self.pv_count = len(pv_list)
        self.full_n = []
        self.results = zeros((self.pv_count, wf_len), dtype = float)
        # lookup index name from channel name
        self.stamps = zeros(self.pv_count)
        self.seen = zeros(self.pv_count, dtype = bool)
        #connect pvs
        print 'saver', self.pv_list
        camonitor(self.pv_list, self.update_array_entry, format = FORMAT_TIME)
            
    def update_array_entry(self, new_value, index):
        if self.seen[index]:
            print 'Hmm: already seen this?'
        
        self.results[index] = new_value
        # Record the incoming data.
        stamp = new_value.timestamp
        self.stamps[index] = stamp
        self.seen[index] = True
              
        # got one more sample
        self.full_n.append(index)
        #print self.full_n
        counter = 0
        for i in range(self.pv_count):
            if self.full_n.count(i) > 0:
                counter += 1         

        if self.seen.all():
            print 'comparing:'
            print self.stamps
            if (self.stamps == self.stamps[0]).all():
                print 'Timestamps match'
            else:
                counter = 0
                print 'Timestamps DONT match'
                print self.stamps
                print stamps_ref
                
              
        if counter == self.pv_count:
            # Compute the filename as the timestamp in UTC format in seconds.
            filename = new_value.datetime.replace(microsecond = 0).isoformat()
            self.write_result(new_value.timestamp, filename)

            
    def write_result(self, time, filename):
        # Convert the results into complex numbers
        result = self.results.reshape(self.pv_count/2, 2, -1)
        result = result[:, 0] + 1j * result[:, 1]
        
        # we've got all the channels
        fname = os.path.join(PMDIR, FNAME + filename)
        print fname
        savemat(fname, {'pm': result, 'time': time} , appendmat=True)
        
        Sleep(5)
        self.full_n = []
        self.results[:] = 0
        self.seen[:] = False
#        self.stamps = ['T' for sb in range(self.pv_count)]
            
  
# epics channels for RF
pv_list = [
    'SR-RF-PM-%02d:PM:WF%c%c' % (p+1, button, iq)
    for p in range(1)
    for button in 'ABCD'
    for iq in 'IQ']
print pv_list

           # save task
if __name__ == "__main__":
    s = saver(pv_list, 2**14)
    WaitForQuit()
