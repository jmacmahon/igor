"""Builtin plugin"""

from __future__ import absolute_import, print_function, unicode_literals

from igor.irc.messages import Privmsg, RPL_WELCOME
from igor.plugins import Plugin, listen, listen_for, command, trigger

class Builtins(Plugin):
    @listen
    def print_messages(self, message):
        print(message)

    @listen_for(RPL_WELCOME)
    def welcome(self, message):
        print("Connected to {c.host}:{c.port}".format(c=message.connection))

    @command
    def say(self, message):
        message.reply(message.trailing.split(' ', 1)[1])
