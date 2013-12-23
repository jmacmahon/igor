"""Builtin plugin"""

from __future__ import absolute_import, print_function, unicode_literals

from igor.irc.messages import RPL_WELCOME
from igor.plugins import Plugin, listen, listen_for, command


class Builtins(Plugin):
    @listen
    def print_messages(self, message):
        print(message)

    @listen_for(RPL_WELCOME)
    def welcome(self, message):
        print("Connected to {c.host}:{c.port}".format(c=message.connection))

    @command
    def say(self, message, argv):
        message.reply(' '.join(argv))

    @command
    def join(self, message, argv):
        message.connection.join(*argv)

    @command
    def part(self, message, argv):
        message.connection.part(*argv)

    @command
    def quit(self, message, argv):
        message.connection.quit(' '.join(argv))
