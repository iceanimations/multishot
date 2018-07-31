# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\fillinout\src\_fillinout.py
# Compiled at: 2017-11-08 17:37:11
import pymel.core as pc, os.path as op, site
from ... import imaya

def removeOverrides(attr):
    count = 0
    for renderLayer in pc.nt.RenderLayer.listAllRenderLayers():
        try:
            count += renderLayer.removeAdjustments(attr)
        except RuntimeError:
            pass

    return count


def fill():
    sel = pc.ls(sl=True)
    if not sel:
        pc.warning('Select a mesh or camera')
        return
    if len(sel) > 1:
        pc.warning('Select only one camera or mesh')
        return
    try:
        obj = sel[0].getShape(ni=True)
    except:
        pc.warning('Selection should be camera or mesh')
        return

    if type(obj) == pc.nt.Mesh:
        try:
            cache = obj.history(type='cacheFile')[0]
        except IndexError:
            pc.warning('No cache found on the selected object')
            return

        start = cache.sourceStart.get()
        end = cache.sourceEnd.get()
    else:
        if type(obj) == pc.nt.Camera:
            animCurves = pc.listConnections(obj.firstParent(), scn=True, d=False, s=True)
            if not animCurves:
                pc.warning('No animation found on the selected camera...')
                return
            frames = pc.keyframe(animCurves[0], q=True)
            if not frames:
                pc.warning('No keys found on the selected camera...')
                return
            start = frames[0]
            end = frames[-1]
            imaya.setRenderableCamera(obj)
        else:
            pc.warning('Selection should be camera or mesh')
            return
    pc.playbackOptions(minTime=start)
    pc.setAttr('defaultRenderGlobals.startFrame', start)
    pc.playbackOptions(maxTime=end)
    pc.setAttr('defaultRenderGlobals.endFrame', end)
    pc.currentTime(start)
    return (
     start, end)
# okay decompiling _fillinout.pyc
