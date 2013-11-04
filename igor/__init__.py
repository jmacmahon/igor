"""Igor - an IRC bot"""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import select
import os

from igor.irc.connection import Connection
from igor.irc.messages import Message
from igor.reactor import Reactor
from igor.plugins import TestPlugin

def test():
    plugin = TestPlugin()
    plugin(Message.parse(":npc!npc@borntyping.co.uk PRIVMSG #69 ::test some arguments"))

def main():
    Reactor([Connection("irc.aberwiki.org", 6667)], [TestPlugin()]).go()
