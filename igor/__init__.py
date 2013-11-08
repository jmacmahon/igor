"""Igor - an IRC bot"""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import sys
import select
import os
import yaml

from igor.irc.connection import Connection
from igor.irc.messages import Message
from igor.reactor import Reactor
from igor.plugins.builtins import Builtins

def formatter_class(*args, **kwargs):
    kwargs['max_help_position'] = 32
    return argparse.ArgumentDefaultsHelpFormatter(*args, **kwargs)

parser = argparse.ArgumentParser(formatter_class=formatter_class)
parser.add_argument(
    '-c', '--config', default='igor.yaml', metavar='file',
    help="The configuration file to load")

def main():
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    config['connections'] = [Connection(**c) for c in config['connections']]
    config['plugins'] = [Builtins()]

    Reactor.from_config(**config).go()
