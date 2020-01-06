#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os
import sys
import time
import subprocess
import shutil

from common import macro
from common import utils


def backupSmallImages(path):
    bpath = os.path.join(path, macro.BACKUP_NAME)
    for fname in os.listdir(path):
        filename = os.path.join(path, fname)
        if not utils.isImage(filename):
            continue
        with Image.open(filename) as img:
            width = img.width
            height = img.height
        if width < macro.STAND_WIDTH and height < macro.STAND_HEIGHT:
            os.makedirs(bpath, exist_ok=True)
            shutil.move(filename, os.path.join(bpath, fname))


def filterUpscaledImages(path):
    bpath = os.path.join(path, macro.BACKUP_NAME)
    tpath = os.path.join(path, macro.TMP_NAME)
    if not os.path.exists(bpath) or not os.path.exists(tpath):
        return
    largeImages = os.listdir(tpath)
    for damagedImage in largeImages[-3:]:
        os.remove(os.path.join(tpath, damagedImage))
    applyLargeImages(path)
    largeImages = largeImages[:-3]

    for largeImage in largeImages:
        fname, _ = os.path.splitext(largeImage)
        os.remove(os.path.join(bpath, fname))


def applyLargeImages(path):
    tpath = os.path.join(path, macro.TMP_NAME)
    if not os.path.exists(tpath):
        return
    for fname in os.listdir(tpath):
        filename = os.path.join(tpath, fname)
        originalName, extend = os.path.splitext(fname)
        rawName, _ = os.path.splitext(originalName)
        os.rename(filename, os.path.join(path, rawName + extend))


def clear(path):
    applyLargeImages(path)
    bpath = os.path.join(path, macro.BACKUP_NAME)
    tpath = os.path.join(path, macro.TMP_NAME)
    utils.remove(bpath)
    utils.remove(tpath)


def upscaleImages(path):
    if not sys.platform.startswith('win'):
        return

    backupSmallImages(path)
    filterUpscaledImages(path)

    bpath = os.path.join(path, macro.BACKUP_NAME)
    tasks = os.listdir(bpath) if os.path.exists(bpath) else []
    if not tasks:
        clear(path)
        return

    tpath = os.path.join(path, macro.TMP_NAME)
    os.makedirs(tpath, exist_ok=True)

    waifu2xPath = os.path.join('tools', 'waifu2x-ncnn-vulkan')
    cmd = [
        os.path.join(waifu2xPath, 'waifu2x-ncnn-vulkan.exe'), '-t', '64', '-i',
        bpath, '-o', tpath
    ]
    p = subprocess.Popen(cmd, cwd=waifu2xPath)

    yield len(tasks)

    previsouNum = 0
    while previsouNum < len(tasks):
        time.sleep(5)  # second
        finishNum = len(os.listdir(tpath))
        for index in range(previsouNum, finishNum):
            yield 'upscaling: ' + os.path.join(path, tasks[index])
        previsouNum = finishNum

    p.wait()

    clear(path)
