"""Core plugin classes"""

from __future__ import absolute_import, print_function, unicode_literals

import functools
import inspect
import re
import shlex

import igor.irc.messages
import igor.utils

__all__ = ['Plugin', 'listener', 'command', 'trigger']


class Plugin(object):
    @igor.utils.lazy
    def log(self):
        return igor.utils.getLogger(self)

    def _is_listener(self, obj):
        """Checks if the object has a receives attribute and is callable"""
        return hasattr(obj, 'receives') and callable(obj)

    def __call__(self, message):
        """Dispatches a message to all methods that say they will receive it"""
        for name, listener in inspect.getmembers(self, self._is_listener):
            try:
                if isinstance(message, listener.receives):
                    listener(message)
            except Exception:
                self.log.exception(
                    "Listener {0} raised an exception".format(name))


def listen(function, message_class=igor.irc.messages.Message):
    """Sets function.receives, and in the future other listener metadata"""
    function.receives = message_class
    return function


def listen_for(message_class):
    """Returns a listener that only receives messages of a certain type"""
    def create_listener(function):
        return listen(function, message_class)
    return create_listener


def command(function, message_class=igor.irc.messages.Privmsg):
    """
    Returns a listener which checks if messages start with a command

    Command functions should have the signature `(self, message, *argv)`
    """
    @functools.wraps(function)
    def wrapper(self, message):
        if message.trailing.startswith(':' + function.__name__):
            argv = shlex.split(message.trailing)[1:]
            return function(self, message, argv)
    return listen(wrapper, message_class)


def trigger(pattern, flags=0, message_class=igor.irc.messages.Privmsg):
    regex = re.compile(pattern, flags)

    def create_trigger(function):
        @functools.wraps(function)
        def wrapper(self, message):
            result = regex.match(message.trailing)
            if result is not None:
                return function(self, message, result)
        return listen(wrapper, message_class)
    return create_trigger


class TestPlugin(Plugin):
    @listen
    def test_all(self, message):
        """Receives all messages"""
        self.log.info("Message received by TestPlugin")

    @command
    def test(self, message):
        """Receives Privmsg messages that start with :test"""
        self.log.info("Command received by TestPlugin")

    @trigger(".*test.*")
    def test_regex(self, message, result):
        """Receives Privmsg messages match a regex"""
        self.log.info("Trigger received by TestPlugin")
