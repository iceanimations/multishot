# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\playblast.py
# Compiled at: 2017-11-08 17:37:11
import shotactions, shotplaylist
PlayListUtils = shotplaylist.PlaylistUtils
Action = shotactions.Action
from collections import OrderedDict
import pymel.core as pc, os, os.path as osp, exportutils, shutil, maya.cmds as cmds
from exceptions import *
import json, imaya
reload(imaya)
reload(exportutils)
__poly_count__ = False
__HUD_DATE__ = '__HUD_DATE__'
__HUD_LABEL__ = '__HUD_LABEL__'
__HUD_USERNAME__ = '__HUD_USERNAME__'
__CURRENT_FRAME__ = 0.0

def playblast(data):
    pc.playblast(st=data['start'], et=data['end'], f=data['path'], fo=True, quality=100, w=1280, h=720, compression='MS-CRAM', percent=100, format='avi', sequenceTime=0, clearCache=True, viewer=False, showOrnaments=True, fp=4, offScreen=True)


def getUsername():
    return ''#os.environ.get('USERNAME').upper().replace('.', ' ')


def label():
    return 'ICE ANIMATIONS'


def recordCurrentFrame():
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
    if pc.headsUpDisplay(__HUD_LABEL__, q=True, exists=True):
        pc.headsUpDisplay(__HUD_LABEL__, remove=True)
    pc.headsUpDisplay(__HUD_LABEL__, section=2, block=pc.headsUpDisplay(nfb=2), blockSize='large', dfs='large', command=label)
    if pc.headsUpDisplay(__HUD_USERNAME__, q=True, exists=True):
        pc.headsUpDisplay(__HUD_USERNAME__, remove=True)
    pc.headsUpDisplay(__HUD_USERNAME__, section=3, block=pc.headsUpDisplay(nfb=3), blockSize='large', dfs='large', command=getUsername)
    pc.headsUpDisplay(__HUD_USERNAME__, e=True, dfs='large')


def showDate():
    global __HUD_DATE__
    if pc.headsUpDisplay(__HUD_DATE__, q=True, exists=True):
        pc.headsUpDisplay(__HUD_DATE__, remove=True)
    pc.headsUpDisplay(__HUD_DATE__, section=1, block=pc.headsUpDisplay(nfb=1), blockSize='large', dfs='large', command='import pymel.core as pc;pc.date(format="DD/MM/YYYY hh:mm")')


def removeNameLabel():
    if pc.headsUpDisplay(__HUD_LABEL__, exists=True):
        pc.headsUpDisplay(__HUD_LABEL__, rem=True)
    if pc.headsUpDisplay(__HUD_USERNAME__, exists=True):
        pc.headsUpDisplay(__HUD_USERNAME__, rem=True)


def removeDate():
    if pc.headsUpDisplay(__HUD_DATE__, exists=True):
        pc.headsUpDisplay(__HUD_DATE__, rem=True)


class PlayblastExport(Action):
    _conf = None

    def __init__(self, *args, **kwargs):
        super(PlayblastExport, self).__init__(*args, **kwargs)
        self._conf = self.initConf()
        if not self.get('layers'):
            self['layers'] = []
        if not self.path:
            self.path = osp.expanduser('~')

    @staticmethod
    def initConf():
        conf = OrderedDict()
        playblastargs = OrderedDict()
        playblastargs['format'] = 'qt'
        playblastargs['fo'] = True
        playblastargs['quality'] = 100
        playblastargs['w'] = 1280
        playblastargs['h'] = 720
        playblastargs['percent'] = 100
        playblastargs['compression'] = 'H.264'
        playblastargs['format'] = 'qt'
        playblastargs['sequenceTime'] = 0
        playblastargs['clearCache'] = True
        playblastargs['viewer'] = False
        playblastargs['showOrnaments'] = True
        playblastargs['fp'] = 4
        playblastargs['offScreen'] = True
        huds = OrderedDict()
        conf['playblastargs'] = playblastargs
        conf['HUDs'] = huds
        return conf

    def perform(self, readconf=True, **kwargs):
        if self.enabled:
            for layer in PlayListUtils.getDisplayLayers():
                if layer.name() in self.getLayers():
                    layer.visibility.set(1)
                else:
                    layer.visibility.set(0)

            item = self.__item__
            try:
                if readconf:
                    self.read_conf()
            except IOError:
                self._conf = PlayblastExport.initConf()

            pc.select(item.camera)
            pc.lookThru(item.camera)
            hidePolyCount()
            showDate()
            exportutils.turnResolutionGateOn(item.camera)
            exportutils.showFrameInfo(item)
            exportutils.setDefaultResolution((1920, 1080), default=kwargs.get('defaultResolution'))
            exportutils.turn2dPanZoomOff(item.camera)
            if not kwargs.get('hdOnly'):
                self.makePlayblast(sound=kwargs.get('sound'), local=kwargs.get('local'))
            
            exportutils.turnResolutionGateOff(item.camera)
            if kwargs.get('hd'):
                
                exportutils.turnResolutionGateOffPer(item.camera)
                exportutils.setDefaultResolution((1920, 1080))
                self.makePlayblast(sound=kwargs.get('sound'), hd=True, local=kwargs.get('local'))
                showNameLabel()
            exportutils.removeFrameInfo(all=True)
            removeDate()
            removeNameLabel()
            showPolyCount()
            exportutils.restoreDefaultResolution()
            exportutils.restore2dPanZoom(item.camera)
        exportutils.restoreFrameInfo()

    def addLayers(self, layers):
        self['layers'][:] = layers

    def getLayers(self):
        return self.get('layers', [])

    def getPath(self):
        return self.get('path')

    def setPath(self, val):
        self['path'] = val

    path = property(getPath, setPath)

    def addHUDs(self):
        conf = self._conf
        for hud in conf.get('HUDs', {}):
            if pc.headsUpDisplay(hud, q=True, exists=True):
                pc.headsUpDisplay(hud, remove=True)
            pc.headsUpDisplay(hud, **conf['HUDS'][hud])

    def removeHUDs(self):
        conf = self._conf
        for hud in conf.get('HUDs', []):
            if pc.headsUpDisplay(hud, q=True, exists=True):
                pc.headsUpDisplay(hud, remove=True)

    def makePlayblast(self, item=None, sound=None, hd=False, local=False):
        if not item:
            item = self.__item__
            if not item:
                pc.warning('Item not set: cannot make playblast')
        conf = self._conf
        if sound:
            sound = exportutils.getAudioNode()
            if not sound:
                sound = [
                 '']
        else:
            sound = [
             '']
        itemName = imaya.getNiceName(item.name)
        tempFilePath = osp.join(self.tempPath, itemName)
        pc.playblast(format='qt', fo=1, st=item.getInFrame(), et=item.getOutFrame(), f=tempFilePath, s=str(sound[0]), sequenceTime=0, clearCache=1, viewer=0, showOrnaments=1, fp=4, percent=100, compression='H.264', quality=100, widthHeight=exportutils.getDefaultResolution(), offScreen=1)
        tempFilePath += '.mov'
        if hd:
            depth = 4
            path = self.path
            try:
                os.mkdir(path)
            except:
                pass

        else:
            depth = 3
            path = self.path
        infoFilePath = osp.join(osp.dirname(tempFilePath), itemName + '.json')
        infoFileOrigPath = osp.join(path, itemName + '.json')
        data = ''
        if osp.exists(infoFileOrigPath):
            with open(infoFileOrigPath) as (ifr):
                data = json.loads(ifr.read())
        with open(infoFilePath, 'a') as (infoFile):
            newData = [
             {'user': getUsername(), 'time': pc.date(format='DD/MM/YYYY hh:mm'), 'inOut': ('-').join([str(item.inFrame), str(item.outFrame)]), 'name': itemName, 
                'focalLength': item.camera.focalLength.get()}]
            if data:
                if type(data) == type([]):
                    newData[0]['user'] = data[0]['user']
                    newData.extend(data)
                if type(data) == type({}):
                    newData[0]['user'] = data['user']
                    newData.append(data)
            infoFile.write(json.dumps(newData))
        if local:
            path = exportutils.getLocalDestination(path, depth)
        exportutils.copyFile(infoFilePath, self.path, depth=3)
        exportutils.copyFile(tempFilePath, path, depth=depth)
# okay decompiling playblast.pyc
