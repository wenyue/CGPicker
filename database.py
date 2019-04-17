#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import util
import macro
from tools.picker import repickScene


class Action(object):
    def __init__(self, path):
        self._path = path
        self._imagepath = os.path.join(self._path, macro.IMAGE_NAME)
        self._facepath = os.path.join(self._path, macro.FACE_NAME)
        self.load()

    def load(self):
        if os.path.exists(self._imagepath):
            self._fnames = [fname for fname in os.listdir(self._imagepath)]
            self._fnames.sort()
        else:
            self._fnames = []
        self.refresh()

    def refresh(self):
        self._images = [
            os.path.join(self._imagepath, fname) for fname in self._fnames
        ]
        self._faces = [
            os.path.join(self._facepath, fname) for fname in self._fnames
        ]

    def indexImage(self, image):
        fname = os.path.basename(image)
        try:
            index = self._fnames.index(fname)
        except ValueError:
            index = None
        return index

    def getImage(self, index):
        return self._images[index] if index < len(self._images) else None

    def getImages(self):
        return self._images.copy()

    def getFaces(self):
        return self._faces.copy()

    def getFaceByImage(self, imagepath):
        fname = os.path.basename(imagepath)
        parentPath = os.path.dirname(os.path.dirname(imagepath))
        return os.path.join(parentPath, macro.FACE_NAME, fname)

    def normalizeImageIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._images), 1)
        else:
            return min(max(index, 0), max(len(self._images) - 1, 0))


class Pick(Action):
    def clear(self):
        for image in self._images.copy():
            self.delFromPick(image)

    def isInPick(self, imagepath):
        fname = os.path.basename(imagepath)
        return fname in self._fnames

    def addToPick(self, imagepath):
        if self.isInPick(imagepath):
            return
        fname = os.path.basename(imagepath)
        self._fnames.append(fname)
        self._fnames.sort()
        util.copy(imagepath, self._imagepath)
        facepath = self.getFaceByImage(imagepath)
        util.copy(facepath, self._facepath)
        self.refresh()

    def delFromPick(self, imagepath):
        if not self.isInPick(imagepath):
            return
        fname = os.path.basename(imagepath)
        self._fnames.remove(fname)
        imagepath = os.path.join(self._imagepath, fname)
        os.remove(imagepath)
        facepath = os.path.join(self._facepath, fname)
        os.remove(facepath)
        self.refresh()


class Scene(object):
    def __init__(self, path):
        self._path = path
        self.repick()
        self.load()

    def getSceneId(self):
        return int(os.path.basename(self._path))

    def repick(self):
        tmpPath = os.path.join(self._path, macro.TMP_NAME)
        if os.path.exists(tmpPath):
            repickScene(self.getSceneId(), 1, False)

    def load(self):
        self._actions = []
        for dirname in os.listdir(self._path):
            if dirname in (macro.PICK_NAME, macro.LOVE_NAME,
                           macro.BACKUP_NAME):
                continue
            actionPath = os.path.join(self._path, dirname)
            self._actions.append(Action(actionPath))
        pickPath = os.path.join(self._path, macro.PICK_NAME)
        self._pick = Pick(pickPath)
        lovePath = os.path.join(self._path, macro.LOVE_NAME)
        self._love = Pick(lovePath)

    def getAction(self, index):
        return self._actions[index] if index < len(self._actions) else None

    def getActionLen(self):
        return len(self._actions)

    def getPick(self):
        return self._pick

    def getLove(self):
        return self._love

    def indexImage(self, image):
        aidx, iidx = next(((aidx, action.indexImage(image))
                           for aidx, action in enumerate(self._actions)
                           if action.indexImage(image) is not None),
                          (None, None))
        return aidx, iidx

    def normalizeActionIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._actions), 1)
        else:
            return min(max(index, 0), max(len(self._actions) - 1, 0))


class Database(object):
    def __init__(self):
        self._scenes = []
        self.loadDataFromTmp()

    def loadDataFromTmp(self):
        self._scenes = []
        if not os.path.exists(macro.TMP_NAME):
            return
        for dirname in os.listdir(macro.TMP_NAME):
            dirpath = os.path.join(macro.TMP_NAME, dirname)
            scene = Scene(dirpath)
            self._scenes.append(scene)

    def getScene(self, index):
        return self._scenes[index] if index < len(self._scenes) else None

    def normalizeSceneIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._scenes), 1)
        else:
            return min(max(index, 0), max(len(self._scenes) - 1, 0))


data = Database()
