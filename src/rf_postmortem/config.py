# Simple PM configuration.  Everything read from configuration file normally
# found in /home/ops/diagnostics/concentrator/, but read from the local
# directory in debug mode.

import os
import sys

if "-D" in sys.argv:
    CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
else:
    CONFIG_DIR = "/home/ops/diagnostics/concentrator"
CONFIG_FILE = os.path.join(CONFIG_DIR, "CS-DI-IOC-07.config")

config_dir = {}
exec(open(CONFIG_FILE).read(), {}, config_dir)

__all__ = list(config_dir.keys())
globals().update(config_dir)
