#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil


def groupby(func, elist):
    if not elist:
        return []
    groups = []
    group = []
    for element in elist:
        if not group or func(group[-1], element):
            group.append(element)
        else:
            groups.append(group)
            group = [element]
    groups.append(group)
    return groups


def isImage(filepath):
    _, extend = os.path.splitext(filepath)
    return os.path.isfile(filepath) and extend.lower() in ('.jpg', '.png', '.bmp')


def remove(path):
    if os.path.exists(path):
        shutil.rmtree(path)
