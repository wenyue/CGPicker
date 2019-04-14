#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os
import random
import math
import copy
from functools import reduce
import shutil

if __name__ == '__main__':
    import sys
    sys.path.append('../')

import util  # noqa
import macro  # noqa


def debugData(data):
    w, h = len(data), len(data[0])
    maxValue = max(data[i][j] for i in range(w) for j in range(h))
    if maxValue == 0:
        return
    img = Image.new('RGB', (w, h))
    pixel = img.load()
    for i in range(w):
        for j in range(h):
            v = 255 - int(data[i][j] / maxValue * 255)
            pixel[i, j] = (v, v, v)
    img.show()


def loadImage(filename):
    img = Image.open(filename)
    w, h = int(img.width * macro.NORMALIZE_SCALE), int(
        img.height * macro.NORMALIZE_SCALE)
    img = img.resize((w, h), Image.BILINEAR)
    img = img.convert('L')
    img.filename = filename
    return img


def isSamePixel(lp, rp, i, j):
    return abs(lp[i, j] - rp[i, j]) < macro.SCENE_ABERRATION_ENDURANCE


def calSimilarity(li, ri):
    w, h = li.size
    lp = li.load()
    rp = ri.load()
    samePixelNum = sum(1 if isSamePixel(lp, rp, i, j) else 0
                       for i in range(w) for j in range(h))
    return samePixelNum / (w * h)


def isSameScene(li, ri):
    if li.size != ri.size:
        return False
    return calSimilarity(li, ri) > macro.SCENE_ABERRATION_THRESHOLD


def calHit(hits, li, ri):
    factor = macro.FACE_ABERRATION_FACTOR
    w, h = li.size
    lp = li.load()
    rp = ri.load()
    totDiff = sum(
        pow(abs(lp[i, j] - rp[i, j]), factor) for i in range(w)
        for j in range(h))
    if totDiff == 0:
        return
    for i in range(w):
        for j in range(h):
            hits[i][j] += pow(abs(lp[i, j] - rp[i, j]), factor) / totDiff


def calHits(scene):
    w, h = scene[0].size
    hits = [[0] * h for _ in range(w)]
    reduce(lambda li, ri: calHit(hits, li, ri) or ri, scene)
    hits = [[pow(value, macro.FACE_REFORCE_FACTOR) for value in col]
            for col in hits]
    return hits


def calRegion(regions, hits, li, ri):
    w, h = li.size
    lp = li.load()
    rp = ri.load()
    left, right, top, bottom = w, 0, h, 0
    for i in range(w):
        for j in range(h):
            if hits[i][j] > 0 and not isSamePixel(lp, rp, i, j):
                left = min(left, i)
                right = max(right, i)
                top = min(top, j)
                bottom = max(bottom, j)
    x = (left + right) // 2
    y = (top + bottom) // 2
    radius = max(right - left + 1, bottom - top + 1)
    shape = abs((right - left) - (bottom - top)) / radius
    radius = int(radius * macro.FACE_EXTEND_FACTOR // 2)
    maxRadius = int(math.sqrt(w * h * macro.FACE_MAX_SIZE) // 2)
    if 0 < radius <= maxRadius:
        regions.append((x, y, radius, shape))


def convertRegion(region, w, h):
    x, y, radius, _ = region
    left = max(x - radius, 0)
    right = min(x + radius, w - 1)
    top = max(y - radius, 0)
    bottom = min(y + radius, h - 1)
    return left, right, top, bottom


def clearHits(hits, region, w, h):
    left, right, top, bottom = convertRegion(region, w, h)
    for i in range(left, right + 1):
        for j in range(top, bottom + 1):
            hits[i][j] = 0


def calTotalHits(hits):
    w = len(hits)
    h = len(hits[0])
    totalHits = copy.deepcopy(hits)
    for i in range(w):
        for j in range(h):
            if i > 0:
                totalHits[i][j] += totalHits[i - 1][j]
            if j > 0:
                totalHits[i][j] += totalHits[i][j - 1]
            if i > 0 and j > 0:
                totalHits[i][j] -= totalHits[i - 1][j - 1]
    return totalHits


def calHitValue(totalHits, x, y, radius):
    left = x - radius - 1
    top = y - radius - 1
    right = min(len(totalHits) - 1, x + radius)
    bottom = min(len(totalHits[0]) - 1, y + radius)
    value = totalHits[right][bottom]
    if left >= 0:
        value -= totalHits[left][bottom]
    if top >= 0:
        value -= totalHits[right][top]
    if left >= 0 and top >= 0:
        value += totalHits[left][top]
    return value


def calFaceRegions(scene, faceNum=1, debug=False):  # noqa
    hits = calHits(scene)

    faces = []
    w, h = scene[0].size
    for _ in range(faceNum):
        if debug:
            debugData(hits)

        center = (0, (w // 2, h // 2, max(w, h) // 2, -1))
        totalHits = calTotalHits(hits)
        if faces:
            bestRadius = faces[0][2]
        else:
            bestRadius = int(math.sqrt(w * h * macro.FACE_BEST_SIZE) // 2)

        regions = []
        reduce(lambda li, ri: calRegion(regions, hits, li, ri) or ri, scene)
        for region in regions:
            x, y, radius, shape = region
            faceSize = max(radius, bestRadius) / min(radius, bestRadius)
            factor = faceSize * macro.FACE_SIZE_FACTOR + shape * macro.FACE_SHAPE_FACTOR
            value = calHitValue(totalHits, x, y, radius) / factor
            center = max(center, (value, region))

        if (faceNum > 1):
            maxRadius = int(math.sqrt(w * h * macro.FACE_MAX_SIZE) // 2)
            for scale in macro.FACE_DETECT_FACTORS:
                radius = max(int(bestRadius * scale), 1)
                if radius > maxRadius:
                    break
                faceSize = max(radius, bestRadius) / min(radius, bestRadius)
                shape = 0.5
                factor = faceSize * macro.FACE_SIZE_FACTOR + shape * macro.FACE_SHAPE_FACTOR
                for x in range(w):
                    for y in range(h):
                        value = calHitValue(totalHits, x, y, radius) / factor
                        center = max(center, (value, (x, y, radius, shape)))

        _, region = center
        faces.append(region)
        clearHits(hits, region, w, h)

    return faces


def isSameAction(li, ri, faces):
    w, h = li.size
    lp = li.load()
    rp = ri.load()
    count = 0
    for i in range(w):
        for j in range(h):
            if not isSamePixel(lp, rp, i, j):
                for x, y, radius, shape in faces:
                    if max(abs(i - x), abs(j - y)) <= radius and shape >= 0:
                        break
                else:
                    count += 1
                    if count >= 10:
                        return False
    return True


def copyImagesToTmp(sid, actions):
    for aid, action in enumerate(actions):
        for img in action:
            imagePath = os.path.join(macro.TMP_NAME, '%04d/%02d/%s' %
                                     (sid, aid, macro.IMAGE_NAME))
            img.imagename = os.path.join(imagePath,
                                         os.path.basename(img.filename))
            util.copy(img.filename, imagePath)


def genFaceToTmp(sid, actions, faces):
    w, h = actions[0][0].size
    faces = [convertRegion(face, w, h) for face in faces]
    for idx, face in enumerate(faces.copy()):
        faces[idx] = tuple(int(val / macro.NORMALIZE_SCALE) for val in face)
    totalW = 0
    maxH = 0
    offsets = []
    for face in faces:
        left, right, top, bottom = face
        width = right - left + 1
        height = bottom - top + 1
        offsets.append((totalW, height))
        totalW += width
        maxH = max(maxH, height)
    for aid, action in enumerate(actions):
        for img in action:
            facePath = os.path.join(macro.TMP_NAME, '%04d/%02d/%s' %
                                    (sid, aid, macro.FACE_NAME))
            os.makedirs(facePath, exist_ok=True)
            basename = os.path.basename(img.filename)
            facename = os.path.join(facePath, basename)
            img.facename = facename
            image = Image.open(img.filename)
            faceImg = Image.new('RGB', (totalW, maxH), (255, 255, 255))
            for offset, face in zip(offsets, faces):
                left, right, top, bottom = face
                w, h = offset
                faceImg.paste(
                    image.crop((left, top, right, bottom)), (w,
                                                             (maxH - h) // 2))
                faceImg.save(facename)


def pickImagesToTmp(sid, actions):
    picks = []
    for action in actions:
        if picks:
            imgs = random.sample(action, min(
                len(action), macro.PICK_SAMPLE_NUM))
            cpicks = picks[-macro.PICK_COMPARE_NUM:]
            values = [
                sum(calSimilarity(img, pick) for pick in cpicks)
                for img in imgs
            ]
            _, pick = min(zip(values, imgs), key=lambda x: x[0])
        else:
            pick = random.choice(action) if random.randint(0, 1) else action[0]

        imagePath = os.path.join(macro.TMP_NAME, '%04d/%s/%s' %
                                 (sid, macro.PICK_NAME, macro.IMAGE_NAME))
        util.copy(pick.imagename, imagePath)
        facePath = os.path.join(macro.TMP_NAME, '%04d/%s/%s' %
                                (sid, macro.PICK_NAME, macro.FACE_NAME))
        util.copy(pick.facename, facePath)
        picks.append(pick)


def pickScene(sid, images, faces):
    actions = util.groupby(lambda li, ri: isSameAction(li, ri, faces), images)
    copyImagesToTmp(sid, actions)
    genFaceToTmp(sid, actions, faces)
    pickImagesToTmp(sid, actions)


def pickCGToTmp(path):
    util.remove(macro.TMP_NAME)
    fnames = [fname for fname in os.listdir(path)]
    fnames.sort()
    images = [os.path.join(path, fname) for fname in fnames]
    images = [loadImage(fname) for fname in images if util.isImage(fname)]
    scenes = util.groupby(isSameScene, images)

    yield len(scenes)

    for sid, images in enumerate(scenes):
        faces = calFaceRegions(images)
        pickScene(sid, images, faces)
        yield 'picking: %d/%d' % (sid + 1, len(scenes))


def collectScene(sid):
    scenePath = os.path.join(macro.TMP_NAME, '%04d' % sid)
    tmpPath = os.path.join(scenePath, macro.TMP_NAME)
    if os.path.exists(tmpPath):
        return
    backupPath = os.path.join(scenePath, macro.BACKUP_NAME)
    if os.path.exists(backupPath):
        shutil.copytree(backupPath, tmpPath)
        return
    for action in os.listdir(scenePath):
        actionPath = os.path.join(scenePath, action)
        if action not in (macro.PICK_NAME, macro.LOVE_NAME):
            imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
            for image in os.listdir(imagePath):
                util.copy(os.path.join(imagePath, image), tmpPath)


def clearScene(sid):
    scenePath = os.path.join(macro.TMP_NAME, '%04d' % sid)
    for action in os.listdir(scenePath):
        actionPath = os.path.join(scenePath, action)
        if action not in (macro.TMP_NAME, macro.BACKUP_NAME):
            util.remove(actionPath)


def backupScene(sid):
    scenePath = os.path.join(macro.TMP_NAME, '%04d' % sid)
    backupPath = os.path.join(scenePath, macro.BACKUP_NAME)
    if os.path.exists(backupPath):
        return
    for action in os.listdir(scenePath):
        actionPath = os.path.join(scenePath, action)
        if action not in (macro.PICK_NAME, macro.LOVE_NAME):
            imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
            for image in os.listdir(imagePath):
                util.copy(os.path.join(imagePath, image), backupPath)


def repickScene(sid, faceNum, debug):
    collectScene(sid)
    clearScene(sid)
    scenePath = os.path.join(macro.TMP_NAME, '%04d' % sid)
    tmpPath = os.path.join(scenePath, macro.TMP_NAME)
    fnames = [fname for fname in os.listdir(tmpPath)]
    fnames.sort()
    images = [os.path.join(tmpPath, fname) for fname in fnames]
    images = [loadImage(fname) for fname in images if util.isImage(fname)]
    faces = calFaceRegions(images, faceNum, debug)
    pickScene(sid, images, faces)
    util.remove(tmpPath)


if __name__ == '__main__':
    pickCGToTmp('test')
    repickScene(1, True)
