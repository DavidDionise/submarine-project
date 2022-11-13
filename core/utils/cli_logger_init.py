import logging
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--log-to-file", action="store_true")
parser.add_argument("--log-level", default="WARN",
                    choices=["ERROR", "WARN", "WARNING", "INFO", "DEBUG"])
args = parser.parse_args()

levels = [
    logging.ERROR,
    logging.WARN,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG
]

logger_level = next(
    level for level in levels if logging.getLevelName(level) == args.log_level)

if args.log_to_file:
    logging.basicConfig(
        filename="logs.dat",
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        level=logger_level
    )
else:
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        level=logger_level
    )
