#!/dls_sw/tools/bin/python2.4

import sys, os

if __name__ == '__main__':
    from pkg_resources import require
    require('matplotlib == 0.91.1')

os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib
matplotlib.use('Agg')

from pylab import *
from numpy import *
from datetime import datetime
import cStringIO, pickle, elog


def display_waveforms(time, *pms):
    clf()
    # Plotting phase and magnitude plots
    a = axes([0, 0, 1, 0.93], axisbg='grey')
    setp(a, xticks=[], yticks=[])
    
    title(time.strftime('RF postmortem for %d/%m/%Y at %H:%M.%S'))
    ioff()
    
    channels = ['Cavity', 'Forward', 'Reflected']

    # Normalise the plot arrays by dividing by the first entry and select the
    # part we're actually going to plot
    pms = [pm[1:, -2000:] / pm[0, -2000:] for pm in pms]

    timebase = linspace(-1000, 1000, 2000)
    colours = ['blue', 'green', 'cyan']
    for n, channel in enumerate(channels):
        plots = reversed(zip(pms, colours))
        
        axes([0.1, 0.08 + 0.3*n, 0.35, 0.2])
        title('%s Phase' % channel)
        xlabel('Turns')
        ylabel('Degrees')
        for pm, colour in plots:
            plot(timebase, 180/pi * unwrap(angle(pm[n])), colour)
            hold(True)
        axvline(0, color = 'red')
        
        axes([0.6, 0.08 + 0.3*n, 0.35, 0.2])
        title('%s Magnitude' % channel)
        xlabel('Turns')
        ylabel('Signal (a.u.)')
        for pm, colour in plots:
            plot(timebase, abs(pm[n]), colour)
            hold(True)
        axvline(0, color = 'red')
        
    # print png to string buffer
    buf = cStringIO.StringIO()
    gcf().canvas.print_png(buf)
    return buf.getvalue()
    

if __name__ == '__main__':
    file1 = '/dls/ops-data/Postmortems/RF_Postmortems/2010-04/' \
        'rf_postmortem-01-2010-04-14T06:45:08.mat'
    file2 = '/dls/ops-data/Postmortems/RF_Postmortems/2010-04/' \
        'rf_postmortem-02-2010-04-14T06:45:08.mat'
    from scipy.io import loadmat
    from datetime import time
    m1 = loadmat(file1)
    m2 = loadmat(file2)
    buf = display_waveforms(time(), m1['pm'], m2['pm'], ones([4, 2000]))
    
    # post to elog
    elog.entry('RF Postmortem', 'RF Postmortem', buf, True)
