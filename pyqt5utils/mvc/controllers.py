from PyQt5.QtCore import QObject
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLineEdit

from types import MethodType
from typing import Generic, TypeVar, Type, List, Optional, Dict

from ._types import ControllerTypes
from .managers import ControllerManager

T = TypeVar('T', bound=QWidget)


class Base(object):
    _control_manager_ = ControllerManager()

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self._controllers_: Dict[ControllerTypes, 'Controller'] = {}

    def create_controllers(self) -> List['Controller']:
        return []

    def build_controllers(self):
        for control in self.create_controllers():
            self._control_manager_.register(control.name or control.__class__.__name__, control)
            control._build()
            if hasattr(control, 'when_build'):
                control.when_build()

        register = getattr(self, '_register_controllers_', [])
        for control_cls in register:
            value = register[control_cls]
            target = getattr(self, value, None)
            assert target is not None
            control = control_cls(target, self)
            self._controllers_[control_cls.name or control_cls.__name__] = control
            self._control_manager_.register(control_cls.name or control_cls.__name__, control)
            control._build()

    @property
    def controllers(self) -> List['Controller']:
        return list(self._control_manager_.values())

    def controller_for(self, control_type: 'ControllerTypes') -> Optional['Controller']:
        return self._control_manager_.get(control_type)

    @classmethod
    def register_controller(cls, controller_name: 'ControllerTypes', controller: Type['Controller']) -> Type[
        'Controller']:
        if getattr(cls, '_register_controllers_', None) is None:
            cls._register_controllers_ = {}
            cls._register_controllers_[controller_name] = controller
        else:
            cls._register_controllers_[controller_name] = controller
        return controller


K = TypeVar('K', bound=Base)


class _ControlUtils(QObject):

    def set_fmheight(self, target: QWidget, scaled: float, value: int = 0):
        fm = target.fontMetrics()
        height = fm.height() * scaled + value
        target.setFixedHeight(height)
        return height

    def set_fmwidth(self, target: QWidget, content: str, scaled: float = 1.0, value: int = 0):
        fm = target.fontMetrics()
        width = fm.width(content) * scaled + value
        target.setFixedWidth(width)
        return width

    def set_double_validator(self, line: QLineEdit, min_=0, max_=9999999999, digit=2) -> QDoubleValidator:
        def _currentText(this):
            return this.__class__.text(this).replace(',', '').strip()

        validator = QDoubleValidator(min_, max_, digit)
        validator.setNotation(QDoubleValidator.StandardNotation)
        line.setValidator(validator)
        line.text = MethodType(_currentText, line)
        return validator


class OverRider(object):

    def __init__(self) -> None:
        self._instance: Controller = None
        self._over_func = []

    def __get__(self, instance, owner=None):
        assert isinstance(instance, Controller)
        self._instance = instance
        return self

    def __set__(self, value):
        pass

    def __call__(self, func):
        self._over_func.append(func)
        return self


class Controller(Generic[T, K], _ControlUtils):
    name: ControllerTypes = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        rider = None
        for k in cls.__dict__:
            if isinstance(cls.__dict__[k], OverRider):
                rider = cls.__dict__[k]
                break
        cls._valid_rider = rider
        cls._instance = None

    def __init__(self, widget: T, master: K) -> None:
        super().__init__()
        self._widget: T = widget
        self._master: K = master
        self.__class__._instance = self

    def _build(self):
        if self._valid_rider:
            for f in self._valid_rider._over_func:
                setattr(self._widget, f.__name__, MethodType(f, self._widget))

    @property
    def widget(self) -> T:
        return self._widget

    @property
    def master(self) -> K:
        return self._master

    @classmethod
    def instance(cls) -> 'Controller[T, K]':
        return cls._instance

    def when_build(self):
        pass
