"""Builtin plugin"""

from __future__ import absolute_import, unicode_literals

import igor
import igor.utils

from igor.irc.messages import RPL_WELCOME
from igor.plugins import Plugin, listen, listen_for, command


class Builtins(Plugin):
    def __init__(self):
        self.log = igor.utils.getLogger(self)

    @listen
    def log_messages(self, message):
        self.log.debug(message)

    @listen_for(RPL_WELCOME)
    def welcome(self, message):
        self.log.info(message.trailing)

    @command
    def about(self, message, argv):
        message.reply("https://github.com/borntyping/igor")

    @command
    def version(self, message, argv):
        message.reply("Igor, version {0}".format(igor.__version__))

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
