# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\sui.py
# Compiled at: 2017-11-08 17:37:11
from cStringIO import StringIO
from Qt import QtWidgets
from Qt.QtCompat import wrapInstance as wrap
import maya.OpenMayaUI as apiUI

def getMayaWindow():
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrap(long(ptr), QtWidgets.QWidget)
    return


class MessageBox(QtWidgets.QMessageBox):

    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

    def closeEvent(self, event):
        self.deleteLater()


def showMessage(parent, title='Shot Export', msg='Message', btns=QtWidgets.QMessageBox.Ok, icon=None, ques=None, details=None, **kwargs):
    mBox = MessageBox(parent)
    mBox.setWindowTitle(title)
    mBox.setText(msg)
    if ques:
        mBox.setInformativeText(ques)
    if icon:
        mBox.setIcon(icon)
    if details:
        mBox.setDetailedText(details)
    customButtons = kwargs.get('customButtons')
    mBox.setStandardButtons(btns)
    if customButtons:
        for btn in customButtons:
            mBox.addButton(btn, QtGui.QMessageBox.AcceptRole)

    pressed = mBox.exec_()
    if customButtons:
        cBtn = mBox.clickedButton()
        if cBtn in customButtons:
            return cBtn
    return pressed
# okay decompiling sui.pyc
