"""Core plugin classes"""

from __future__ import absolute_import, print_function, unicode_literals

import functools
import inspect
import re
import sys
import traceback

from igor.irc.messages import Message, Privmsg, MOTD

__all__ = ['Plugin', 'listener', 'command', 'trigger']


class Plugin(object):
    def _is_listener(self, obj):
        """Checks if the object has a receives attribute and is callable"""
        return hasattr(obj, 'receives') and callable(obj)

    def __call__(self, message):
        """Dispatches a message to all methods that say they will receive it"""
        for name, listener in inspect.getmembers(self, self._is_listener):
            try:
                if isinstance(message, listener.receives):
                    listener(message)
            except Exception as exception:
                print("Listener '{}' from plugin '{}' failed to run.".format(
                    name, self.__class__.__name__,
                ), traceback.format_exc(exception), end='', file=sys.stderr)


def listen(function, message_class=Message):
    """Sets function.receives, and in the future other listener metadata"""
    function.receives = message_class
    return function


def listen_for(message_class=Message):
    """Returns a listener that only receives messages of a certain type"""
    def create_listener(function):
        return listen(function, message_class=message_class)
    return create_listener


def command(function):
    """Returns a listener, and checks for the command"""
    @functools.wraps(function)
    def wrapper(self, message):
        # TODO: pass the function the command arguments
        if message.trailing.startswith(':' + function.__name__):
            return function(self, message)
    return listen(wrapper, Privmsg)


def trigger(pattern, flags=0):
    regex = re.compile(pattern, flags)

    def create_trigger(function):
        @functools.wraps(function)
        def wrapper(self, message):
            result = regex.match(message.trailing)
            if result is not None:
                return function(self, message, result)
        return listen(wrapper, Privmsg)
    return create_trigger


class TestPlugin(Plugin):
    @listen
    def test_all(self, message):
        """Receives all messages"""
        print("Message received")

    @command
    def test(self, message):
        """Receives Privmsg messages that start with :test"""
        print("Command")

    @trigger(".*test.*")
    def test_regex(self, message, result):
        """Receives Privmsg messages match a regex"""
        print("Trigger")
