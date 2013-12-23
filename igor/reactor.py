"""The core Reactor class"""

from __future__ import absolute_import, unicode_literals

import select

import yaml

import igor.irc.connection
import igor.plugins.builtins
import igor.utils


class Reactor(object):
    """Manages connections using select() and passes events to callbacks"""

    _timeout = 1000 * 60
    _input_mask = select.POLLPRI | select.POLLIN
    _error_mask = select.POLLERR | select.POLLHUP | select.POLLNVAL

    def __init__(self, connections, callbacks):
        self.log = igor.utils.getLogger(self)
        self.log.info("Igor raises from the grave!")

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
        self.log.info("Connecting to {0}".format(connection))
        try:
            connection.connect()
        except Exception:
            self.log.exception("Failed to connect to {0}".format(connection))
        else:
            self._descriptors[connection.fd] = connection
            self._poll.register(connection.fd, self._input_mask)

    def disconnect(self, connection, exception=None):
        """Unregister a connection and tell it to disconnect"""
        self.log.info("Disconnecting from {0}".format(connection))
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
                    self.log.warn("Disconnecting due to user interrupt")
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
                except igor.irc.connection.Disconnected:
                    self.disconnect(connection)

    def dispatch(self, event):
        for callback in self.callbacks:
            callback(event)


class Igor(Reactor):
    @classmethod
    def from_config_file(cls, filename):
        with open(filename, 'r') as f:
            config = yaml.safe_load(f)
        return cls(config)

    def __init__(self, config):
        self.config = config
        connections = [
            igor.irc.connection.Connection(**c) for c in config['connections']]
        callbacks = [
            igor.plugins.builtins.Builtins()]
        super(Igor, self).__init__(connections, callbacks)
