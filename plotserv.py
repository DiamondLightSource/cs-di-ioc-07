import sys, os


import matplotlib

matplotlib.use('Agg')

from pylab import *
from numpy import *
import io, elog

from config import *

VALID_COLOURS = [colour for n, colour in enumerate(COLOURS) if n + 1 in VALID_PMS]


def display_waveforms(time, *pms):
    assert len(pms) == len(VALID_COLOURS)

    clf()
    # Plotting phase and magnitude plots
    a = axes([0, 0, 1, 0.93], facecolor='grey')
    setp(a, xticks=[], yticks=[])

    # Normalise the plot arrays by dividing by the first entry and select the
    # part we're actually going to plot
    pms = [pm[1:, -2000:] / pm[0, -2000:] for pm in pms]

    plots = [
        (pm, colour)
        for pm, colour in reversed(list(zip(pms, VALID_COLOURS)))
        if not any(isnan(pm))
    ]
    labels = [
        '%d: %s' % (n, colour)
        for n, pm, colour in zip(VALID_PMS, pms, VALID_COLOURS)
        if not any(isnan(pm))
    ]

    title(
        'RF PM for %s: %s' % (time.strftime('%d/%m/%Y at %H:%M.%S'), ', '.join(labels))
    )
    ioff()

    channels = ['Cavity', 'Forward', 'Reflected']

    timebase = linspace(-1000, 1000, 2000)
    for n, channel in enumerate(channels):
        axes([0.1, 0.08 + 0.3 * n, 0.35, 0.2])
        title('%s Phase' % channel)
        xlabel('Turns')
        ylabel('Degrees')
        for pm, colour in plots:
            plot(timebase, 180 / pi * unwrap(angle(pm[n])), colour)
        axvline(0, color='red')

        axes([0.6, 0.08 + 0.3 * n, 0.35, 0.2])
        title('%s Magnitude' % channel)
        xlabel('Turns')
        ylabel('Signal (a.u.)')
        for pm, colour in plots:
            plot(timebase, abs(pm[n]), colour)
        axvline(0, color='red')

    # print png to string buffer
    buf = io.BytesIO()
    gcf().canvas.print_png(buf)
    return buf.getvalue()


if __name__ == '__main__':
    file1 = (
        '/dls/ops-data/Postmortems/RF_Postmortems/2010-04/'
        'rf_postmortem-01-2010-04-14T06:45:08.mat'
    )
    file2 = (
        '/dls/ops-data/Postmortems/RF_Postmortems/2010-04/'
        'rf_postmortem-02-2010-04-14T06:45:08.mat'
    )
    from scipy.io import loadmat
    from datetime import time

    m1 = loadmat(file1)
    m2 = loadmat(file2)
    mm = [m1['pm'], m2['pm'], ones([4, 2000])]
    buf = display_waveforms(time(), *[mm[n - 1] for n in VALID_PMS])

    # post to elog
    elog.entry('RF Postmortem', 'RF Postmortem', buf, True)
