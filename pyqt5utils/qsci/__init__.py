try:
    from PyQt5 import Qsci

    sci_support = True
except ImportError:
    sci_support = False

__all__ = (
    'sci_support'
)
