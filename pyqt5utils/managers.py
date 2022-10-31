import logging
import threading

from types import MethodType
from typing import List, Dict, Type

from pyqt5utils.decorators import singleton
from pyqt5utils.components.caches import ImageCacheManager

from PyQt5.QtWidgets import QUndoCommand, QUndoStack
from PyQt5.QtCore import QSettings

__all__ = (
    'ImageCacheManager', 'DomainManager', 'LoggerManager', 'CommandsManager', 'HotkeysManager', 'Domains'
)


class Domains(object):
    domain_fields: List[str] = ['http', 'websocket', 'image']

    domain_types: List[str] = ['product', 'debug']

    product: Dict[str, str] = dict(
        http='http://www.baidu.com',
        websocket='ws://www.test.com',
        image='http://www.test-image.com')

    debug: Dict[str, str] = dict(http='http://www.baidu.com',
                                 websocket='ws://www.test.com',
                                 image='http://www.test-image.com')


@singleton
class DomainManager(object):
    mode = 'debug'
    file = 'dms.ini'

    def field_types(self) -> List[str]:
        return self._domain_class.domain_fields

    def domain_types(self) -> List[str]:
        return self._domain_class.domain_types

    def __init__(self, domain_class: Type = Domains) -> None:
        self._domain_class = domain_class
        self._values = {}

    def get_domain(self, field=''):
        if self._values == {}:
            self.load()
        return self._values.get(self.mode, {}).get(field, '')

    def save(self):
        file = QSettings(self.file, QSettings.IniFormat)
        file.setIniCodec('UTF-8')
        for key in self._domain_class.domain_types:
            for k2 in self._domain_class.domain_fields:
                v = self._values.get(key, {}).get(k2, '')
                file.setValue(f'{key}/{k2}', v)
        file.sync()

    def load(self):
        file = QSettings(self.file, QSettings.IniFormat)
        file.setIniCodec('UTF-8')
        for key in self._domain_class.domain_types:
            self._values[key] = {}
            for k2 in self._domain_class.domain_fields:
                dft_value = getattr(self._domain_class, key, {}).get(k2, '')
                value = file.value(f'{key}/{k2}', dft_value)
                self._values[key][k2] = value

    def __str__(self) -> str:
        return f'Domain<{self.mode}>'

    def __del__(self):
        if self._values:
            self.save()


@singleton
class LoggerManager(object):

    @classmethod
    def get_logger(cls, logger_name: str):
        if logger_name is not None:
            return logging.getLogger(logger_name)
        return


@singleton
class CommandsManager(object):
    class _CommandExecute(object):
        def __init__(self, name, help_text, values, manager) -> None:
            self.name = name
            self.help_text = help_text
            self.manager = manager
            self.values: dict = values
            self.func = None
            self.redo_func = None
            self.undo_func = None
            self._set_undo = False
            self._set_redo = False
            self._context = None

        def __call__(self, func):
            old_value = self.values.get(self.name or func.__name__, None)
            if self._set_undo:
                self.undo_func = func
            elif self._set_redo:
                self.redo_func = func
            else:
                self.func = func

            if old_value is None:
                self.values[self.name or func.__name__] = self
            else:
                self.func = self.func or old_value.func
                self.undo_func = self.undo_func or old_value.undo_func
                self.redo_func = self.redo_func or old_value.redo_func
                self.values[self.name or func.__name__] = self
            return self

        def __get__(self, instance, owner=None):
            self._context = instance
            return self

        def __set__(self, value):
            pass

        def undo(self):
            self.manager.undo()

        def redo(self):
            self.manager.push(self.name, self._context)

        def __str__(self) -> str:
            return f"Command<{self.name}, {self._set_redo}, {self._set_undo}>"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._values = {}
        self._current = None
        self._stack = QUndoStack()

    def register(self, cmd_name: str = None, help_text: str = None):
        return self._CommandExecute(cmd_name, help_text, self._values, self)

    def register_redo(self, cmd_name: str, help_text: str = None):
        old = self._values.get(cmd_name, None)
        ret = self._CommandExecute(cmd_name, help_text, self._values, self)
        ret._set_redo = True
        return ret

    def register_undo(self, cmd_name: str, help_text: str = None):
        old = self._values.get(cmd_name, None)
        ret = self._CommandExecute(cmd_name, help_text, self._values, self)
        ret._set_undo = True
        return ret

    def _get_register_command(self, cmd_name: str, *args, **kwargs) -> QUndoCommand:
        def _undo(this):
            with self._lock:
                try:
                    self._current = this
                    if execute_obj.undo_func:
                        execute_obj.undo_func(*args, **kwargs)
                finally:
                    self._current = None

        def _redo(this):
            with self._lock:
                try:
                    self._current = this
                    if execute_obj.redo_func:
                        execute_obj.redo_func(*args, **kwargs)
                finally:
                    self._current = None

        execute_obj = self._values.get(cmd_name)
        redo = None
        undo = None
        if execute_obj.func:
            redo, undo = execute_obj.func(*args, **kwargs)
        if execute_obj.redo_func is not None:
            redo = _redo
        if execute_obj.undo_func is not None:
            undo = _undo

        if redo is None:
            def redo(this): return None
        if undo is None:
            def undo(this): return None

        comand_instance = QUndoCommand()
        comand_instance.setText(execute_obj.help_text or '')
        comand_instance.undo = MethodType(undo, comand_instance)
        comand_instance.redo = MethodType(redo, comand_instance)
        return comand_instance

    def execute(self, cmd_name: str, *args, **kwargs):
        command = self._get_register_command(cmd_name, *args, **kwargs)
        self._stack.push(command)

    def clear(self):
        self._values.clear()
        self._stack.clear()

    def commands(self):
        return self._values.keys()

    def beginMacro(self, desc: str = ''):
        self._stack.beginMacro(desc)

    def endMacro(self):
        self._stack.endMacro()

    def push(self, cmd_name: str = None, *args, command: QUndoCommand = None, **kwargs, ):
        if cmd_name is not None:
            command = self._get_register_command(cmd_name, *args, **kwargs)
            self._stack.push(command)
        elif command is not None:
            self._stack.push(command)

    def undo(self):
        self._stack.undo()

    @property
    def current(self) -> QUndoCommand:
        return self._current


@singleton
class HotkeysManager(object):
    pass
