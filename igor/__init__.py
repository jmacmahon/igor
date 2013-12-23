"""Igor - an IRC bot"""

from __future__ import absolute_import, print_function, unicode_literals

import argparse

from igor.reactor import Igor


def formatter_class(*args, **kwargs):
    kwargs.setdefault('max_help_position', 32)
    kwargs.setdefault('width', 128)
    return argparse.ArgumentDefaultsHelpFormatter(*args, **kwargs)


parser = argparse.ArgumentParser(formatter_class=formatter_class)
parser.add_argument(
    '-c', '--config', default='igor.yaml', metavar='file',
    help="The configuration file to load")


def main():
    args = parser.parse_args()
    Igor.from_config_file(args.config).go()
