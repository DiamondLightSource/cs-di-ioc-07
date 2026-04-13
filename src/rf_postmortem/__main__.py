"""Interface for ``python -m rf_postmortem``."""

import os
from argparse import ArgumentParser
from collections.abc import Sequence

from . import __version__, config
from .rf_pm import start_server

__all__ = ["main"]


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    parser = ArgumentParser()
    # Accept "-d" flag (ignored by the app)
    parser.add_argument(
        "-d", dest="debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "-c",
        "--config",
        default=config.CONFIG_FILE,
        help="Path to config file",
    )
    parsed_args = parser.parse_args(args)

    if parsed_args.debug:
        os.environ["EPICS_CAS_SERVER_PORT"] = "6064"
    config.load(parsed_args.config)

    start_server()


if __name__ == "__main__":
    main()
