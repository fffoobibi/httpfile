# -*- coding: utf-8 -*-
# @Time    : 2022/10/31 14:28
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : run.py
# @Software: PyCharm
import ast

from pyflakes import checker, messages
from pyflakes.reporter import _makeDefaultReporter


def check(codeString, filename, reporter=None):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @param reporter: A L{Reporter} instance, where errors and warnings will be
        reported.

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    if reporter is None:
        reporter = _makeDefaultReporter()
    # First, compile into an AST and handle syntax errors.
    try:
        tree = ast.parse(codeString, filename=filename)
    except SyntaxError as e:
        print(111111)
        reporter.syntaxError(filename, e.args[0], e.lineno, e.offset, e.text)
        return 1
    except Exception:
        print(222222)
        reporter.unexpectedError(filename, 'problem decoding source')
        return 1
    # Okay, it's syntactically valid.  Now check it.
    w = checker.Checker(tree, filename=filename)
    w.messages.sort(key=lambda m: m.lineno)
    for warning in w.messages:
        reporter.flake(warning)
    return len(w.messages), w.messages

from widgets.mainwidget import run

code = '''
1+2

import time
try:
    1/0
except:
    pass

'''

#
# w = check(code, 'run.py')
# print(w)
# c, meesage = w
# for m in meesage:
#     print(m, m.lineno, m.col, m.message_args)

if __name__ == '__main__':
    run()
