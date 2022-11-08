import threading
from enum import Enum
from pathlib import Path


class ConfigKey(str, Enum):
    general = 'general'
    left_control_virtualtree = 'widgets.left_control.control_virtualtree.NetWorkFileSystemTreeView'
    http_code_widget = 'widgets.tabs.tab_httpfile'


class ConfigProvider(object):
    _defaults = {}

    @classmethod
    def register_configs(cls, values):
        cls._defaults = values

    @classmethod
    def default(cls, key: ConfigKey, name: str):
        return _Lazy(cls._proxy, key, name, cls._poxy_setter)

    @classmethod
    def _proxy(cls, key, name):
        return cls._defaults.get(key, {}).get(name)

    @classmethod
    def _poxy_setter(cls, key, name, value):
        cls._defaults.get(key, {})[name] = value


class _Lazy(object):
    lock = threading.Lock()

    def __init__(self, func, key, name, func_setter):
        self._func_key = key
        self._func_name = name
        self._func = func
        self._func_setter = func_setter
        self._observe = []

    @property
    def value(self):
        with self.lock:
            return self._func(self._func_key, self._func_name)

    @value.setter
    def value(self, v):
        with self.lock:
            self._func_setter(self._func_key, self._func_name, v)
            for func in self._observe:
                func(self._func_key, self._func_name, v)

    def observe(self, func):
        self._observe.append(func)
        return func


def get_file_type_and_name(file_path: str):
    path = Path(file_path)
    file_type = path.suffix.replace('.', '') + ' File'
    file_name = path.name
    return file_type, file_name

import jedi
jedi.get_default_environment()