#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import util
from macro import TMP_PATH, PICK_NAME, IMAGE_NAME, FACE_NAME


class Action(object):

	def __init__(self, path):
		self._path = path
		self._images = []
		self._faces = []
		self._load()

	def _load(self):
		imagepath = os.path.join(self._path, IMAGE_NAME)
		for filename in os.listdir(imagepath):
			filepath = os.path.join(imagepath, filename)
			self._images.append(filepath)

		facePath = os.path.join(self._path, FACE_NAME)
		for filename in os.listdir(facePath):
			filepath = os.path.join(facePath, filename)
			self._faces.append(filepath)

	def indexImage(self, image):
		for index, img in enumerate(self._images):
			if image == os.path.basename(img):
				return index

	def getImage(self, index):
		return self._images[index] if index < len(self._images) else None

	def getImages(self):
		return self._images.copy()

	def getFaces(self):
		return self._faces.copy()

	def normalizeImageIdx(self, index, loop=False):
		if loop:
			return index % max(len(self._images), 1)
		else:
			return min(max(index, 0), max(len(self._images) - 1, 0))


class Pick(object):

	def __init__(self, path):
		self._path = path
		self._images = []
		self._load()

	def _load(self):
		for filename in os.listdir(self._path):
			self._images.append(filename)

	def clear(self):
		for image in self._images.copy():
			self.delFromPick(image)

	def findNearestImage(self, imagepath, offset):
		if offset not in (-1, 1) or not self._images:
			return None, None
		image = os.path.basename(imagepath)
		if image in self._images:
			index = self._images.index(image)
			index = self.normalizeImageIdx(index + offset, loop=True)
		else:
			index = next((index for index, img in enumerate(self._images) if image < img), 0)
			index = index - 1 if offset == -1 else index
		return index, self._images[index]

	def isInPick(self, imagepath):
		image = os.path.basename(imagepath)
		return image in self._images

	def addToPick(self, imagepath):
		image = os.path.basename(imagepath)
		if image in self._images:
			return
		self._images.append(image)
		self._images.sort()
		util.copy(imagepath, self._path)

	def delFromPick(self, imagepath):
		image = os.path.basename(imagepath)
		if image not in self._images:
			return
		self._images.remove(image)
		pickpath = os.path.join(self._path, image)
		os.remove(pickpath)

	def getImageLen(self):
		return len(self._images)

	def normalizeImageIdx(self, index, loop=False):
		if loop:
			return index % max(len(self._images), 1)
		else:
			return min(max(index, 0), max(len(self._images) - 1, 0))


class Scene(object):

	def __init__(self, path):
		self._path = path
		self._actions = []
		self._pick = None
		self._load()

	def _load(self):
		for dirname in os.listdir(self._path):
			if dirname == PICK_NAME:
				continue
			actionPath = os.path.join(self._path, dirname)
			self._actions.append(Action(actionPath))
		pickPath = os.path.join(self._path, PICK_NAME)
		self._pick = Pick(pickPath)

	def getAction(self, index):
		return self._actions[index] if index < len(self._actions) else None

	def getActionLen(self):
		return len(self._actions)

	def getPick(self):
		return self._pick

	def indexImage(self, image):
		aidx, iidx = next(((aidx, action.indexImage(image))
						   for aidx, action in enumerate(self._actions)
						   if action.indexImage(image) is not None), (None, None))
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
		if not os.path.exists(TMP_PATH):
			return
		for dirname in os.listdir(TMP_PATH):
			dirpath = os.path.join(TMP_PATH, dirname)
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
