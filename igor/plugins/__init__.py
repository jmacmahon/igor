"""Core plugin classes"""

from __future__ import absolute_import, print_function, unicode_literals

import functools
import inspect
import sys
import traceback

from igor.irc.messages import Message, Privmsg, MOTD

class Plugin(object):
    def _is_listener(self, obj):
        """Checks if the object has a receives attribute and is callable"""
        return hasattr(obj, 'receives') and callable(obj)

    def _call_listener(self, listener, message):
        """Calls a listener, making sure exceptions are handled"""
        if isinstance(message, listener.receives):
            try:
                listener(message)
            except Exception as exception:
                print("Listener {} failed to run".format(name))
                print(traceback.format_exc(exception), file=sys.stderr)

    def _receive_message(self, message):
        """Dispatches a message to all methods that say they will receive it"""
        for name, listener in inspect.getmembers(self, self._is_listener):
            self._call_listener(listener, message)

    def __call__(self, *args, **kwargs):
        self._receive_message(*args, **kwargs)

def listener(function, message_class=Message):
    """Sets function.receives, and in the future other listener metadata"""
    function.receives = message_class
    return function

def command(function):
    """Returns a listener, and checks for the command"""
    @functools.wraps(function)
    def wrapper(self, message):
        if message.trailing.startswith(':' + function.__name__):
            return function(self, message)
    return listener(wrapper, Privmsg)

class TestPlugin(Plugin):
    @listener
    def test_all(self, message):
        """Receives all messages"""
        print(message)

    @command
    def test_command(self, message):
        """Receives Privmsg messages that start with :test_command"""
        print("Command received", message.trailing)
