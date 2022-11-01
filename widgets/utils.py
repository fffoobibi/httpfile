from enum import Enum


class ConfigKey(str, Enum):
    general = 'general'
    left_control_virtualtree = 'widgets.left_control.control_virtualtree.NetWorkFileSystemTreeView'


class ConfigProvider(object):
    _defaults = {}

    @classmethod
    def register_configs(cls, values):
        cls._defaults = values

    @classmethod
    def default(cls, key: ConfigKey, name: str):
        return _Lazy(lambda: cls._proxy(key, name))

    @classmethod
    def _proxy(cls, key, name):
        return cls._defaults.get(key, {}).get(name)


class _Lazy(object):
    def __init__(self, func):
        self._func = func

    @property
    def value(self):
        return self._func()



