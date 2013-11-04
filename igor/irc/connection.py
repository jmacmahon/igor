"""IRC event handler, using sockets"""

from __future__ import absolute_import, unicode_literals

import socket
import sys

from igor.irc.messages import Message
from igor.irc.parser import format_line
from igor.utils import quick_repr

class Disconnected(Exception):
    pass

class Connection(object):
    ENCODING = 'utf-8'
    MESSAGE_CLASS = Message

    if sys.version_info > (3, 0, 0):
        BINARY_TYPE = bytes
        NEWLINE = bytes("\r\n", ENCODING)
    else:
        BINARY_TYPE = str
        NEWLINE = str("\r\n")

    fd = None
    socket = None

    def __init__(self, host, port=None, username=None, password=None):
        self.host = host
        self.port = port or 6667
        self.username = username or 'igor'
        self.password = password
        self.reconnect_count = 0

    def __repr__(self):
        return quick_repr(self, {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
        })

    def connect(self):
        self._buffer = self.BINARY_TYPE()

        self.socket = socket.socket()
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.connect((self.host, self.port))

        self.fd = self.socket.fileno()

        print("Connected to {0}:{1}".format(self.host, self.port))

        self.write('NICK :{username}'.format(username=self.username))
        self.write('USER igor * * :Igor - https://github.com/borntyping/igor')
        self.write('QUIT :Disconnected because this is a test')

    def read(self, recv_size=1024):
        self._buffer += self.socket.recv(recv_size)

        while self.NEWLINE in self._buffer:
            line, self._buffer = self._buffer.split(self.NEWLINE, 1)

            if line.startswith('PING :'):
                self.write('PONG :' + line[6:])
                break

            if line.startswith('ERROR :'):
                raise Disconnected("Server error: " + line[7:])

            event = self.MESSAGE_CLASS.parse(line, connection=self)

            if event is not None:
                yield event

        raise StopIteration

    def _write(self, line):
        """Encode and send a single line"""
        self.socket.send(line.encode(self.ENCODING) + self.NEWLINE)

    def write(self, command, parameters=None, trailing=None):
        """Format an IRC message and send it"""
        self._write(format_line(None, command, parameters, trailing))

    def _try(self, func, *args, **kwargs):
        """Attempt to call a function, but pass on socket errors"""
        try:
            return func(*args, **kwargs)
        except socket.error:
            pass

    def disconnect(self, exception=None, message="Disconnected"):
        if exception and not message:
            message = str(exception)
        
        if self.socket is not None:
            self._try(self.write, "QUIT :" + message)
            self._try(self.socket.shutdown, socket.SHUT_RDWR)
            self._try(self.socket.close)
            del self.socket
