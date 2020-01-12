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

    def __init__(self, CGRoot, actionProto):
        self._CGRoot = CGRoot
        self._images = actionProto['images'].copy()
        self._pick = actionProto['pick']
        self._love = actionProto['love']

    def serialize(self):
        return {
            'images': self._images,
            'pick': self._pick,
            'love': self._love,
        }

    def getPick(self):
        return os.path.join(self._CGRoot, self._pick)

    def setPick(self, imagePath):
        self._pick = os.path.basename(imagePath)

    def isLove(self):
        return self._love

    def setLove(self, isLove):
        self._love = isLove

    def indexImage(self, imagePath):
        image = os.path.basename(imagePath)
        try:
            index = self._images.index(image)
        except ValueError:
            index = None
        return index

    def hasImage(self, imagePath):
        image = os.path.basename(imagePath)
        return image in self._images

    def getImages(self):
        return [self.getImage(index) for index in range(len(self._images))]

    def getImage(self, index):
        return os.path.join(self._CGRoot,
                            self._images[index]) if index < len(self._images) else None

    def getImageNames(self):
        return self._images

    def getImageName(self, index):
        return self._images[index]

    def getImageNum(self):
        return len(self._images)

    def normalizeImageIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._images), 1)
        else:
            return min(max(index, 0), max(len(self._images) - 1, 0))

    def _renameImage(self, namesMap):
        for idx, image in enumerate(self._images):
            if image in namesMap:
                self._images[idx] = namesMap[image]
        if self._pick in namesMap:
            self._pick = namesMap[self._pick]
        if self._love in namesMap:
            self._love = namesMap[self._love]


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
        self.load(sceneProto)

    def load(self, sceneProto):
        self._rating = sceneProto['rating']
        # rating = -1 indicates that rating is not set in this work life
        if self._rating == 0:
            self._rating = -1
        self._actions = [Action(self._CGRoot, actionProto) for actionProto in sceneProto['actions']]
        self._faces = [Face(faceProto) for faceProto in sceneProto['faces']]
        self._datetime = datetime.utcfromtimestamp(sceneProto['timestamp'])

    def serialize(self):
        return {
            'rating': self.getRating(),
            'actions': [action.serialize() for action in self._actions],
            'faces': [face.serialize() for face in self._faces],
            'timestamp': self._datetime.replace(tzinfo=timezone.utc).timestamp(),
        }

    def moveActionForward(self, action):
        index = self.normalizeActionIdx(self._actions.index(action) - 1)
        self._actions.remove(action)
        self._actions.insert(index, action)

    def moveActionBackward(self, action):
        index = self.normalizeActionIdx(self._actions.index(action) + 1)
        self._actions.remove(action)
        self._actions.insert(index, action)

    def delAction(self, action):
        if len(self._actions) == 1:
            return False
        self._actions.remove(action)
        return True

    def getActions(self):
        return self._actions

    def getAction(self, index):
        return self._actions[index] if index < len(self._actions) else None

    def getActionNum(self):
        return len(self._actions)

    def normalizeActionIdx(self, index, loop=False):
        if loop:
            return index % max(len(self._actions), 1)
        else:
            return min(max(index, 0), max(len(self._actions) - 1, 0))

    def getLoveActions(self):
        loveActions = []
        for action in self._actions:
            if action.isLove():
                loveActions.append(action)
        return loveActions

    def getLoveAction(self, index):
        for action in self._actions:
            if not action.isLove():
                continue
            if index == 0:
                return action
            else:
                index -= 1
        return None

    def getLoveActionNum(self):
        counter = 0
        for action in self._actions:
            if action.isLove():
                counter += 1
        return counter

    def normalizeLoveActionIdx(self, index, loop=False):
        loveNum = self.getLoveActionNum()
        if loop:
            return index % max(loveNum, 1)
        else:
            return min(max(index, 0), max(loveNum - 1, 0))

    def getFaces(self):
        return self._faces

    def getDatetime(self):
        return self._datetime

    def setDatetime(self, datetime):
        self._datetime = datetime

    def getRating(self):
        return max(0, self._rating) if self.getLoveActionNum() != 0 else 0

    def getRawRating(self):
        return self._rating

    def setRating(self, rating):
        if rating >= 0:
            self._rating = rating

    # Only called by database class
    def _normalizeImages(self, imageIndex):
        namesMap = {}
        for action in self._actions:
            for idx in range(action.getImageNum()):
                imageName = action.getImageName(idx)
                _, extend = os.path.splitext(imageName)
                toName = '%04d%s' % (imageIndex, extend)
                imageIndex += 1
                if (imageName == toName):
                    continue
                namesMap[imageName] = toName
                toImage = os.path.join(self._CGRoot, macro.TMP_NAME, toName)
                os.makedirs(os.path.join(self._CGRoot, macro.TMP_NAME), exist_ok=True)
                shutil.move(action.getImage(idx), toImage)
        for action in self._actions:
            action._renameImage(namesMap)
        return imageIndex

    def _split(self, action):
        index = self._actions.index(action)
        if index == 0:
            return None
        new_scene = copy.deepcopy(self)
        for action in self._actions[index:]:
            self.delAction(action)
        for action in new_scene._actions[:index]:
            new_scene.delAction(action)
        return new_scene

    def _merge(self, scene):
        self._actions += scene._actions


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
            for action in scene.getActions():
                fnames += action.getImageNames()
        fnames = set(fnames)
        # Delete images not in image set
        for fname in os.listdir(self._CGRoot):
            filename = os.path.join(self._CGRoot, fname)
            if utils.isImage(filename) and fname not in fnames:
                os.remove(filename)
        # Rename images
        imageIndex = 0
        for scene in self._scenes:
            imageIndex = scene._normalizeImages(imageIndex)
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
        new_scene = scene._split(action)
        if new_scene is None:
            return False
        index = self._scenes.index(scene) + 1
        self._scenes.insert(index, new_scene)
        return True

    def mergeScene(self, scene):
        index = self._scenes.index(scene) - 1
        if index < 0:
            return False
        self._scenes[index]._merge(scene)
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
