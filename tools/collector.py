#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import macro
import util


def collectPickToCG(outPath, CGName):
    if not os.path.exists(macro.TMP_NAME):
        return

    CGPath = os.path.join(outPath, CGName)
    apath = os.path.join(CGPath, macro.ALL_NAME)
    spath = os.path.join(CGPath, macro.SAMPLE_NAME)
    gpath = os.path.join(outPath, macro.GREATEST_NAME)

    for fname in os.listdir(outPath):
        index = fname.rfind('[')
        if (index == -1 and fname == CGName) or (index != -1
                                                 and fname[0:index] == CGName):
            util.remove(os.path.join(outPath, fname))
            break

    for fname in os.listdir(gpath):
        if fname.startswith("%s-" % CGName):
            os.remove(os.path.join(gpath, fname))

    tasks = []
    for scene in os.listdir(macro.TMP_NAME):
        scenePath = os.path.join(macro.TMP_NAME, scene)
        for action in os.listdir(scenePath):
            actionPath = os.path.join(scenePath, action)
            if action == macro.PICK_NAME:
                imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
                for image in os.listdir(imagePath):
                    tasks.append((os.path.join(imagePath, image), spath))
            elif action == macro.LOVE_NAME:
                imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
                for image in os.listdir(imagePath):
                    lovename = os.path.join(gpath, "%s-%s" % (CGName, image))
                    tasks.append((os.path.join(imagePath, image), lovename))
            elif action == macro.BACKUP_NAME:
                continue
            elif action == macro.TMP_NAME:
                continue
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
