# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\sui.py
# Compiled at: 2017-11-08 17:37:11
from cStringIO import StringIO
import pysideuic
import xml.etree.ElementTree as xml
from PySide import QtGui
from shiboken import wrapInstance as wrap
import maya.OpenMayaUI as apiUI

def loadUiType(uiFile):
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    with open(uiFile, 'r') as (f):
        o = StringIO()
        frame = {}
        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame
        form_class = frame['Ui_%s' % form_class]
        base_class = eval('QtGui.%s' % widget_class)
    return (form_class, base_class)


def getMayaWindow():
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrap(long(ptr), QtGui.QWidget)
    return


class MessageBox(QtGui.QMessageBox):

    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

    def closeEvent(self, event):
        self.deleteLater()


def showMessage(parent, title='Shot Export', msg='Message', btns=QtGui.QMessageBox.Ok, icon=None, ques=None, details=None, **kwargs):
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
