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

if __name__ == "__main__":
    from pkg_resources import require as Require
    Require('cothread')

from cothread import *
from cothread.catools import *
from numpy import *
from scipy.io import savemat

# sets the max waveform size for EPICS
import os, datetime, time
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "3000000"

PMDIR = "/tmp"
FNAME = "rf_postmortem_"
#FNAME = "bpm_postmortem_"

class saver:

    # object constructor
    def __init__(self, pv_list):
        self.pv_list = pv_list
        self.pv_count = len(pv_list)
        self.full_n = []
        self.results = zeros(self.pv_count, dtype = float)
        # lookup index name from channel name
        self.stamps = ['T' for sb in range(self.pv_count)]
        #connect pvs
        camonitor(self.pv_list, self.update_array_entry, format = FORMAT_TIME)
            
    def update_array_entry(self, new_value, index):

        self.results[index] = new_value
       
        # real timestamp from channel
        dn = str(new_value.timestamp)
        # time stamp accurate to 10us
        stamp = dn[0:10]+ 'T' + dn[11:13] + dn[14:16] + \
            dn[17:19] + '_' + dn[20:22]
        self.stamps[index] = stamp
        
              
        # got one more sample
        self.full_n.append(index)
        #print self.full_n
        counter = 0
        for i in range(self.pv_count):
            if self.full_n.count(i) > 0:
                counter += 1         


        # update the trigger reference value from the latest updated channel
        stamps_ref = [stamp]
        for b in range(self.pv_count -1):
            stamps_ref.append(stamps_ref[0])

 
      #  print stamps_ref
      #  print self.stamps
 
        if counter == self.pv_count :
            if self.stamps == stamps_ref:
                print 'Timestamps match'
            else:
                counter = 0
                print 'Timestamps DONT match'
              
        if counter == self.pv_count :
            # we've got all the channels
            fname = os.path.join(PMDIR, FNAME + stamp)
            print fname
            savemat(fname, {'pm': self.results} , appendmat=True)
            Sleep(5)
            self.full_n = []
            self.results[:] = 0
            self.stamps = ['T' for sb in range(self.pv_count)]
            
  
# epics channels for BPMS
pv_list = [
    'SR%02dC-DI-EBPM-%02d:SA:X' % (cell+1, n+1)
    for cell in range(1)
    for n in range(7)]
    
    # epics channels for RF
letters = ["A", "B", "C", "D"]
RI = ["I", "Q"]
pv_list = [
    'SR-RF-PM-%02d:PM:WF%c%c' % (p+1, letters[n], RI[m])
    for p in range(1)
    for n in range(1)
    for m in range(1)]
print pv_list

           # save task
if __name__ == "__main__":
    s = saver(pv_list)
    WaitForQuit()
