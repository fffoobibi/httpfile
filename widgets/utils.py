import threading
from enum import Enum
from pathlib import Path

from PyQt5.QtGui import QIcon

__all__ = ('ConfigKey', 'ConfigProvider', 'IconProvider', 'get_file_type_and_name', 'hum_convert')


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


class IconProvider(object):
    @classmethod
    def get_icon(cls, file_name: str, is_dir: bool=False) -> QIcon:
        file_type = file_name.split('.')[-1].strip() + ' File'
        if is_dir:
            return QIcon(':/icon/文件夹.svg')
        if file_type in ['txt File', 'File']:
            return QIcon(':/icon/txt.svg')
        elif file_type in ['py File', 'pyw File']:
            return QIcon(':/icon/python-misc.svg')
        elif file_type in ['json File']:
            return QIcon(':/icon/json.svg')
        elif file_type in ['js File']:
            return QIcon(':/icon/txt.svg')
        elif file_type in ['css File']:
            return QIcon(':/icon/css.svg')
        elif file_type in ['ui File']:
            return QIcon(':/icon/file-xml.svg')
        elif file_type in ['http File']:
            return QIcon(':/icon/HTTP.svg')
        elif file_type in ['html File']:
            return QIcon(':/icon/html.svg')
        return QIcon('')


def get_file_type_and_name(file_path: str):
    path = Path(file_path)
    file_type = path.suffix.replace('.', '') + ' File'
    file_name = path.name
    return file_type, file_name


def hum_convert(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size
