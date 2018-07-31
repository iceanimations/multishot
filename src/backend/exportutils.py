# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\exportutils.py
# Compiled at: 2017-11-08 17:37:11
import pymel.core as pc, maya.cmds as cmds, os
osp = os.path
import shutil, time, imaya, iutil
reload(imaya)
reload(iutil)
import fillinout
reload(fillinout)
errorsList = []
localPath = 'D:\\multishotexport'
if not osp.exists(localPath):
    try:
        os.mkdir(localPath)
    except:
        localPath = 'E:\\multishotexport'
        if not osp.exists(localPath):
            try:
                os.mkdir(localPath)
            except:
                pass

__original_camera__ = None
__original_frame__ = None
__selection__ = None
__resolutionGate__ = True
__safeAction__ = True
__safeTitle__ = True
__resolutionGateMask__ = True
__hud_frame_1__ = '__hud_frame_1__'
__hud_frame_2__ = '__hud_frame_2__'
__labelColor__ = None
__valueColor__ = None
__current_frame__ = None
__camera_name__ = None
__focal_length__ = None
__DEFAULT_RESOLUTION__ = None
__fps_mapping__ = {'game': '15 fps', 
   'film': 'Film (24 fps)', 'pal': 'PAL (25 fps)', 
   'ntsc': 'NTSC (30 fps)', 'show': 'Show 48 fps', 
   'palf': 'PAL Field 50 fps', 'ntscf': 'NTSC Field 60 fps', 
   'millisec': 'milliseconds', 'sec': 'seconds', 
   'min': 'minutes', 'hour': 'hours'}
__stretchMeshEnvelope__ = {}
__2d_pane_zoom__ = {}
home = osp.join(osp.expanduser('~'), 'temp_shots_export')
if not osp.exists(home):
    os.mkdir(home)

def camHasKeys(camera):
    return pc.listConnections(camera, scn=True, d=False, s=True)


def linkedLD(rigPath):
    return True


def getEnvFilePath():
    envs = []
    for ref in imaya.getReferences():
        if 'environment' in ref.path.lower():
            envs.append(str(ref.path))

    return envs


def getSaveFilePath(items):
    try:
        items = [ item for item in items if item.selected ]
        path = [ action for action in items[0].actions.getActions() if action.enabled ][0].path.split('SHOTS')[0]
        animPath = osp.join(path, 'ANIMATION')
        if not osp.exists(animPath):
            os.mkdir(animPath)
        path = osp.join(animPath, 'MULTISHOTEXPORT')
        if not osp.exists(path):
            os.mkdir(path)
        path = osp.join(path, ('__').join([ item.name for item in items ]))
        if not osp.exists(path):
            os.mkdir(path)
        return path
    except Exception as ex:
        errorsList.append('Could not save maya file\nReason: ' + str(ex))


def saveMayaFile(items):
    filename = cmds.file(q=True, location=True)
    if filename and osp.exists(filename):
        path = getSaveFilePath(items)
        if path and filename:
            copyFile(filename, path, move=False)


def turn2dPanZoomOff(camera):
    global __2d_pane_zoom__
    enabled = camera.panZoomEnabled.get()
    if enabled:
        __2d_pane_zoom__['enabled'] = enabled
        __2d_pane_zoom__['horizontalPan'] = camera.horizontalPan.get()
        camera.horizontalPan.set(0)
        __2d_pane_zoom__['verticalPan'] = camera.verticalPan.get()
        camera.verticalPan.set(0)
        __2d_pane_zoom__['zoom'] = camera.zoom.get()
        camera.zoom.set(1)
        camera.panZoomEnabled.set(0)


def restore2dPanZoom(camera):
    if __2d_pane_zoom__:
        camera.panZoomEnabled.set(__2d_pane_zoom__['enabled'])
        camera.horizontalPan.set(__2d_pane_zoom__['horizontalPan'])
        camera.verticalPan.set(__2d_pane_zoom__['verticalPan'])
        camera.zoom.set(__2d_pane_zoom__['zoom'])


def showInViewMessage(msg):
    pc.inViewMessage(msg='<hl>%s<hl>' % msg, fade=True, position='midCenter')


def switchCam(cam):
    pc.lookThru(cam)
    sel = pc.ls(sl=True)
    pc.select(cam)
    fillinout.fill()
    pc.select(sel)


def getAudioNodes():
    return pc.ls(type='audio')


def isConnected(_set):
    return pc.PyNode(_set).hasAttr('forCache') and pc.PyNode(_set).forCache.get()


def isCompatible(_set):
    try:
        return pc.polyEvaluate(_set, f=True) == pc.PyNode(_set).forCache.outputs()[0]
    except Exception as ex:
        pc.warning(str(ex))
        return True


def removeFile(path):
    try:
        os.remove(path)
    except Exception as ex:
        pc.warning(ex)


def getLocalDestination(des, depth=3):
    basename = iutil.basename(des, depth=depth)
    tempPath = osp.join(localPath, basename)
    if not osp.exists(tempPath):
        iutil.mkdir(localPath, basename)
    return tempPath


def copyFile(src, des, depth=3, move=True):
    src = osp.normpath(src)
    des = osp.normpath(des)
    try:
        existingFile = osp.join(des, osp.basename(src))
        if osp.exists(existingFile) and osp.isfile(existingFile):
            os.remove(existingFile)
        shutil.copy(src, des)
    except Exception as ex:
        try:
            basename = iutil.basename(des, depth)
            tempPath = osp.join(home, basename)
            if not osp.exists(tempPath):
                iutil.mkdir(home, basename)
            tempPath2 = osp.join(tempPath, osp.basename(src))
            if osp.exists(tempPath2):
                os.remove(tempPath2)
            shutil.copy(src, tempPath)
        except Exception as ex2:
            pc.warning(ex2)

        errorsList.append(str(ex))
    finally:
        if move:
            os.remove(src)


def hideFaceUi():
    sel = pc.ls(sl=True)
    pc.select(pc.ls(regex='(?i).*:?UI_grp'))
    pc.Mel.eval('HideSelectedObjects')
    pc.select(sel)


def showFaceUi():
    sel = pc.ls(sl=True)
    pc.select(pc.ls(regex='(?i).*:?UI_grp'))
    pc.showHidden(b=True)
    pc.select(sel)


def setDefaultResolution(res, default=False):
    global __DEFAULT_RESOLUTION__
    __DEFAULT_RESOLUTION__ = getDefaultResolution()
    if default:
        return
    node = pc.ls('defaultResolution')[0]
    node.width.set(res[0])
    node.height.set(res[1])


def restoreDefaultResolution():
    res = __DEFAULT_RESOLUTION__
    node = pc.ls('defaultResolution')[0]
    node.width.set(res[0])
    node.height.set(res[1])


def getDefaultResolution():
    node = pc.ls('defaultResolution')[0]
    return (
     node.width.get(), node.height.get())


def saveHUDColor():
    global __labelColor__
    global __valueColor__
    __labelColor__ = pc.general.displayColor('headsUpDisplayLabels', dormant=True, q=True)
    __valueColor__ = pc.general.displayColor('headsUpDisplayValues', dormant=True, q=True)


def restoreHUDColor():
    if __labelColor__ and __valueColor__:
        setHUDColor(__labelColor__, __valueColor__)


def setHUDColor(color1, color2):
    try:
        pc.general.displayColor('headsUpDisplayLabels', color1, dormant=True)
    except:
        pass

    try:
        pc.general.displayColor('headsUpDisplayValues', color2, dormant=True)
    except:
        pass


def getFrameRate():
    global __fps_mapping__
    unit = pc.general.currentUnit(q=True, time=True)
    fps = __fps_mapping__.get(unit)
    if fps:
        return fps
    return unit


def showFrameInfo(pl_item):
    global __camera_name__
    fps = getFrameRate()
    inOut = str(pl_item.inFrame) + ' - ' + str(pl_item.outFrame)

    def getFps():
        return fps

    def getInOut():
        return inOut

    removeFrameInfo()
    pc.headsUpDisplay(__hud_frame_1__, lfs='large', label='FPS:', section=6, block=pc.headsUpDisplay(nfb=6), blockSize='medium', dfs='large', command=getFps)
    pc.headsUpDisplay(__hud_frame_2__, lfs='large', label='IN OUT:', section=6, block=pc.headsUpDisplay(nfb=6), blockSize='medium', dfs='large', command=getInOut)
    __camera_name__ = pc.optionVar(q='cameraNamesVisibility')
    __current_frame__ = pc.optionVar(q='currentFrameVisibility')
    __focal_length__ = pc.optionVar(q='focalLengthVisibility')
    pc.Mel.eval('setCurrentFrameVisibility(1)')
    pc.headsUpDisplay('HUDCurrentFrame', e=True, lfs='large', dfs='large', bs='medium')
    pc.Mel.eval('setFocalLengthVisibility(1)')
    pc.headsUpDisplay('HUDFocalLength', e=True, lfs='large', dfs='large', bs='medium')
    pc.Mel.eval('setCameraNamesVisibility(1)')
    pc.headsUpDisplay('HUDCameraNames', e=True, lfs='large', dfs='large', bs='medium')


def removeFrameInfo(all=False):
    if pc.headsUpDisplay(__hud_frame_1__, exists=True):
        pc.headsUpDisplay(__hud_frame_1__, rem=True)
    if pc.headsUpDisplay(__hud_frame_2__, exists=True):
        pc.headsUpDisplay(__hud_frame_2__, rem=True)
    if all:
        pc.Mel.eval('setCurrentFrameVisibility(0)')
        pc.Mel.eval('setFocalLengthVisibility(0)')
        pc.Mel.eval('setCameraNamesVisibility(0)')


def restoreFrameInfo():
    if __camera_name__:
        pc.Mel.eval('setCameraNamesVisibility(1)')
    if __current_frame__:
        pc.Mel.eval('setCurrentFrameVisibility(1)')
    if __focal_length__:
        pc.Mel.eval('setFocalLengthVisibility(1)')


def turnResolutionGateOn(camera):
    global __resolutionGateMask__
    global __resolutionGate__
    global __safeAction__
    global __safeTitle__
    oscan = 1.4
    if not pc.camera(camera, q=True, displayResolution=True):
        __resolutionGate__ = False
        pc.camera(camera, e=True, displayResolution=True, overscan=oscan)
    if pc.camera(camera, q=True, displaySafeAction=True):
        __safeAction__ = False
        pc.camera(camera, e=True, displaySafeAction=False, overscan=oscan)
    if pc.camera(camera, q=True, displaySafeTitle=True):
        __safeTitle__ = False
        pc.camera(camera, e=True, displaySafeTitle=False, overscan=oscan)
    if not pc.camera(camera, q=True, dgm=True):
        __resolutionGateMask__ = False
        pc.camera(camera, e=True, dgm=True, overscan=oscan)


def turnResolutionGateOff(camera):
    global __resolutionGate__
    global __safeAction__
    global __safeTitle__
    if not __resolutionGate__:
        pc.camera(camera, e=True, displayResolution=False, overscan=1.0)
        __resolutionGate__ = True
    if not __safeAction__:
        pc.camera(camera, e=True, displaySafeAction=True, overscan=1.0)
        __safeAction__ = True
    if not __safeTitle__:
        pc.camera(camera, e=True, displaySafeTitle=True, overscan=1.0)
        __safeTitle__ = True
    if not __resolutionGateMask__:
        pc.camera(camera, e=True, dgm=False, overscan=1.0)


def turnResolutionGateOffPer(camera):
    pc.camera(camera, e=True, displayResolution=False, overscan=1.0)
    pc.camera(camera, e=True, displaySafeAction=False, overscan=1.0)
    pc.camera(camera, e=True, displaySafeTitle=False, overscan=1.0)
    pc.camera(camera, e=True, dgm=False, overscan=1.0)


def hideShowCurves(flag):
    sel = pc.ls(sl=True)
    try:
        if flag:
            pc.select(pc.ls(type=pc.nt.NurbsCurve))
            pc.Mel.eval('HideSelectedObjects')
        else:
            pc.select(pc.ls(type=pc.nt.NurbsCurve))
            pc.showHidden(b=True)
    except:
        pass

    pc.select(sel)


def getAudioNode():
    nodes = pc.ls(type=['audio'])
    if nodes:
        return nodes
    return []


def setOriginalCamera():
    global __original_camera__
    __original_camera__ = pc.lookThru(q=True)


def restoreOriginalCamera():
    global __original_camera__
    pc.lookThru(__original_camera__)
    __original_camera__ = None
    return


def setOriginalFrame():
    global __original_frame__
    __original_frame__ = pc.currentTime(q=True)


def restoreOriginalFrame():
    global __original_frame__
    pc.currentTime(__original_frame__)
    __original_frame__ = None
    return


def setSelection():
    global __selection__
    __selection__ = pc.ls(sl=True)


def restoreSelection():
    global __selection__
    pc.select(__selection__)
    __selection__ = None
    return


def getObjects():
    objSets = []
    for _set in pc.ls(type=pc.nt.ObjectSet):
        if 'geo_set' in str(_set).lower():
            objSets.append(_set.name())

    return objSets


def enableStretchMesh():
    global __stretchMeshEnvelope__
    for node in pc.ls(type='stretchMesh'):
        __stretchMeshEnvelope__[node] = node.envelope.get()
        node.envelope.set(1.0)


def restoreStretchMesh():
    for node in pc.ls(type='stretchMesh'):
        env = __stretchMeshEnvelope__.get(node)
        if env is not None:
            node.envelope.set(env)

    return


def disableStretchMesh():
    for node in pc.ls(type='stretchMesh'):
        __stretchMeshEnvelope__[node] = node.envelope.get()
        node.envelope.set(0.0)
# okay decompiling exportutils.pyc
