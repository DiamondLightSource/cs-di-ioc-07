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
from rf_pm_file_select import *

path_to_files = '/dls/ops-data/Postmortems/RF_Postmortems/'

# if given an argument (whatever) will use file_list to find out the required filenames otherwise it will ask for a file through the browser.
print len(sys.argv)
if len(sys.argv) == 7:
    filenames = file_list(sys.argv[1],path_to_files,sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    print filenames
elif len(sys.argv) == 2:
    # takes the n newest files
    filenames = file_list(sys.argv[1],path_to_files,'*','*','*','*','*')
    print filenames
else:
    filenames = []
    # No filename specified, so prompt for filename!
    import tkFileDialog
    filename = tkFileDialog.askopenfilename(
        initialdir = path_to_files,
        filetypes = ['mat *.mat'])
    if not filename:
        sys.exit(1)
    else:
        filenames.append(filename)
    print filenames    
        
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
    
pmN.reverse()
cavity.reverse()
utctime.reverse()
    
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

title_time = datetime.fromtimestamp(utctime[0])  
disptime = ['RF postmortem for ',str(title_time.day),'/',str(title_time.month),'/',str  (title_time.year),' at ',str(title_time.hour),':',str(title_time.minute)]
disptime = ''.join(disptime)

# case for one dataset
if len(utctime) == 1:
    disp = disptime + ' (cavity ' + str(cavity[0]) + ')'
# for multiple data sets with the same timestamp to the nearest second (i.e. the same incident for all cavities)
elif len(utctime) > 1 and same_ts=='True':
    disp = disptime + '\nBlue is cavity ' + str(cavity[0]) + ' Green is cavity ' + str(cavity[1])
elif len(utctime) > 1 and same_cavity=='True':
    colour_list = ['blue','green','red','cyan','magenta','yellow','black','white']
    disp_temp = ['RF postmortems for cavity ', str(cavity[0]), '\n']
    for f in range(len(utctime)):
        date_temp = datetime.fromtimestamp(utctime[f])
        disp_temp.extend([colour_list[f], ' is ',str(date_temp.day),'/',str(date_temp.month),'/',str(date_temp.year),' at ',str(date_temp.hour),':',str(date_temp.minute),'   '])
    disp = ''.join(disp_temp)
    # need to add legend somewhere
else:
     disp = 'Neather timestamps or cavities match!'

title(disp)    
ioff()
head1 = ['Cavity Phase', 'Forward Phase','Reflected Phase']
head2 = ['Cavity Magnitude', 'Forward Magnitude','Reflected Magnitude']
x_axis = linspace(-1000,1000,2000)
for n in range(1,4):
    axes([0.1,0.08+(n-1)*0.3,0.35,0.2])
    title(head1[n-1])
    xlabel('Turns')
    ylabel('Degrees')
    for h in range(len(utctime)):
        plot(x_axis,180/pi * unwrap(angle(pmN[h].T[-2000:, n])))
        grid(color='grey', linestyle=':', linewidth=1, alpha=0.5)
        hold
    hold
    axvline(0)  
    axes([0.6,0.08+(n-1)*0.3,0.35,0.2])
    title(head2[n-1])
    xlabel('Turns')
    ylabel('Signal (a.u.)')
    for h in range(len(utctime)):
        plot(x_axis,abs(pmN[h].T[-2000:, n]))
        grid(color='grey', linestyle=':', linewidth=1, alpha=0.5)
        hold
    hold
    axvline(0)
draw()
show()

WaitForQuit()
