#!/usr/bin/env python2.4

# This is the frontend for the RF postmortem. It displays magnitude and phase infromation for channels 2-4. It uses channel 1 as the reference signal (i.e. the RF)

from pkg_resources import require
require('cothread')
require('matplotlib')

from cothread import *
iqt()

from pylab import *
from numpy import *
from qt import *
from scipy.io import loadmat
import sys

print 'args:', sys.argv

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    # No filename specified, so prompt for filename!
    import tkFileDialog
    filename = tkFileDialog.askopenfilename(
        initialdir = '/tmp',
        filetypes = ['mat *.mat'])
    if not filename:
        sys.exit(1)

m = loadmat(filename)

# splitting out the data and the timestamp
time = m['time']
pm = m['pm']
# Channel 0 is RF reference so all other channels are relative to this.
pmN = pm / pm[0]
# Plotting phase and magnitude plots
for n in range(1,4):
    subplot(3,2,n+(n-1))
    plot(180/pi * unwrap(angle(pmN.T[-2000:, n])))
    subplot(3,2,2*n)
    plot(pmN.T[-2000:, n])

WaitForQuit()
