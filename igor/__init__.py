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

parser = argparse.ArgumentParser()
parser.add_argument(
    '--config', default='igor.yaml', metavar='file',
    help="The configuration file to load")

def main():
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    config['connections'] = [Connection(**c) for c in config['connections']]
    config['plugins'] = [Builtins()]

    Reactor.from_config(**config).go()
