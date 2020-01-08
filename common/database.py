#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import json
import copy
import shutil
from datetime import datetime, timezone

from common import macro
from common import utils


class Action(object):

    def __init__(self, CGRoot, actionProto, sceneFnames):
        self._CGRoot = CGRoot
        self._fnames = actionProto.copy()
        self._sceneFnames = sceneFnames

    def serialize(self):
        return self._fnames

    # Only called by Scene class
    def renameImage(self, namesMap):
        for idx, fname in enumerate(self._fnames):
            if fname in namesMap:
                self._fnames[idx] = namesMap[fname]

    def indexImage(self, imagePath):
        fname = os.path.basename(imagePath)
        try:
            index = self._fnames.index(fname)
        except ValueError:
            index = None
        return index

    def hasImage(self, imagePath):
        fname = os.path.basename(imagePath)
        return fname in self._fnames

    def getImage(self, index):
        return os.path.join(self._CGRoot,
                            self._fnames[index]) if index < len(self._fnames) else None

    def getFname(self, index):
        return self._fnames[index] if index < len(self._fnames) else None

    def getImageNum(self):
        return len(self._fnames)

    def normalizeImageIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._fnames), 1)
        else:
            return min(max(index, 0), max(len(self._fnames) - 1, 0))


class Pick(Action):

    def clear(self):
        self._fnames.clear()

    def sort(self):

        def bySceneIndex(fname):
            return self._sceneFnames.index(fname)

        self._fnames.sort(key=bySceneIndex)

    def addImage(self, imagePath):
        if self.hasImage(imagePath):
            return
        fname = os.path.basename(imagePath)
        self._fnames.append(fname)
        self.sort()

    def delImage(self, imagePath):
        if not self.hasImage(imagePath):
            return
        fname = os.path.basename(imagePath)
        self._fnames.remove(fname)

    def merge(self, pick):
        self._fnames += pick._fnames


class Face(object):

    def __init__(self, faceProto):
        self.x = faceProto[0]
        self.y = faceProto[1]
        self.z = faceProto[2]
        self.w = faceProto[3]

    def serialize(self):
        return [self.x, self.y, self.z, self.w]

    @property
    def width(self):
        return self.z - self.x + 1

    @property
    def height(self):
        return self.w - self.y + 1


class Scene(object):

    def __init__(self, CGRoot, sceneProto):
        self._CGRoot = CGRoot
        self._sceneFnames = []
        self.load(sceneProto)

    def _updateSceneFnames(self):
        self._sceneFnames.clear()
        for action in self._actions:
            for idx in range(action.getImageNum()):
                self._sceneFnames.append(action.getFname(idx))

    def load(self, sceneProto):
        self._rating = sceneProto['rating']
        self._actions = [
            Action(self._CGRoot, actionProto, self._sceneFnames)
            for actionProto in sceneProto['actions']
        ]
        self._pick = Pick(self._CGRoot, sceneProto['pick'], self._sceneFnames)
        self._love = Pick(self._CGRoot, sceneProto['love'], self._sceneFnames)
        self._faces = [Face(faceProto) for faceProto in sceneProto['faces']]
        self._datetime = datetime.utcfromtimestamp(sceneProto['timestamp'])
        self._updateSceneFnames()

    def serialize(self):
        rating = self.getRating()
        return {
            'rating': rating,
            'actions': [action.serialize() for action in self._actions],
            'pick': self._pick.serialize(),
            'love': self._love.serialize() if rating != 0 else [],
            'faces': [face.serialize() for face in self._faces],
            'timestamp': self._datetime.replace(tzinfo=timezone.utc).timestamp(),
        }

    def normalizeImages(self, imageIndex):
        namesMap = {}
        for action in self._actions:
            for idx in range(action.getImageNum()):
                fname = action.getFname(idx)
                _, extend = os.path.splitext(fname)
                toName = '%04d%s' % (imageIndex, extend)
                imageIndex += 1
                if (fname == toName):
                    continue
                namesMap[fname] = toName
                toImage = os.path.join(self._CGRoot, macro.TMP_NAME, toName)
                os.makedirs(os.path.join(self._CGRoot, macro.TMP_NAME), exist_ok=True)
                shutil.move(action.getImage(idx), toImage)
        for action in self._actions:
            action.renameImage(namesMap)
        self._pick.renameImage(namesMap)
        self._love.renameImage(namesMap)
        self._updateSceneFnames()
        return imageIndex

    def moveActionForward(self, action):
        index = self.normalizeActionIdx(self._actions.index(action) - 1)
        self._actions.remove(action)
        self._actions.insert(index, action)
        self._updateSceneFnames()
        self._pick.sort()
        self._love.sort()

    def moveActionBackward(self, action):
        index = self.normalizeActionIdx(self._actions.index(action) + 1)
        self._actions.remove(action)
        self._actions.insert(index, action)
        self._updateSceneFnames()
        self._pick.sort()
        self._love.sort()

    def delAction(self, action):
        if len(self._actions) == 1:
            return False
        self._actions.remove(action)
        self._updateSceneFnames()
        for idx in range(action.getImageNum()):
            image = action.getImage(idx)
            self._pick.delImage(image)
            self._love.delImage(image)
        return True

    def split(self, action):
        index = self._actions.index(action)
        if index == 0:
            return None
        new_scene = copy.deepcopy(self)
        for action in self._actions[index:]:
            self.delAction(action)
        for action in new_scene._actions[:index]:
            new_scene.delAction(action)
        return new_scene

    def merge(self, scene):
        self._actions += scene._actions
        self._updateSceneFnames()
        self._pick.merge(scene._pick)
        self._love.merge(scene._love)

    def getDatetime(self):
        return self._datetime

    def setDatetime(self, datetime):
        self._datetime = datetime

    def getImages(self):
        return [
            action.getImage(idx) for action in self._actions for idx in range(action.getImageNum())
        ]

    def getFnames(self):
        return self._sceneFnames

    def getAction(self, index):
        return self._actions[index] if index < len(self._actions) else None

    def getActionNum(self):
        return len(self._actions)

    def getPick(self):
        return self._pick

    def getLove(self):
        return self._love

    def getFaces(self):
        return self._faces

    def getRating(self):
        return 0 if self._love.getImageNum() == 0 else self._rating

    def getRawRating(self):
        return self._rating

    def setRating(self, rating):
        self._rating = rating

    def indexImage(self, imagePath):
        aidx, iidx = next(((aidx, action.indexImage(imagePath))
                           for aidx, action in enumerate(self._actions)
                           if action.indexImage(imagePath) is not None),
                          (None, None))
        return aidx, iidx

    def normalizeActionIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._actions), 1)
        else:
            return min(max(index, 0), max(len(self._actions) - 1, 0))


class Database(object):

    def __init__(self, CGRoot):
        self.load(CGRoot)

    def load(self, CGRoot):
        self._CGRoot = None
        self._scenes = []
        databaseFilename = os.path.join(CGRoot, macro.DATABASE_FILE)
        if not os.path.isfile(databaseFilename):
            return
        self._CGRoot = CGRoot
        with open(databaseFilename, 'r') as f:
            proto = json.load(f)
        for sceneProto in proto:
            scene = Scene(CGRoot, sceneProto)
            self._scenes.append(scene)

    def save(self):
        if self._CGRoot is None:
            return
        proto = [scene.serialize() for scene in self._scenes]
        databaseFilename = os.path.join(self._CGRoot, macro.DATABASE_FILE)
        with open(databaseFilename, 'w') as f:
            json.dump(proto, f, indent=2, sort_keys=True)

    def flush(self):
        if self._CGRoot is None:
            return
        # Get image set
        fnames = []
        for scene in self._scenes:
            fnames += scene.getFnames()
        fnames = set(fnames)
        # Delete images not in image set
        for fname in os.listdir(self._CGRoot):
            filename = os.path.join(self._CGRoot, fname)
            if utils.isImage(filename) and fname not in fnames:
                os.remove(filename)
        # Rename images
        imageIndex = 0
        for scene in self._scenes:
            imageIndex = scene.normalizeImages(imageIndex)
        tpath = os.path.join(self._CGRoot, macro.TMP_NAME)
        if os.path.exists(tpath):
            for fname in os.listdir(tpath):
                shutil.move(os.path.join(tpath, fname), self._CGRoot)
            os.rmdir(tpath)
        # Save database
        self.save()

    def getCGName(self):
        return os.path.basename(self._CGRoot)

    def moveSceneForward(self, scene):
        index = self.normalizeSceneIdx(self._scenes.index(scene) - 1)
        self._scenes.remove(scene)
        self._scenes.insert(index, scene)

    def moveSceneBackward(self, scene):
        index = self.normalizeSceneIdx(self._scenes.index(scene) + 1)
        self._scenes.remove(scene)
        self._scenes.insert(index, scene)

    def delScene(self, scene):
        self._scenes.remove(scene)

    def splitScene(self, scene, action):
        new_scene = scene.split(action)
        if new_scene is None:
            return False
        index = self._scenes.index(scene) + 1
        self._scenes.insert(index, new_scene)
        return True

    def mergeScene(self, scene):
        index = self._scenes.index(scene) - 1
        if index < 0:
            return False
        self._scenes[index].merge(scene)
        self._scenes.remove(scene)
        return True

    def getScene(self, index):
        return self._scenes[index] if index < len(self._scenes) else None

    def getSceneNum(self):
        return len(self._scenes)

    def normalizeSceneIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._scenes), 1)
        else:
            return min(max(index, 0), max(len(self._scenes) - 1, 0))
