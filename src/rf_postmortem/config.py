# Simple PM configuration.  Everything read from configuration file normally
# found in /home/ops/diagnostics/config/, but read from the local
# directory in debug mode.

import os
import sys

if "-d" in sys.argv:
    CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
else:
    CONFIG_DIR = "/home/ops/diagnostics/config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "CS-DI-IOC-07.config")


def load(path: str = CONFIG_FILE) -> None:
    config_dir = {}
    exec(open(path).read(), {}, config_dir)
    globals().update(config_dir)
    global __all__
    __all__ = list(config_dir.keys())
