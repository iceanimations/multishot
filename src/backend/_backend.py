# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\_backend.py
# Compiled at: 2017-11-08 17:37:11
import pymel.core as pc, maya.cmds as cmds, os
__poly_count__ = False
__HUD_DATE__ = '__HUD_DATE__'
__HUD_LABEL__ = '__HUD_LABEL__'
__HUD_USERNAME__ = '__HUD_USERNAME__'
__CURRENT_FRAME__ = 0.0

def playblast(data):
    pc.playblast(st=data['start'], et=data['end'], f=data['path'], fo=True, quality=100, w=1280, h=720, compression='MS-CRAM', percent=100, format='avi', sequenceTime=0, clearCache=True, viewer=False, showOrnaments=True, fp=4, offScreen=True)


def getUsername():
    return os.environ.get('USERNAME')


def label():
    return 'ICE Animations'


def setCurrentFrame():
    global __CURRENT_FRAME__
    __CURRENT_FRAME__ = pc.currentTime()


def restoreCurrentFrame():
    pc.currentTime(__CURRENT_FRAME__)


def hidePolyCount():
    global __poly_count__
    if pc.optionVar(q='polyCountVisibility'):
        __poly_count__ = True
        pc.Mel.eval('setPolyCountVisibility(0)')


def showPolyCount():
    global __poly_count__
    if __poly_count__:
        pc.Mel.eval('setPolyCountVisibility(1)')
        __poly_count__ = False


def showNameLabel():
    global __HUD_LABEL__
    global __HUD_USERNAME__
    pc.headsUpDisplay(__HUD_LABEL__, section=2, block=0, blockSize='large', dfs='large', command=label)
    pc.headsUpDisplay(__HUD_USERNAME__, section=3, block=0, blockSize='large', dfs='large', command=getUsername)


def showDate():
    global __HUD_DATE__
    pc.headsUpDisplay(__HUD_DATE__, section=1, block=0, blockSize='large', dfs='large', command='pc.date(format="DD/MM/YYYY hh:mm")')


def removeNameLabel():
    if pc.headsUpDisplay(__HUD_LABEL__, exists=True):
        pc.headsUpDisplay(__HUD_LABEL__, rem=True)
    if pc.headsUpDisplay(__HUD_USERNAME__, exists=True):
        pc.headsUpDisplay(__HUD_USERNAME__, rem=True)


def removeDate():
    if pc.headsUpDisplay(__HUD_DATE__, exists=True):
        pc.headsUpDisplay(__HUD_DATE__, rem=True)
# okay decompiling _backend.pyc
