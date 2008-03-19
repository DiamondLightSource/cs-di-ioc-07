#!/usr/bin/env python2.4

# This is the frontend for the RF postmortem. It displays magnitude and phase infromation for channels 2-4. It uses channel 1 as the reference signal (i.e. the RF)

from pkg_resources import require
require('cothread==1.5')
require('matplotlib==0.91.1')

from cothread import *
iqt()

from pylab import *
from numpy import *
from qt import *
from scipy.io import loadmat
import sys
from datetime import datetime

#print 'args:', sys.argv

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    # No filename specified, so prompt for filename!
    import tkFileDialog
    filename = tkFileDialog.askopenfilename(
        initialdir = '/home/ops/rf/RF-libera/RF_Postmortems',
        filetypes = ['mat *.mat'])
    if not filename:
        sys.exit(1)

m = loadmat(filename)

# splitting out the data and the timestamp
utctime = m['time']
pm = m['pm']
# Channel 0 is RF reference so all other channels are relative to this.
pmN = pm / pm[0]
# Plotting phase and magnitude plots
a = axes([0,0,1,0.93],axisbg='grey')
setp(a,xticks=[],yticks=[])
time = datetime.fromtimestamp(utctime)   
disptime = ['RF postmortem for ',str(time.day),'/',str(time.month),'/',str(time.year),' at ',str(time.hour),':',str(time.minute),'.',str(time.second)]
disptime = ''.join(disptime)
title(disptime)
ioff()
#setp(a, xticks=[],yticks=[])
for n in range(1,4):
  #  subplot(3,2,n+(n-1))
    axes([0.1,0.08+(n-1)*0.3,0.35,0.2])
    title('Phase')
    xlabel('Turns')
    ylabel('Degrees')
    plot(linspace(-1000,1000,2000),180/pi * unwrap(angle(pmN.T[-2000:, n])))
    axvline(0)  
  #  subplot(3,2,2*n)
    axes([0.6,0.08+(n-1)*0.3,0.35,0.2])
    title('Magnitude')
    xlabel('Turns')
    ylabel('Signal (a.u.)')
    plot(linspace(-1000,1000,2000),pmN.T[-2000:, n])
    axvline(0)
draw()
show()

WaitForQuit()
