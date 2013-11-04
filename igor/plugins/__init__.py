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

    def __set__(self, function):
        self.function = function

    def __call__(self, instance, message):
        if self.predicate is None or self.predicate(message):
            return self.function(instance, message)

def listener(*args, **kwargs):
    """Returns a decorator function that will create a listener instance"""

    # If the only argument passed is a function, create a Listener
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return Listener(function=args[0])

    # This decorator will create a Listener with the arguments we already have
    def create_listener(function):
        return Listener(function, *args, **kwargs)

    return create_listener

class Plugin(object):
    def __call__(self, message):
        for name, listener in inspect.getmembers(self, self.__is_listener):
            try:
                listener(message)
            except Exception as exception:
                self.__log_exception(exception)        

    def __is_listener(self, object):
        return isinstance(object, BoundListener)

    def __log_exception(self, exception):
        print("Listener {} failed to run".format(name), file=sys.stderr)
        print(traceback.format_exc(exception), file=sys.stderr)

class TestPlugin(Plugin):
    @listener(predicate=lambda message: isinstance(message, MOTD))
    def test_motd(self, message):
        print(message.text)

    @listener
    def test_all(self, message):
        print(message)
