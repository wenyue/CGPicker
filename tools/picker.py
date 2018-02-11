#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os
import random
import math
from functools import reduce

if __name__ == '__main__':
	import sys
	sys.path.append('../')

import util # noqa
import macro # noqa


def loadImage(filename):
	img = Image.open(filename)
	w, h = int(img.width * macro.NORMALIZE_SCALE), int(img.height * macro.NORMALIZE_SCALE)
	img = img.resize((w, h), Image.BILINEAR)
	img = img.convert('L')
	img.filename = filename
	return img


def isSamePixel(lp, rp, i, j):
	return abs(lp[i, j] - rp[i, j]) < 1


def calSimilarity(li, ri):
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	samePixelNum = sum(
		1 if isSamePixel(lp, rp, i, j) else 0 for i in range(w) for j in range(h))
	return float(samePixelNum) / (w * h)


def isSameScene(li, ri):
	if li.size != ri.size:
		return False
	return calSimilarity(li, ri) > macro.SAME_SCENE_THRESHOLD


def calHit(li, ri, hits):
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	for i in range(w):
		for j in range(h):
			if not isSamePixel(lp, rp, i, j):
				hits[i][j] += 1


def calHitNum(hits, i, j, radius):
	ti = i - radius - 1
	tj = j - radius - 1
	bi = min(len(hits[0]) - 1, i + radius)
	bj = min(len(hits) - 1, j + radius)
	value = hits[bi][bj]
	if ti >= 0:
		value -= hits[ti][bj]
	if tj >= 0:
		value -= hits[bi][tj]
	if ti >= 0 and tj >= 0:
		value += hits[ti][tj]
	return value


def calFaceRegions(scene): # noqa
	w, h = scene[0].size
	hits = [[0] * w for _ in range(h)]
	reduce(lambda li, ri: calHit(li, ri, hits) and ri, scene)
	for i in range(w):
		for j in range(h):
			if i > 0:
				hits[i][j] += hits[i - 1][j]
			if j > 0:
				hits[i][j] += hits[i][j - 1]
			if i > 0 and j > 0:
				hits[i][j] -= hits[i - 1][j - 1]
	centers = [(calHitNum(hits, i, j, macro.FACE_BRUSH_RADIUS), i, j)
			   for i in range(w)
			   for j in range(h)]
	centers.sort(key=lambda k: -k[0])

	maxRadius = int(math.sqrt(w * h * (1 - macro.SAME_ACTION_THRESHOLD)))
	faces = []
	for _, i, j in centers:
		for x, y, radius in faces:
			if min(abs(i - x), abs(i - y)) <= radius + macro.FACE_BRUSH_RADIUS:
				break
		else:
			radius = maxRadius
			for r in range(macro.FACE_BRUSH_RADIUS, maxRadius):
				if calHitNum(hits, i, j, r) == calHitNum(hits, i, j, r + 1):
					radius = r
					break
			faces.append((i, j, radius))
	return faces


def isSameAction(li, ri, faces):
	w, h = li.size
	lp = li.load()
	rp = ri.load()
	for i in range(w):
		for j in range(h):
			if not isSamePixel(lp, rp, i, j):
				for x, y, radius in faces:
					if min(abs(i - x), abs(j - y)) <= radius:
						break
				else:
					return False
	return True


def copyImagesToTmp(scenes):
	for sid, scene in enumerate(scenes):
		for aid, action in enumerate(scene):
			for img in action:
				util.copy(img.filename,
						  os.path.join(macro.TMP_PATH,
									   '%04d/%02d/%s' % (sid, aid, macro.IMAGE_NAME)))


def genFaceToTmp(scenes, faces):
	for sid, v in enumerate(zip(scenes, faces)):
		scene, faces = v
		facesWidth = int(sum(radius for _, _, radius in faces) / macro.NORMALIZE_SCALE)
		facesHight = int(max(radius for _, _, radius in faces) / macro.NORMALIZE_SCALE)
		for aid, action in enumerate(scene):
			for img in action:
				facePath = os.path.join(macro.TMP_PATH,
										'%04d/%02d/%s' % (sid, aid, macro.FACE_NAME))
				os.makedirs(facePath, exist_ok=True)
				basename = os.path.basename(img.filename)
				facePath = os.path.join(facePath, basename)
				image = Image.open(img.filename)
				faceImg = Image.new('RGB', (facesWidth, facesHight))
				tw = 0
				for face in faces:
					x, y, radius = face
					region = [x - radius, y - radius, x + radius, y + radius]
					region = [int(val / macro.NORMALIZE_SCALE) for val in region]
					faceImg.paste(image.crop(region), (tw, 0))
					tw += radius
				faceImg.save(facePath)


def pickImagesToTmp(scenes):
	for sid, scene in enumerate(scenes):
		picks = []
		for action in scene:
			if picks:
				imgs = random.sample(action, min(len(action), macro.PICK_SAMPLE_NUM))
				cpicks = picks[-macro.PICK_COMPARE_NUM:]
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
	scenes = util.groupby(isSameScene, images)
	faces = [calFaceRegions(scene) for scene in scenes]
	scenes = [util.groupby(lambda li, ri: isSameAction(li, ri, face), scene) for face, scene in zip(faces, scenes)]
	copyImagesToTmp(scenes)
	genFaceToTmp(scenes, faces)
	pickImagesToTmp(scenes)


if __name__ == '__main__':
	pickCGToTmp('test')
