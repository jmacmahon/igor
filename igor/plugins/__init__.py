"""Core plugin classes"""

from __future__ import absolute_import, print_function, unicode_literals

import functools
import inspect
import sys
import traceback

from igor.irc.messages import Message, Privmsg, MOTD

class BoundListener(object):
    """Binds a Listener instance to a Plugin instance"""

    def __init__(self, listener, instance):
        self.listener = listener
        self.instance = instance

    def __call__(self, *args, **kwargs):
        return self.listener(self.instance, *args, **kwargs)

class Listener(object):
    """Wraps a function, filtering messages with a predicate"""

    def __init__(self, function, predicate=None):
        self.function = function
        self.predicate = predicate

    def __get__(self, instance, owner):
        return BoundListener(self, instance)

    def __call__(self, instance, message):
        if self.predicate is None or self.predicate(message):
            return self.function(instance, message)

class Command(Listener):
    COMMAND_CHARACTER = ':'

    def __init__(self, function, command):
        self.function = function
        self.command = command

    def __call__(self, instance, message):
        if isinstance(message, Privmsg) and message.trailing.startswith(self._prefix):
            return self.function(instance, message, self._arguments(message))

    @property
    def _prefix(self):
        return self.COMMAND_CHARACTER + self.command

    def _arguments(self, message):
        arguments = message.trailing.split(' ', 1)
        return arguments[1] if arguments[1] else ''

class ListenerDecorator(object):
    def __init__(self, listener_class, ):
        self.listener_class = listener_class

    def __call__(self, *args, **kwargs):
        """Returns a decorator function that will create a listener instance"""

        # If the only argument passed is a function, create a Listener
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return self.listener_class(function=args[0])

        # This decorator will create a Listener with the arguments we already have
        def create_listener(function):
            return self.listener_class(function, *args, **kwargs)

        return create_listener

listener = ListenerDecorator(Listener)
command = ListenerDecorator(Command)

class Plugin(object):
    def __call__(self, message):
        for name, listener in inspect.getmembers(self, self.__is_listener):
            try:
                listener(message)
            except Exception as exception:
                print("Listener {} failed to run".format(name))
                self.__log_exception(exception)        

    def __is_listener(self, object):
        return isinstance(object, BoundListener)

    def __log_exception(self, exception):
        print(traceback.format_exc(exception), file=sys.stderr)

class TestPlugin(Plugin):
    @listener(predicate=lambda message: isinstance(message, MOTD))
    def test_motd(self, message):
        print(message.text)

    @listener
    def test_all(self, message):
        print(message)

    @command("test")
    def test_command(self, message, arguments):
        print("Called command test with", repr(arguments))
