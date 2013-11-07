"""IRC message class hierarchy"""

from __future__ import absolute_import, unicode_literals

from igor.irc.parser import parse_line, format_line


class Message(object):
    classes = dict()

    @classmethod
    def register(cls, obj):
        cls.classes[obj.__name__.lower()] = obj
        return obj

    @classmethod
    def register_numeric(cls, code):
        def decorator(obj):
            cls.classes[str(code).zfill(3)] = obj
            return obj
        return decorator

    @classmethod
    def parse(cls, line, connection=None):
        source, command, parameters, trailing = parse_line(line)

        if command.lower() in cls.classes:
            cls = cls.classes[command.lower()]

        return cls(
            connection=connection,
            source=source,
            command=command,
            parameters=parameters,
            trailing=trailing)

    def __init__(self, connection, source, command, parameters, trailing):
        self.connection = connection
        self.source = source
        self.command = command
        self.parameters = parameters
        self.trailing = trailing

        # Subclasses can define a function that is used to perform
        # extra setup with the existing attributes
        if hasattr(self, 'init') and callable(self.init):
            self.init()

    def __repr__(self):
        return ":{0!r} {1!r} {2!r} :{3!r}".format(*self.to_tuple())

    def __str__(self):
        return format_line(*self.to_tuple())

    def to_tuple(self):
        return self.source, self.command, self.parameters, self.trailing

    @property
    def sender(self):
        return self.source[0]

    @property
    def me(self):
        if hasattr(self.connection, 'nick'):
            return self.connection.nick
        return None


class ChannelMessage(Message):
    def init(self):
        # The first parameter in a channel message is always the receiver
        self.receiver = self.parameters.pop(0)

        # If the message has been sent directly to me, the sender can be
        # found in the source and the message is 'private'
        if self.receiver == self.me:
            self.channel = self.sender
            self.private = True
        # Otherwise, the message was sent to a channel I am in
        else:
            self.channel = self.receiver
            self.private = False


# RFC 1459: Internet Relay Chat Protocol
# 4.1 Connection Registration


@Message.register
class Quit(Message):
    reason = property(lambda self: self.trailing)


@Message.register
class Join(Message):
    channel = property(lambda self: self.parameters[0])

    def parameters(self, channel):
        """TODO: Implement this"""
        self.channel = channel


@Message.register
class Part(Message):
    channel = property(lambda self: self.parameters[0])


@Message.register
class Topic(Message):
    channel = property(lambda self: self.parameters[0])


# 4.4 Sending messages


@Message.register
class Privmsg(ChannelMessage):
    text = property(lambda self: self.trailing)

    def reply(self, message):
        self.connection.privmsg(self.channel, message)


@Message.register
class Notice(ChannelMessage):
    def reply(self):
        raise Exception("Don't reply to IRC NOTICE messages")


# 6.2 Command responses


@Message.register_numeric(331)
def no_topic(**kwargs):
    """Return a Topic event with an empty topic"""
    kwargs['trailing'] = ""
    return Topic(**kwargs)


@Message.register_numeric(332)
class Topic(Message):
    topic = property(lambda self: self.trailing)


@Message.register_numeric(333)
class TopicMeta(Message):
    channel = property(lambda self: self.parameters[1])
    setter = property(lambda self: self.parameters[2])
    time = property(lambda self: self.parameters[3])


@Message.register_numeric(375)
def motd_start(connection, **kwargs):
    connection.motd = ""


@Message.register_numeric(372)
def motd(connection, trailing, **kwargs):
    connection.motd += trailing[2:] + "\n"


@Message.register_numeric(376)
class MOTD(Message):
    text = property(lambda self: self.connection.motd)

    def init(self):
        """Strip the trailing newline from the MOTD"""
        self.connection.motd = self.connection.motd[:-1]


# RFC 2812 - Internet Relay Chat: Client Protocol
# 5.1 Command responses


@Message.register_numeric(001)
class RPL_WELCOME(Message):
    pass
