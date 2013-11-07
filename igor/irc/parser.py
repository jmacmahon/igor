"""Pure-python IRC message parser"""

from __future__ import absolute_import, unicode_literals

import re


def parse_prefix(prefix):
    """Parse an IRC hostmask into a tuple"""
    return tuple(re.split('[!@]', prefix))


def parse_line(line):
    """Parse an IRC message and return a tuple of it's components"""
    get_token = lambda s: s.split(' ', 1) if ' ' in s else (s, None)

    source, parameters, trailing = None, list(), None

    if line.startswith(':'):
        source, line = get_token(line[1:])
        source = parse_prefix(source)

    command, line = get_token(line)

    while line:
        if not line.startswith(':'):
            param, line = get_token(line)
            parameters.append(param)
        else:
            trailing = line[1:].strip()
            break

    return source, command, parameters, trailing


def format_prefix(nick, user=None, host=None):
    """Format an IRC prefix (i.e. hostmask) from its components"""
    prefix = nick
    if user:
        prefix += '!' + user
    if host:
        prefix += '@' + host
    return prefix


def format_line(source, command, parameters, trailing):
    """Format an IRC message from its components"""
    message = command
    if source:
        message = ':' + format_prefix(*source) + ' ' + message
    if parameters:
        message += ' ' + (' '.join(parameters))
    if trailing:
        message += ' :' + trailing
    return message
