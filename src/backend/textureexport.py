# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26)
# [MSC v.1500 64 bit (AMD64)]
# Embedded file name:
# C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\textureexport.py
# Compiled at: 2017-11-08 17:37:11

import shotactions
import shotplaylist
import os.path as osp
import pymel.core as pc
import os
import shutil
import re
from . import exportutils


PlayListUtils = shotplaylist.Playlist
Action = shotactions.Action
errorsList = []


class TextureExport(Action):

    def __init__(self, *args, **kwargs):
        super(TextureExport, self).__init__(*args, **kwargs)
        if not self._conf:
            self._conf = TextureExport.initConf()
        if not self.path:
            self.path = osp.expanduser('~')
        if not self.get('texture_attrs'):
            self['texture_attrs'] = []

    @staticmethod
    def initConf():
        conf = dict()
        conf['texture_export_data'] = [
         (
          '(?i).*nano.*', ['ExpRenderPlaneMtl.outColor'])]
        conf['texture_resX'] = 1024
        conf['texture_resY'] = 1024
        return conf

    def perform(self, **kwargs):
        if self.enabled:
            conf = self._conf
            self.exportAnimatedTextures(conf)

    @staticmethod
    def getAnimatedTextures(conf):
        """ read conf to get candidate textures from the scene """
        texture_attrs = []
        for key, attrs in conf.get('texture_export_data', []):
            for namespace in pc.namespaceInfo(lon=True):
                if re.match(key, namespace):
                    for attr in attrs:
                        attr = pc.Attribute(namespace + ':' + attr)
                        texture_attrs.append(attr)

        return texture_attrs

    def getNameToAttrMapping(self):
        """ find attrs in the scene and determine their file texture name """
        nameToAttrMapping = []
        texture_attrs = self.get('texture_attrs', [])
        for attr in texture_attrs:
            try:
                attribute = pc.Attribute(attr)
                name = attr.split('|')[-1]
                name = ('_').join(name.split(':')[:-1])
                name += '.' + name.split('.')[-1]
                nameToAttrMapping.append((name, attribute))
            except Exception as ex:
                print str(ex)

    def exportAnimatedTextures(self, conf):
        """ bake export animated textures from the scene """
        if not self.get('objects'):
            return False
        tempFilePath = osp.join(self.tempPath, 'tex')
        if osp.exists(tempFilePath):
            shutil.rmtree(tempFilePath)
        os.mkdir(tempFilePath)
        start_time = int(self._item.getInFrame())
        end_time = int(self._item.getOutFrame())
        rx = conf['texture_resX']
        ry = conf['texture_resY']
        nameToAttrMapping = self.getNameToAttrMapping()
        if exportAsTextures(
                nameToAttrMapping, startTime=start_time, endTime=end_time,
                rx=rx, ry=ry, outputDir=tempFilePath):
            target_dir = osp.join(self.path, 'tex')
            try:
                if not osp.exists(target_dir):
                    os.mkdir(target_dir)
            except Exception as ex:
                errorsList.append(str(ex))

            for phile in os.listdir(tempFilePath):
                philePath = osp.join(tempFilePath, phile)
                exportutils.copyFile(philePath, target_dir, depth=4)


def exportAsTextures(
        nameToAttrMapping, startTime=None, endTime=None, rx=1024, ry=1024,
        outputDir='images'):
    """ Export """
    textures_exported = False
    if not startTime:
        startTime = pc.playbackOptions(q=True, min=True)
    if not endTime:
        endTime = pc.playbackOptions(q=True, max=True)
    for curtime in range(startTime, endTime + 1):
        num = '%04d' % curtime
        pc.currentTime(curtime, e=True)
        for name, attr in nameToAttrMapping:
            fileImageName = osp.join(outputDir, ('.').join([name, num, 'iff']))
            try:
                newobj = pc.convertSolidTx(
                        attr, samplePlane=True, rx=rx, ry=ry, fil='tif',
                        fileImageName=fileImageName)
                pc.delete(newobj)
                textures_exported = True
            except (WindowsError, IOError):
                pass

    return textures_exported
# okay decompiling textureexport.pyc
