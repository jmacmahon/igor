"""Utility functions and classes"""

def quick_repr(obj, attributes=None):
    attributes = ["{}={}".format(k, v) for k, v in attributes.items()]
    return obj.__class__.__name__ + '(' + ', '.join(attributes) + ')'
