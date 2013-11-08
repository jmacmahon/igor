"""The core Reactor class"""

from __future__ import absolute_import, unicode_literals
from __future__ import print_function

import select
import traceback

from igor.irc.connection import Disconnected


class Reactor(object):
    """Manages connections using select() and passes events to callbacks"""

    _timeout = 1000 * 60
    _input_mask = select.POLLPRI | select.POLLIN
    _error_mask = select.POLLERR | select.POLLHUP | select.POLLNVAL

    @classmethod
    def from_config(cls, connections, plugins):
        return cls(connections, callbacks=plugins)

    def __init__(self, connections, callbacks):
        self.connections = connections
        self.callbacks = callbacks

        self._poll = select.poll()
        self._descriptors = dict()

    def __enter__(self):
        """Connect to each connection"""
        for connection in self.connections:
            self.connect(connection)

    def __exit__(self, *error):
        """Disconnect from each connection"""
        for connection in list(self._descriptors.values()):
            self.disconnect(connection)

    def connect(self, connection):
        try:
            connection.connect()
        except Exception as exception:
            print("Connection {connection} failed to connect:\n "
                  "{message}".format(connection=connection, message=exception))
            print(traceback.format_exc(exception), end='')
        else:
            self._descriptors[connection.fd] = connection
            self._poll.register(connection.fd, self._input_mask)

    def disconnect(self, connection, exception=None):
        """Unregister a connection and tell it to disconnect"""
        self._poll.unregister(connection.fd)
        self._descriptors.pop(connection.fd)
        connection.disconnect(exception)

    def go(self):
        """Start the context manager, loop until there a no connections left
           and handle user interrupts"""
        with self:
            while self._descriptors:
                try:
                    self.tick()
                except KeyboardInterrupt:
                    print("\nShutting down...")
                    break
        return self

    def tick(self):
        """Poll for events and read events from the event connection"""
        for fd, event in self._poll.poll(self._timeout):
            connection = self._descriptors[fd]
            if event & self._error_mask:
                self.disconnect(connection)
            elif event & self._input_mask:
                try:
                    for event in connection.read():
                        self.dispatch(event)
                except Disconnected:
                    self.disconnect(connection)

    def dispatch(self, event):
        for callback in self.callbacks:
            callback(event)
