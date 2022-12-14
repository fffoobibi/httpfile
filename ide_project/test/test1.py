# -*- coding: utf-8 -*-
# @Time    : 2022/3/8 9:40
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : test1.py
# @Software: PyCharm
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtWidgets import QApplication

app = QApplication([])

ed = QsciScintilla()

ed.setText('insert <-\nsome <-\ntext <-\n')
ed.show()

# typing should insert in all selections at the same time
ed.SendScintilla(ed.SCI_SETADDITIONALSELECTIONTYPING, 1)

# do multiple selections
offset = ed.positionFromLineIndex(0, 7) # line-index to offset
ed.SendScintilla(ed.SCI_SETSELECTION, offset, offset)
# using the same offset twice selects no characters, hence a cursor

offset = ed.positionFromLineIndex(1, 5)
ed.SendScintilla(ed.SCI_ADDSELECTION, offset, offset)

offset = ed.positionFromLineIndex(2, 5)
ed.SendScintilla(ed.SCI_ADDSELECTION, offset, offset)

app.exec_()