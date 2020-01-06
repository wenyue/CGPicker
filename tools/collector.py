#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil

from common import macro
from common import utils


def collectPickToCG(CGRoot, newCGRoot):
    utils.remove(newCGRoot)
    os.makedirs(newCGRoot)

    shutil.move(os.path.join(CGRoot, macro.DATABASE_FILE), newCGRoot)

    tasks = []
    for fname in os.listdir(CGRoot):
        filename = os.path.join(CGRoot, fname)
        if utils.isImage(filename):
            tasks.append(filename)

    yield len(tasks)

    for filename in tasks:
        shutil.move(filename, newCGRoot)
        basename = os.path.basename(filename)
        yield 'collecting: ' + basename

    utils.remove(CGRoot)
