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

    @staticmethod
    def __arguments(message):
        """Gets the arguments that follow a command"""
        # TODO: Remove this and improve @command
        if not ' ' in message.trailing: return None
        return message.trailing.split(' ', 1)[1]

    @command
    def say(self, message):
        message.reply(self.__arguments(message))

    @command
    def quit(self, message):
        message.connection.quit(self.__arguments(message))
