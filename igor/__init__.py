"""Igor - an IRC bot"""

from __future__ import absolute_import, unicode_literals

import argparse
import logging

from igor.reactor import Igor

LOG_FORMAT = '%(asctime)s %(levelname)-8s [%(name)s] %(message)s'

LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def configure_logging(level='INFO'):
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log = logging.getLogger('igor')
    log.setLevel(LOG_LEVELS.get(level))
    log.addHandler(handler)


def formatter_class(*args, **kwargs):
    kwargs.setdefault('max_help_position', 32)
    kwargs.setdefault('width', 128)
    return argparse.ArgumentDefaultsHelpFormatter(*args, **kwargs)


parser = argparse.ArgumentParser(formatter_class=formatter_class)
parser.add_argument(
    '-c', '--config', default='igor.yaml', metavar='file',
    help="The configuration file to load")
parser.add_argument(
    '-l', '--log-level', metavar='LEVEL',
    default='INFO', choices=LOG_LEVELS.keys(),
    help="One of CRITICAL, ERROR, WARNING, INFO, DEBUG")


def main():
    args = parser.parse_args()
    configure_logging(args.log_level)
    Igor.from_config_file(args.config).go()
