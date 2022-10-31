import json
import threading
import typing

from functools import wraps

from PyQt5.QtCore import QSettings

from pyqt5utils.workers import WorkerManager, BackgroundWorker
from widgets.signals import app_exit, app_start_up


def _after(clz, func_name):
    def decorator(func):
        @wraps(func)
        def inner(self, *a, **kw):
            getattr(clz, f'__old_{func_name}')(self, *a, **kw)
            ret = func(self, *a, **kw)
            return ret

        setattr(clz, f'__old_{func_name}', getattr(clz, func_name))
        return inner

    return decorator


class _Settings(QSettings):

    def set_serializer(self, serialzer):
        self._serialzer = serialzer

    def setValue(self, key: str, value: typing.Any, use_ser=True) -> None:
        if use_ser:
            data = self._serialzer[0](value)
            super().setValue(key, data)
        else:
            super().setValue(key, value)

    def value(self, key: str, defaultValue: typing.Any = None, type=None, use_ser=True) -> typing.Any:
        if use_ser:
            value = super().value(key, defaultValue)
            if value == defaultValue:
                return value
            return self._serialzer[1](value)
        else:
            return super().value(key, defaultValue, type)


def _settings_dump(data):
    return json.dumps(data, ensure_ascii=False)


def _settings_load(data):
    return json.loads(data)


def _plugin_init_(self, *a, **kw):
    def _app_start(args):
        self.when_app_start_up(args)

    def _app_exit(args):
        self.when_app_exit(args)

    self.settings = self.settings_class(self.settings_name, QSettings.IniFormat)
    self.settings.setIniCodec('UTF-8')
    self.settings.set_serializer(self.settings_serializers)
    app_start_up.connect(_app_start, weak=False)
    app_exit.connect(_app_exit, weak=False)

    self.after_init()


class PluginBaseMixIn(object):
    worker_class = WorkerManager
    worker_name = 'pluginbasemixin'
    __worker_instances__ = dict()

    settings_class = _Settings
    settings_name = './config.ini'
    settings_serializers = [_settings_dump, _settings_load]

    settings: _Settings = None  # type hint bad but necessary

    __provider__ = dict()
    __provider_lock__ = threading.Lock()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls.__init__ = _after(cls, '__init__')(_plugin_init_)

    def after_init(self):
        pass

    @property
    def worker(self) -> BackgroundWorker:
        if self.__worker_instances__.get(self.worker_name, None) is None:
            self.__worker_instances__[self.worker_name] = self.worker_class().get(self.worker_name)
        return self.__worker_instances__.get(self.worker_name)

    def config_name(self, key_name: str) -> str:
        return f'{self.__class__.__name__}/{key_name}'

    cn = config_name

    def when_app_exit(self, main_app):
        pass

    def when_app_start_up(self, main_app):
        pass

    def set_provider(self, key, target):
        with self.__provider_lock__:
            self.__provider__[key] = target

    sp = set_provider

    def get_provider(self, key):
        with self.__provider_lock__:
            return self.__provider__[key]

    gp = get_provider
