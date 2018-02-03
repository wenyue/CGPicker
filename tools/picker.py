#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os
import macro
import util
import random
import math
from functools import reduce


def loadImage(filename):
	img = Image.open(filename)
	w, h = int(img.width * macro.NORMALIZE_SCALE), int(img.height * macro.NORMALIZE_SCALE)
	img = img.resize((w, h), Image.BILINEAR)
	img.filename = filename
	return img


def isSamePixel(lp, rp):
	return max(abs(x[0] - x[1]) for x in zip(lp, rp)) < 16


def calSimilarity(li, ri):
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	samePixelNum = sum(
		1 if isSamePixel(lp[i, j], rp[i, j]) else 0 for i in range(w) for j in range(h))
	return float(samePixelNum) / (w * h)


def isSameScene(li, ri):
	if li.size != ri.size:
		return False
	return calSimilarity(li, ri) > macro.SAME_SCENE_THRESHOLD


def getDiffRect(li, ri):
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	xmax, xmin, ymax, ymin = 0, w, 0, h
	for i in range(w):
		for j in range(h):
			if not isSamePixel(lp[i, j], rp[i, j]):
				xmax, xmin, ymax, ymin = max(xmax, i), min(xmin, i), max(ymax, j), min(
					ymin, j)
	return [xmin, ymin, xmax, ymax]


def calFaceRects(scene):
	rects = []

	def genRects(li, ri):
		rects.append(getDiffRect(li, ri))
		return ri

	reduce(genRects, scene)
	return rects


def groupbyFaceArea(scene):
	w, h = scene[0].size
	if len(scene) == 1:
		return [scene], [0, 0, w, h]
	rects = calFaceRects(scene)
	maxWidth = int(math.sqrt(w * h * (1.0 - macro.SAME_ACTION_THRESHOLD)))
	nums = []
	for rect in rects:
		extend = int(macro.SAME_ACTION_EXTEND * macro.NORMALIZE_SCALE)
		width = min(max(rect[2] - rect[0], rect[3] - rect[1]) + extend, maxWidth)
		sx = min(max((rect[0] + rect[2] - width) // 2, 0), w - width)
		sy = min(max((rect[1] + rect[3] - width) // 2, 0), h - width)
		area = [sx, sy, sx + width, sy + width]
		nums.append((sum(1 if area[0] <= v[0] and area[1] <= v[1] and area[2] >= v[2] and
						 area[3] >= v[3] else 0 for v in rects), -width, area))
	_, _, area = max(nums)

	def isSameAction(li, ri):
		idx = scene.index(li)
		v = rects[idx]
		return area[0] <= v[0] and area[1] <= v[1] and area[2] >= v[2] and area[3] >= v[3]

	scene = util.groupby(isSameAction, scene)
	return scene, area


def copyImagesToTmp(images):
	for sid, v in enumerate(images):
		scene = v[0]
		for aid, action in enumerate(scene):
			for img in action:
				util.copy(img.filename,
						  os.path.join(macro.TMP_PATH,
									   '%04d/%02d/%s' % (sid, aid, macro.IMAGE_NAME)))


def genFaceToTmp(images):
	for sid, v in enumerate(images):
		scene, area = v
		area = [val / macro.NORMALIZE_SCALE for val in area]
		for aid, action in enumerate(scene):
			for img in action:
				facePath = os.path.join(macro.TMP_PATH,
										'%04d/%02d/%s' % (sid, aid, macro.FACE_NAME))
				os.makedirs(facePath, exist_ok=True)
				basename = os.path.basename(img.filename)
				facePath = os.path.join(facePath, basename)
				face = Image.open(img.filename).crop(area)
				face.save(facePath)


def pickImagesToTmp(images):
	for sid, v in enumerate(images):
		scene = v[0]
		picks = []
		for action in scene:
			if picks:
				imgs = random.sample(action, min(len(action), macro.SAMPLE_IMAGE_NUM))
				cpicks = picks[-macro.COMPARE_IMAGE_NUM:]
				values = [
					sum(calSimilarity(img, pick) for pick in cpicks) for img in imgs
				]
				_, pick = min(zip(values, imgs), key=lambda x: x[0])
			else:
				pick = random.choice(action) if random.randint(0, 1) else action[0]
			util.copy(pick.filename,
					  os.path.join(macro.TMP_PATH, '%04d/%s' % (sid, macro.PICK_NAME)))
			picks.append(pick)


def pickCGToTmp(path):
	util.remove(macro.TMP_PATH)
	images = [os.path.join(path, fname) for fname in os.listdir(path)]
	images = [loadImage(fname) for fname in images if util.isImage(fname)]
	images = util.groupby(isSameScene, images)
	images = [groupbyFaceArea(scene) for scene in images]
	copyImagesToTmp(images)
	genFaceToTmp(images)
	pickImagesToTmp(images)
