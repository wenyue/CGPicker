#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import macro
import util


def collectPickToCG(outPath, CGName):
    if not os.path.exists(macro.TMP_NAME):
        return

    tasks = []
    apath = os.path.join(outPath, CGName, macro.ALL_NAME)
    spath = os.path.join(outPath, CGName, macro.SAMPLE_NAME)
    gpath = os.path.join(outPath, macro.GREATEST_NAME)
    for scene in os.listdir(macro.TMP_NAME):
        scenePath = os.path.join(macro.TMP_NAME, scene)
        for action in os.listdir(scenePath):
            actionPath = os.path.join(scenePath, action)
            if action == macro.PICK_NAME:
                imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
                for image in os.listdir(imagePath):
                    tasks.append((os.path.join(imagePath, image), spath))
            elif action == macro.BACKUP_NAME:
                for image in os.listdir(actionPath):
                    tasks.append((os.path.join(actionPath, image), apath))
            elif action == macro.LOVE_NAME:
                imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
                for image in os.listdir(imagePath):
                    lovename = os.path.join(gpath, "%s-%s" % (CGName, image))
                    tasks.append((os.path.join(imagePath, image), lovename))
            else:
                imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
                for image in os.listdir(imagePath):
                    tasks.append((os.path.join(imagePath, image), apath))

    yield len(tasks)

    for from_, to_ in tasks:
        util.copy(from_, to_)
        filename = os.path.basename(from_)
        dirname = os.path.basename(to_)
        yield 'collecting: ' + os.path.join(CGName, dirname, filename)
