#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os
import macro
import util
import random
from functools import reduce 


def loadImage(filename):
	ori_img = Image.open(filename)
	w, h = int(ori_img.width * macro.NORMALIZE_SCALE), int(ori_img.height * macro.NORMALIZE_SCALE)
	img = ori_img.resize((w, h))
	img.filename = filename
	img.ori_img = ori_img
	return img


def calSimilarity(li, ri):
	if li.size != ri.size:
		return 0
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	samePixelNum = sum(1 if lp[i, j] == rp[i, j] else 0 for i in range(w) for j in range(h))
	return float(samePixelNum) / (w * h)


def isSameScene(li, ri):
	return calSimilarity(li, ri) > macro.SAME_SCENE_THRESHOLD


def getDiffRect(li, ri):
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	xmax, xmin, ymax, ymin = 0, w, 0, h
	for i in range(w):
		for j in range(h):
			if lp[i, j] != rp[i, j]:
				xmax, xmin, ymax, ymin = max(xmax, i), min(xmin, i), max(ymax, j), min(ymin, j)
	return xmax, xmin, ymax, ymin


def isSameAction(li, ri):
	if li.size != ri.size:
		return False
	w, h = li.size
	xmax, xmin, ymax, ymin = getDiffRect(li, ri)
	areaWidth = max((xmax - xmin), (ymax - ymin))
	return areaWidth * areaWidth < w * h * (1.0 - macro.SAME_ACTION_THRESHOLD)


def copyImagesToTmp(images):
	for sid, scene in enumerate(images):
		for aid, action in enumerate(scene):
			for img in action:
				util.copy(img.filename,
					os.path.join(macro.TMP_PATH, '%04d/%02d/%s' % (sid, aid, macro.IMAGE_NAME)))


def genFaceToTmp(images):
	for sid, scene in enumerate(images):
		for aid, action in enumerate(scene):
			if len(action) == 1:
				util.copy(action[0].filename,
					os.path.join(macro.TMP_PATH, '%04d/%02d/%s' % (sid, aid, macro.FACE_NAME)))
				continue

			rect = [float('inf'), float('inf'), 0, 0]
			def func(li, ri):
				xmax, xmin, ymax, ymin = getDiffRect(li, ri)
				rect[0] = min(rect[0], xmin)
				rect[1] = min(rect[1], ymin)
				rect[2] = max(rect[2], xmax)
				rect[3] = max(rect[3], ymax)
				return ri
			reduce(func, action)
			rect = [val / macro.NORMALIZE_SCALE for val in rect]
			for img in action:
				facePath = os.path.join(macro.TMP_PATH, '%04d/%02d/%s' % (sid, aid, macro.FACE_NAME))
				os.makedirs(facePath, exist_ok=True)
				basename = os.path.basename(img.filename)
				facePath = os.path.join(facePath, basename)
				face = img.ori_img.crop(rect)
				face.save(facePath)

				
def pickImagesToTmp(images):
	picks = []
	for sid, scene in enumerate(images):
		for action in scene:
			if picks:
				imgs = random.sample(action, min(len(action), macro.SAMPLE_IMAGE_NUM))
				imgs = [(sum(calSimilarity(img, pick) for pick in picks), img) for img in imgs]
				_, pick = min(imgs, key=lambda x: x[0])
			else:
				pick = random.choice(action) if random.randint(0, 1) else action[0]
			util.copy(pick.filename, os.path.join(macro.TMP_PATH, '%04d/%s' % (sid, macro.PICK_NAME)))
			picks.append(pick)


def pickCGToTmp(path):
	util.remove(macro.TMP_PATH)
	images = [os.path.join(path, fname) for fname in os.listdir(path)]
	images = [loadImage(fname) for fname in images if util.isImage(fname)]
	images = util.groupby(isSameScene, images)
	images = [util.groupby(isSameAction, scene) for scene in images]
	copyImagesToTmp(images)
	genFaceToTmp(images)
	pickImagesToTmp(images)
