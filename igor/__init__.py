"""Igor - an IRC bot"""

from __future__ import absolute_import, unicode_literals

import argparse
import logging

import yaml

import igor.irc.connection
import igor.reactor
import igor.manager

__version__ = '1.0.0-alpha'

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
parser.add_argument(
    '-v', '--version', action='version',
    version='Igor v{0}'.format(__version__),
    help="Show this programs version and exit")


def main():
    args = parser.parse_args()

    configure_logging(args.log_level)

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    manager = igor.manager.Manager()
    manager.load_plugins(config.get('plugins', {
        'Builtins': {'module': 'igor.plugins.builtins'}
    }))

    reactor = igor.reactor.Reactor(callback=manager)
    reactor.load_connections(config.get('connections', list()))

    reactor.go()
