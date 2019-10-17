# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26)
# [MSC v.1500 64 bit (AMD64)]
# Embedded file name:
# C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\shotactions.py
# Compiled at: 2017-11-08 17:37:11

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import json
import os.path as osp
dir_path = osp.dirname(__file__)


class ActionList(OrderedDict):
    """A list of Actions that can be performed on a
    :class:`shotplaylist.PlaylistItem` or :class:`playlist.Playlist` """

    def __init__(self, item, *args, **kwargs):
        """Create an Action List"""
        super(ActionList, self).__init__(*args, **kwargs)
        self._item = item
        actionsubs = Action.inheritors()
        if not item.actions:
            return
        for ak in item.actions.keys():
            cls = actionsubs.get(ak)
            if cls:
                self[ak] = cls(item.actions[ak])
                self[ak].__item__ = item
            else:
                self[ak] = item.actions[ak]

    def getActions(self):
        actions = []
        for ak in self.keys():
            if isinstance(self[ak], Action):
                actions.append(self[ak])

        return actions

    def perform(self, **kwargs):
        for action in self.getActions():
            action.perform(**kwargs)

    def add(self, action):
        if not isinstance(action, Action):
            raise TypeError('only Actions can be added')
        classname = action.__class__.__name__
        action._item = self._item
        self[classname] = action
        return action

    def remove(self, action):
        key = action
        if isinstance(action, Action):
            key = action.__class__.__name__
        if key in self:
            del self[key]


class Action(OrderedDict):
    __metaclass__ = ABCMeta
    _conf = None
    __item__ = None

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        if self.enabled is None:
            self.enabled = True
        self.tempPath = osp.join(osp.expanduser('~'), 'multiShotExport')
        return

    def getEnabled(self):
        return self.get('enabled')

    def setEnabled(self, val):
        self['enabled'] = val

    enabled = property(getEnabled, setEnabled)

    @abstractmethod
    def perform(self):
        pass

    def _item():
        doc = 'The _item property.'

        def fget(self):
            return self.__item__

        def fset(self, value):
            self.__item__ = value

        return locals()

    plItem = property(**_item())
    _item = property(**_item())

    def read_conf(self, confname=''):
        if not confname:
            confname = self.__class__.__name__
        with open(osp.join(dir_path, confname)) as (conf):
            self._conf = json.load(conf)

    def write_conf(self, confname=''):
        if not confname:
            confname = self.__class__.__name__
        with open(osp.join(dir_path, confname), 'w+') as (conf):
            json.dump(self._conf, conf)

    def get_conf(self):
        return self._conf

    conf = property(get_conf)

    @classmethod
    def inheritors(klass):
        subclasses = dict()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses.values():
                    scname = child.__name__
                    subclasses[scname] = child
                    work.append(child)

        return subclasses

    @classmethod
    def performOnPlaylist(cls, pl):
        for item in pl.get_items():
            action = cls.getActionsFromList(item.actions)
            if action and action.enabled:
                cls.getActionFromList(item.actions).perform()
                yield True
            else:
                yield False

    @classmethod
    def getNumActionsFromPlaylist(cls, pl):
        num = 0
        for item in pl.get_items():
            action = cls.getActionFromList(item.actions)
            if action and action.enabled:
                num += 1

        return num

    @classmethod
    def getActionFromList(cls, actionlist, forceCreate=True):
        if not isinstance(actionlist, ActionList):
            raise TypeError('Only Action lists can be queried')
        action = actionlist.get(cls.__name__)
        if not action and forceCreate:
            action = cls()
        return action
# okay decompiling shotactions.pyc
