#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
from functools import reduce
import os
import random
import math
import copy
import json
import shutil

from common import utils
from common import macro


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
    w, h = int(img.width * macro.NORMALIZE_SCALE), int(img.height * macro.NORMALIZE_SCALE)
    img = img.resize((w, h), Image.BILINEAR)
    img = img.convert('L')
    img.filename = filename
    return img


def isSamePixel(lp, rp, i, j):
    return abs(lp[i, j] - rp[i, j]) < macro.ABERRATION_ENDURANCE


def calSimilarity(li, ri):
    w, h = li.size
    lp = li.load()
    rp = ri.load()
    samePixelNum = sum(1 if isSamePixel(lp, rp, i, j) else 0 for i in range(w) for j in range(h))
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
    totalValue = 0
    values = [[0] * h for _ in range(w)]
    for i in range(w):
        for j in range(h):
            value = pow(abs(lp[i, j] - rp[i, j]), factor)
            values[i][j] = value
            totalValue += value
    if totalValue != 0:
        for i in range(w):
            for j in range(h):
                hits[i][j] += values[i][j] / totalValue


def calHits(scene):
    w, h = scene[0].size
    hits = [[0] * h for _ in range(w)]
    if (len(scene) == 1):
        return hits
    reduce(lambda li, ri: calHit(hits, li, ri) or ri, scene)
    hits = [[pow(value, macro.FACE_REFORCE_FACTOR) for value in col] for col in hits]
    totalValue = sum(map(sum, hits))
    if totalValue != 0:
        hits = [[value / totalValue for value in col] for col in hits]
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
    minRadius = int(math.sqrt(w * h * macro.FACE_MIN_SIZE) // 2)
    if minRadius < radius < maxRadius:
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
    w, h = scene[0].size
    maxRadius = int(math.sqrt(w * h * macro.FACE_MAX_SIZE) // 2)
    minRadius = int(math.sqrt(w * h * macro.FACE_MIN_SIZE) // 2)

    if faceNum == 0:
        return [(w // 2, h // 2, max(w, h) // 2, -1)]

    hits = calHits(scene)

    faces = []
    for _ in range(faceNum):
        if debug:
            debugData(hits)

        center = (0, (w // 2, h // 2, max(w, h) // 2, -1))
        totalHits = calTotalHits(hits)
        if faces:
            bestRadius = faces[0][2]
            faceSizeFactor = macro.FACE_SIZE_FACTOR
        else:
            bestRadius = int(math.sqrt(w * h * macro.FACE_BEST_SIZE) // 2)
            faceSizeFactor = macro.FACE_SIZE_FACTOR / 2

        regions = []
        reduce(lambda li, ri: calRegion(regions, hits, li, ri) or ri, scene)
        for region in regions:
            x, y, radius, shape = region
            if radius > bestRadius:
                faceSize = (radius - bestRadius) / (maxRadius - bestRadius)
            else:
                faceSize = (bestRadius - radius) / (bestRadius - minRadius)
            factor = faceSize * faceSizeFactor + shape * macro.FACE_SHAPE_FACTOR + (
                x / w
            ) * macro.FACE_LEFT_FACTOR + (y / h) * macro.FACE_TOP_FACTOR + 1
            value = calHitValue(totalHits, x, y, radius) / factor
            center = max(center, (value, region))

        if (faceNum > 1):
            for scale in macro.FACE_DETECT_FACTORS:
                radius = max(int(bestRadius * scale), 1)
                if not (minRadius < radius < maxRadius):
                    break
                if radius > bestRadius:
                    faceSize = (radius - bestRadius) / (maxRadius - bestRadius)
                else:
                    faceSize = (bestRadius - radius) / (bestRadius - minRadius)
                shape = 0.3
                for x in range(w):
                    for y in range(h):
                        factor = faceSize * faceSizeFactor + \
                                shape * macro.FACE_SHAPE_FACTOR + \
                                (x / w) * macro.FACE_LEFT_FACTOR + \
                                (y / h) * macro.FACE_TOP_FACTOR + 1
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
    aberrationThreshold = w * h * macro.ACTION_ABERRATION_THRESHOLD
    diffPixelCount = 0
    for i in range(w):
        for j in range(h):
            if not isSamePixel(lp, rp, i, j):
                for x, y, radius, shape in faces:
                    if max(abs(i - x), abs(j - y)) <= radius and shape >= 0:
                        break
                else:
                    diffPixelCount += 1
                    if diffPixelCount >= aberrationThreshold:
                        return False
    return True


def generatePicks(actions):
    picks = []
    for action in actions:
        if picks:
            imgs = random.sample(action, min(len(action), macro.PICK_SAMPLE_NUM))
            cpicks = picks[-macro.PICK_COMPARE_NUM:]
            values = [sum(calSimilarity(img, pick) for pick in cpicks) for img in imgs]
            _, pick = min(zip(values, imgs), key=lambda x: x[0])
        else:
            pick = random.choice(action) if random.randint(0, 1) else action[0]
        picks.append(pick)
    return picks


def generateSceneProto(faces, actions, picks):
    actionsProto = []
    for action, pick in zip(actions, picks):
        actionsProto.append({
            'images': [os.path.basename(img.filename) for img in action],
            'pick': os.path.basename(pick.filename),
            'love': False,
        })
    w, h = actions[0][0].size
    facesProto = []
    for face in faces:
        left, right, top, bottom = convertRegion(face, w, h)
        facesProto.append([int(val / macro.NORMALIZE_SCALE) for val in (left, top, right, bottom)])
    return {
        'rating': 0,
        'timestamp': 0,
        'actions': actionsProto,
        'faces': facesProto,
    }


def genScenes(path):
    fnames = [fname for fname in sorted(os.listdir(path))]
    images = [os.path.join(path, fname) for fname in fnames]
    images = [loadImage(fname) for fname in images if utils.isImage(fname)]
    scenes = utils.groupby(isSameScene, images)
    return scenes


def pickCG(path):
    utils.remove(macro.TMP_NAME)
    scenes = genScenes(path)

    yield len(scenes)

    proto = []
    for sid, images in enumerate(scenes):
        faces = calFaceRegions(images)
        actions = utils.groupby(lambda li, ri: isSameAction(li, ri, faces), images)
        picks = generatePicks(actions)
        proto.append(generateSceneProto(faces, actions, picks))
        yield 'picking: %d/%d' % (sid + 1, len(scenes))

    filename = os.path.join(path, macro.DATABASE_FILE)
    with open(filename, 'w') as f:
        json.dump(proto, f, indent=2, sort_keys=True)


def repickScene(images, faceNum, debug):
    images = [loadImage(fname) for fname in images if utils.isImage(fname)]
    faces = calFaceRegions(images, faceNum, debug)
    actions = utils.groupby(lambda li, ri: isSameAction(li, ri, faces), images)
    picks = generatePicks(actions)
    return generateSceneProto(faces, actions, picks)


def repickSceneWithFaces(images, facesProto):
    images = [loadImage(fname) for fname in images if utils.isImage(fname)]
    faces = []
    for faceProto in facesProto:
        x = (faceProto[0] + faceProto[2]) / 2 * macro.NORMALIZE_SCALE
        y = (faceProto[1] + faceProto[3]) / 2 * macro.NORMALIZE_SCALE
        width = (faceProto[2] - faceProto[0]) * macro.NORMALIZE_SCALE
        height = (faceProto[3] - faceProto[1]) * macro.NORMALIZE_SCALE
        radius = max(width, height) / 2
        faces.append([x, y, radius, 0])
    actions = utils.groupby(lambda li, ri: isSameAction(li, ri, faces), images)
    picks = generatePicks(actions)
    return generateSceneProto(faces, actions, picks)
