from enum import Enum


class ConfigKey(str, Enum):
    left_control_virtualtree = 'widgets.left_control.control_virtualtree.NetWorkFileSystemTreeView'


class ConfigProvider(object):
    _defaults = {}

    @classmethod
    def register_configs(cls, values):
        cls._defaults = values

    @classmethod
    def default(cls, key: ConfigKey, name: str):
        return cls._defaults.get(key, {}).get(name)
