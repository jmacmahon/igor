"""A callback manager"""

import importlib

import igor.utils


class Manager(dict):
    def __init__(self):
        self.log = igor.utils.getLogger(self)

    def load_plugins(self, config):
        for name, conf in config.items():
            self.load_plugin(name, **conf)

    def load_plugin(self, name, module):
        self[name] = getattr(importlib.import_module(module), name)()

    def unload_plugin(self, name):
        del self[name]

    def __call__(self, event):
        for plugin in self.values():
            plugin(event)
