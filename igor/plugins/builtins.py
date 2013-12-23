"""Builtin plugin"""

from __future__ import absolute_import, unicode_literals

from igor.irc.messages import RPL_WELCOME
from igor.plugins import Plugin, listen, listen_for, command


class Builtins(Plugin):
    @listen
    def log_messages(self, message):
        self.log.debug(message)

    @listen_for(RPL_WELCOME)
    def welcome(self, message):
        self.log.info("Connected to {0}".format(message.connection))

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
