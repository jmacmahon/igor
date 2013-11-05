"""Igor - an IRC bot"""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import select
import os

from igor.irc.connection import Connection
from igor.irc.messages import Message
from igor.reactor import Reactor
from igor.plugins.builtins import Builtins

def main():
    Reactor([Connection("irc.aberwiki.org", 6667)], [Builtins()]).go()

def test():
    plugin = Builtins()
    line = ":npc!npc@borntyping.co.uk PRIVMSG #69 ::say some arguments"
    plugin(Message.parse(line, connection=Connection("irc.aberwiki.org", 6667)))
