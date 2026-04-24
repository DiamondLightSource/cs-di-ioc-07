import matplotlib

matplotlib.use("Agg")

import io

import matplotlib.pyplot as plt
import numpy as np

from . import config, elog


def display_waveforms(time, *pms):
    valid_colours = [
        colour for n, colour in enumerate(config.COLOURS) if n + 1 in config.VALID_PMS
    ]

    assert len(pms) == len(valid_colours)

    plt.clf()
    plt.gcf().set_facecolor("0.75")  # Sets shade of grey of of top banner
    plt.rcParams["axes.titlepad"] = 3
    plt.rcParams["axes.labelpad"] = 0
    plt.rcParams["lines.linewidth"] = 1.0
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["axes.xmargin"] = 0
    # Plotting phase and magnitude plots
    a = plt.axes((0, 0, 1, 0.93), facecolor="grey")
    plt.setp(a, xticks=[], yticks=[])

    # Normalise the plot arrays by dividing by the first entry and select the
    # part we're actually going to plot
    pms = [pm[1:, -2000:] / pm[0, -2000:] for pm in pms]

    plots = [
        (pm, colour)
        for pm, colour in reversed(list(zip(pms, valid_colours, strict=True)))
        if np.all(~np.isnan(pm))
    ]
    labels = [
        f"{n}: {colour}"
        for n, pm, colour in zip(config.VALID_PMS, pms, valid_colours, strict=True)
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
        plt.locator_params(axis="y", nbins=10)
        plt.axes((0.6, 0.08 + 0.3 * n, 0.35, 0.2))
        plt.title(f"{channel} Magnitude")
        plt.xlabel("Turns")
        plt.ylabel("Signal (a.u.)")
        for pm, colour in plots:
            plt.plot(timebase, abs(pm[n]), colour)
        plt.axvline(0, color="red")
        plt.locator_params(axis="y", nbins=10)

    # print png to string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    return buf.getvalue()


if __name__ == "__main__":
    file1 = (
        "/dls/ops-data/Postmortems/RF_Postmortems/2026-04/"
        "rf_postmortem-01-2026-04-24T13:28:19.mat"
    )
    file2 = (
        "/dls/ops-data/Postmortems/RF_Postmortems/2026-04/"
        "rf_postmortem-03-2026-04-24T13:28:19.mat"
    )
    from datetime import time

    from scipy.io import loadmat

    config.load("CS-DI-IOC-07.config")

    m1 = loadmat(file1)
    m2 = loadmat(file2)
    mm = [m1["pm"], m2["pm"], np.ones([4, 2000])]
    buf = display_waveforms(time(), *[mm[n] for n in range(2)])

    # Write to .png file for review
    if buf:
        with open("buf.png", "wb") as f:
            f.write(buf)

    # post to elog
    elog.entry("RF Postmortem", "RF Postmortem", buf, True)
