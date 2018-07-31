# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\shotplaylist.py
# Compiled at: 2017-11-08 17:37:11
from . import shotactions as actions
import pymel.core as pc, re, json
from collections import OrderedDict

class Playlist(object):

    def __new__(cls, code=''):
        if not isinstance(code, (str, unicode)):
            raise TypeError, 'code must be string or unicode'
        code = re.sub('[^a-z]', '', code.lower())
        if not plu.__playlistinstances__.get(code):
            plu.__playlistinstances__[code] = object.__new__(cls, code)
        else:
            plu.__playlistinstances__[code].sync()
        return plu.__playlistinstances__[code]

    def __init__(self, code='', populate=True):
        self._code = code
        self.actionsOrder = ['PlayblastExport', 'CacheExport']
        if populate:
            self.populate()

    def getCode(self):
        return self._code

    code = property(getCode)

    def populate(self):
        attrs = plu.getSceneAttrs()
        for a in attrs:
            PlaylistItem(a, readFromScene=True, saveToScene=False)

    def __itemBelongs(self, item):
        if not self._code or self._code in item.__playlistcodes__:
            return True
        return False

    def __addCodeToItem(self, item):
        if self._code and not self.__itemBelongs():
            item.__playlistcodes__.append(self._code)

    def __removeCodeFromItem(self, item):
        if self._code and self.__itemBelongs():
            item.__playlistcodes__.remove(self._code)

    def sync(self, deleteBadItems=False):
        for item in plu.__iteminstances__.values():
            if self.__itemBelongs(item):
                try:
                    item.readFromScene()
                except pc.MayaNodeError:
                    if deleteBadItems:
                        item.__remove__()

    def store(self, removeBadItems=True):
        for item in plu.__iteminstances__.values():
            if self.__itemBelongs(item):
                try:
                    item.saveToScene()
                except pc.MayaNodeError:
                    if removeBadItems:
                        item.__remove__()

    def addItem(self, item):
        self.__addCodeToItem(item)

    def addNewItem(self, camera):
        newItem = PlaylistItem(plu.createNewAttr(camera))
        self.addItem(newItem)
        return newItem

    def removeItem(self, item):
        if not self._code:
            item.__remove__()
        else:
            self.__removeCodeFromItem(item)

    def getItems(self, name=''):
        items = []
        for item in plu.__iteminstances__.values():
            if self.__itemBelongs(item):
                items.append(item)

        return items

    def performActions(self, **kwargs):
        allActions = []
        for item in self.getItems():
            if item.selected:
                allActions.extend([ action for action in item.actions.getActions() if action.enabled ])

        yield len(allActions)
        for actiontype in self.actionsOrder:
            for action in allActions:
                try:
                    if action.__class__.__name__ == actiontype:
                        action.perform(**kwargs)
                        yield action
                except Exception as ex:
                    yield [
                     action.plItem, ex]


class PlaylistItem(object):

    def __new__(cls, attr, *args, **kwargs):
        if not isinstance(attr, pc.Attribute):
            raise TypeError, "'attr' can only be of type pymel.core.Attribute"
        if not attr.objExists() or not attr.node().getShapes(type='camera'):
            raise TypeError, 'Attribute %s does not exist on a camera' % attr.name
        if not plu.__iteminstances__.get(attr):
            plu.__iteminstances__[attr] = object.__new__(cls, attr, *args, **kwargs)
        return plu.__iteminstances__[attr]

    def __init__(self, attr, name='', inframe=None, outframe=None, selected=False, readFromScene=False, saveToScene=True):
        if not isinstance(name, (str, unicode)):
            raise TypeError, "'name' can only be of type str or unicode"
        self.__attr = attr
        self._camera = self.__attr.node()
        self.__data = OrderedDict()
        if readFromScene:
            self.readFromScene()
        if name:
            self.name = name
        if inframe:
            self.inFrame = inframe
        if outframe:
            self.outFrame = outframe
        if not self.name:
            self.name = self.camera.name().split('|')[-1].split(':')[-1]
        if not self.inFrame or not self.outFrame:
            self.autosetInOut()
        if not self.__data.has_key('playlistcodes'):
            self.__data['playlistcodes'] = []
        if not self.actions:
            self.actions = actions.ActionList(self)
        self._selected = selected
        if saveToScene:
            self.saveToScene()

    def selected():
        doc = 'The selected property.'

        def fget(self):
            return self._selected

        def fset(self, value):
            self._selected = value

        def fdel(self):
            del self._selected

        return locals()

    selected = property(**selected())

    def setName(self, name):
        self.__data['name'] = name

    def getName(self):
        return self.__data.get('name')

    name = property(getName, setName)

    def setInFrame(self, inFrame):
        if not isinstance(inFrame, (int, float)):
            return (TypeError, 'In frame must be a number')
        self.__data['inFrame'] = inFrame

    def getInFrame(self):
        return self.__data.get('inFrame')

    inFrame = property(getInFrame, setInFrame)

    def setOutFrame(self, outFrame):
        if not isinstance(outFrame, (int, float)):
            return (TypeError, 'Out frame must be a number')
        self.__data['outFrame'] = outFrame

    def getOutFrame(self):
        return self.__data.get('outFrame')

    outFrame = property(getOutFrame, setOutFrame)

    def getCamera(self):
        return self.__attr.node()

    def setCamera(self, camera, dontSave=False, dontDelete=False):
        if plu.isNodeValid(camera) and camera != self._camera:
            oldattr = self.__attr
            self.__attr = plu.createNewAttr(camera)
            if not dontDelete:
                plu.deleteAttr(oldattr)
            if not dontSave:
                self.saveToScene()
            Playlist.__instance[self.__attr] = self
            del plu.__iteminstances__[oldattr]

    camera = property(getCamera, setCamera)

    def actions():
        doc = 'The actions property.'

        def fget(self):
            return self.__data.get('actions')

        def fset(self, value):
            if isinstance(value, actions.ActionList):
                self.__data['actions'] = value
            else:
                raise (
                 TypeError,
                 'Invalid type: %s Expected' % str(actions.ActionList))

        return locals()

    actions = property(**actions())

    def saveToScene(self):
        if not self.existsInScene():
            if self.nodeExistsInScene():
                self.setCamera(self.__attr.node(), True, True)
            else:
                raise (
                 pc.MayaNodeError,
                 'camera %s does not exist' % self.__attr.node().name())
        datastring = json.dumps(self.__data)
        self.__attr.set(datastring)

    def readFromScene(self):
        if not self.existsInScene():
            raise (
             pc.MayaNodeError,
             'Attribute %s Does not exist in scene' % self.__attr.name())
        datastring = self.__attr.get()
        if datastring:
            self.__data = json.loads(datastring)
            if not self.__data.has_key('actions'):
                self.__data['actions'] = {}
            self.__data['actions'] = actions.ActionList(self)

    def __getPlaylistCodes__(self):
        return self.__data['playlistcodes']

    __playlistcodes__ = property(__getPlaylistCodes__)

    def existsInScene(self):
        return pc.objExists(self.__attr)

    def nodeExistsInScene(self):
        return self.__attr.node().objExists()

    def __remove__(self):
        try:
            plu.__iteminstances__.pop(self.__attr)
        except KeyError:
            pass

        try:
            self.__attr.delete()
        except pc.MayaAttributeError:
            pass

    def autosetInOut(self):
        inframe, outframe = (None, None)
        camera = self._camera
        animCurves = pc.listConnections(camera, scn=True, d=False, s=True)
        if animCurves:
            frames = pc.keyframe(animCurves[0], q=True)
            if frames:
                inframe, outframe = frames[0], frames[-1]
        if not inframe or not outframe:
            if not self.inFrame or not self.outFrame:
                self.inFrame, self.outFrame = (0, 1)
        else:
            self.inFrame, self.outFrame = inframe, outframe
        return


class PlaylistUtils(object):
    attrPattern = re.compile('.*\\.ShotInfo_(\\d{2})')
    __iteminstances__ = OrderedDict()
    __playlistinstances__ = OrderedDict()

    @staticmethod
    def isNodeValid(node):
        if type(node) != pc.nt.Transform or not node.getShapes(type='camera'):
            raise (
             TypeError,
             'node must be a pc.nt.Transform of a camera shape')
        return True

    @staticmethod
    def getSceneAttrs():
        """ Get all shotInfo attributes in the Scene (or current namespace)"""
        attrs = []
        for camera in pc.ls(type='camera'):
            node = camera.firstParent()
            if type(node) == pc.nt.Transform:
                attrs.extend(PlaylistUtils.getAttrs(node))

        return attrs

    @staticmethod
    def getAttrs(node):
        """ Get all ShotInfo attributes from the node """
        attrs = []
        if PlaylistUtils.isNodeValid(node):
            for attr in node.listAttr():
                if PlaylistUtils.attrPattern.match(str(attr)):
                    try:
                        attr.setLocked(False)
                    except:
                        pass

                    attrs.append(attr)

        return attrs

    @staticmethod
    def getSmallestUnusedAttrName(node):
        attrs = PlaylistUtils.getAttrs(node)
        for i in range(100):
            attrName = 'ShotInfo_%02d' % i
            nodeattr = node + '.' + attrName
            if nodeattr not in attrs:
                return attrName

    @staticmethod
    def createNewAttr(node):
        """ :type node: pymel.core.nodetypes.Transform() """
        attrName = PlaylistUtils.getSmallestUnusedAttrName(node)
        pc.addAttr(node, ln=attrName, dt='string', h=True)
        attr = node.attr(attrName)
        return attr

    @staticmethod
    def isAttrValid(attr):
        """ Check if the given attribute is where shot info should be stored.
        It must be a string attribute on a camera transform node
        
        :type attr: pymel.core.Attribute()
        :raises TypeError: if attribute is not the expected type
        """
        if not isinstance(attr, pc.Attribute) or attr.get(type=1) != 'string':
            raise (
             TypeError,
             "'attr' can only be of type pymel.core.Attribute of type                    string")
        if not attr.objExists() or not attr.node().getShapes(type='camera'):
            raise TypeError, 'Attribute %s does not exist on a camera' % attr.name
        if not PlaylistUtils.attrPattern.match(attr):
            raise TypeError, 'Attribute %s does not have the correct name' % attr.name
        return True

    @staticmethod
    def deleteAttr(attr):
        """
        :type attr: pymel.core.Attribute()
        """
        attr.delete()

    @staticmethod
    def getAllPlaylists():
        codes = set()
        masterPlaylist = Playlist()
        playlists = [masterPlaylist]
        for item in masterPlaylist.getItems():
            codes.update(item.__playlistcodes__)

        for c in codes:
            playlists.append(Playlist(c, False))

    @staticmethod
    def getDisplayLayers():
        try:
            return [ pc.PyNode(layer) for layer in pc.layout('LayerEditorDisplayLayerLayout', q=True, childArray=True)
                   ]
        except TypeError:
            pc.warning('Display layers not found in the scene')
            return []

    @staticmethod
    def getDisplayLayersState():
        state = {}
        for layer in PlaylistUtils.getDisplayLayers():
            state[layer] = layer.visibility.get()

        return state

    @staticmethod
    def restoreDisplayLayersState(state):
        for layer, visibility in state.items():
            layer.visibility.set(visibility)


plu = PlaylistUtils
# okay decompiling shotplaylist.pyc
