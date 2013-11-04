"""Igor - an IRC bot"""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import select
import os

from igor.irc.connection import Connection
from igor.reactor import Reactor

class Plugin(object):
    def __call__(self, event):
        print(event)

def main():
    Reactor([Connection("irc.aberwiki.org", 6667)], [Plugin()]).go()
