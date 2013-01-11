# Simple PM configuration.  Everything read from configuration file normally
# found in /home/ops/diagnostics/concentrator/, but read from the local
# directory in debug mode.

import sys
import os

if 'D' in sys.argv:
    CONFIG_DIR = '.'
else:
    CONFIG_DIR = '/home/ops/diagnostics/concentrator'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'CS-DI-IOC-07.config')

config_dir = {}
execfile(CONFIG_FILE, {}, config_dir)

__all__ = config_dir.keys()
globals().update(config_dir)
