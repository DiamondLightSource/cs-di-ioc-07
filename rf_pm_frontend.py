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

print 'args:', sys.argv
filenames = []

if len(sys.argv) > 1:
    for h in range(1,len(sys.argv)):
        filenames.append(sys.argv[h])
else:
    # No filename specified, so prompt for filename!
    import tkFileDialog
    filename = tkFileDialog.askopenfilename(
        initialdir = '/home/ops/rf/RF-libera/RF_Postmortems',
        filetypes = ['mat *.mat'])
    if not filename:
        sys.exit(1)
    else:
        filenames.append(filename)

utctime = []
pmN = []
cavity = []
for filename in filenames:
    m = loadmat(filename)
    # splitting out the data and the timestamp
    utctime.append(m['time'])
    cavity.append(filename[53])
    pm = (m['pm'])
    # Channel 0 is RF reference so all other channels are relative to this.
    pm = pm / pm[0]
    pmN.append(pm)

# Plotting phase and magnitude plots

# generating the title display
a = axes([0,0,1,0.93],axisbg='grey')
setp(a,xticks=[],yticks=[])

same_ts = 'True'
same_cavity = 'True'
for d in range(len(utctime)):
    if int(utctime[d])!=int(utctime[0]):
        same_ts = 'False'
        
    if cavity[d]!=cavity[0]:
        same_cavity = 'False'


# case for one dataset
if len(utctime) == 1:
    time = datetime.fromtimestamp(utctime[0])   
    disptime = ['RF postmortem for ',str(time.day),'/',str(time.month),'/',str  (time.year),' at ',str(time.hour),':',str(time.minute),'.',str(time.second),' (cavity ',cavity[0],')']
    disp = ''.join(disptime)
# for multiple data sets with the same timestamp to the nearest second (i.e. the same incedent for all cavities)
elif len(utctime) > 1 and same_ts=='True':
    time = datetime.fromtimestamp(utctime[0])   
    disptime = ['RF postmortem for ',str(time.day),'/',str(time.month),'/',str  (time.year),' at ',str(time.hour),':',str(time.minute),'.',str(time.second)]
    disptime = ''.join(disptime)
    disp = disptime + '\nBlue is cavity ' + str(cavity[0]) + ' Green is cavity ' + str(cavity[1])
elif len(utctime) > 1 and same_cavity=='True':
    disp_temp = ['RF postmortems for cavity ', str(cavity[0])]
    disp = ''.join(disp_temp)
    # need to add legend somewhere
else:
     disp = 'Neather timestamps or cavities match!'

title(disp)    
ioff()

x_axis = linspace(-1000,1000,2000)
for n in range(1,4):
    axes([0.1,0.08+(n-1)*0.3,0.35,0.2])
    title('Phase')
    xlabel('Turns')
    ylabel('Degrees')
    for h in range(len(utctime)):
        plot(x_axis,180/pi * unwrap(angle(pmN[h].T[-2000:, n])))
        hold
    hold
    axvline(0)  
    axes([0.6,0.08+(n-1)*0.3,0.35,0.2])
    title('Magnitude')
    xlabel('Turns')
    ylabel('Signal (a.u.)')
    for h in range(len(utctime)):
        plot(x_axis,pmN[h].T[-2000:, n])
        hold
    hold
    axvline(0)
draw()
show()

WaitForQuit()
