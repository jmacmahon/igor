"""Utility functions and classes"""

import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# This logger is used to ensure igor's log messages are handled
logging.getLogger('igor').addHandler(NullHandler())


def fullname(obj):
    """Returns the qualified name of an object's class"""
    name = obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__
    return '.'.join([obj.__module__, name])


def getLogger(obj):
    """Returns a logger using the full name of the given object"""
    return logging.getLogger(fullname(obj))


def quick_repr(obj, attributes=None):
    attributes = ["{}={}".format(k, v) for k, v in attributes.items()]
    return fullname(obj) + '(' + ', '.join(attributes) + ')'


class lazy(object):
    """Decorates a function, turning it into a lazily-accessed property"""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        setattr(instance, self.func.__name__, self.func(instance))
        return getattr(instance, self.func.__name__)
