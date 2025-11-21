import matplotlib

matplotlib.use("Agg")

import io

import matplotlib.pyplot as plt
import numpy as np

from . import elog
from .config import COLOURS, VALID_PMS

VALID_COLOURS = [colour for n, colour in enumerate(COLOURS) if n + 1 in VALID_PMS]


def display_waveforms(time, *pms):
    assert len(pms) == len(VALID_COLOURS)

    plt.clf()
    # Plotting phase and magnitude plots
    a = plt.axes((0, 0, 1, 0.93), facecolor="grey")
    plt.setp(a, xticks=[], yticks=[])

    # Normalise the plot arrays by dividing by the first entry and select the
    # part we're actually going to plot
    pms = [pm[1:, -2000:] / pm[0, -2000:] for pm in pms]

    plots = [
        (pm, colour)
        for pm, colour in reversed(list(zip(pms, VALID_COLOURS, strict=True)))
        if np.all(~np.isnan(pm))
    ]
    labels = [
        f"{n}: {colour}"
        for n, pm, colour in zip(VALID_PMS, pms, VALID_COLOURS, strict=True)
        if np.all(~np.isnan(pm))
    ]

    plt.title(f"RF PM for {time.strftime('%d/%m/%Y at %H:%M.%S')}: {', '.join(labels)}")
    plt.ioff()

    channels = ["Cavity", "Forward", "Reflected"]

    timebase = np.linspace(-1000, 1000, 2000)
    for n, channel in enumerate(channels):
        plt.axes((0.1, 0.08 + 0.3 * n, 0.35, 0.2))
        plt.title(f"{channel} Phase")
        plt.xlabel("Turns")
        plt.ylabel("Degrees")
        for pm, colour in plots:
            plt.plot(timebase, 180 / np.pi * np.unwrap(np.angle(pm[n])), colour)
        plt.axvline(0, color="red")

        plt.axes((0.6, 0.08 + 0.3 * n, 0.35, 0.2))
        plt.title(f"{channel} Magnitude")
        plt.xlabel("Turns")
        plt.ylabel("Signal (a.u.)")
        for pm, colour in plots:
            plt.plot(timebase, abs(pm[n]), colour)
        plt.axvline(0, color="red")

    # print png to string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    return buf.getvalue()


if __name__ == "__main__":
    file1 = (
        "/dls/ops-data/Postmortems/RF_Postmortems/2010-04/"
        "rf_postmortem-01-2010-04-14T06:45:08.mat"
    )
    file2 = (
        "/dls/ops-data/Postmortems/RF_Postmortems/2010-04/"
        "rf_postmortem-02-2010-04-14T06:45:08.mat"
    )
    from datetime import time

    from scipy.io import loadmat

    m1 = loadmat(file1)
    m2 = loadmat(file2)
    mm = [m1["pm"], m2["pm"], np.ones([4, 2000])]
    buf = display_waveforms(time(), *[mm[n - 1] for n in VALID_PMS])

    # post to elog
    elog.entry("RF Postmortem", "RF Postmortem", buf, True)
