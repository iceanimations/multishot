# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26)
# [MSC v.1500 64 bit (AMD64)]
# Embedded file name:
# C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\src\backend\exceptions.py
# Compiled at: 2017-11-08 17:37:11


class ReplaceError(Exception):

    def __init__(self, msg, errors):
        super(ReplaceError, self).__init__(msg)
        self.errors = errors

# okay decompiling exceptions.pyc
