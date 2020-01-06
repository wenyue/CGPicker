#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os

from common import utils


def convertImages(path):
    tasks = []
    for fname in os.listdir(path):
        filename = os.path.join(path, fname)
        if not utils.isImage(filename):
            continue
        _, extend = os.path.splitext(filename)
        if extend.lower() == '.jpg':
            continue
        tasks.append(filename)

    yield len(tasks)

    for filename in tasks:
        im = Image.open(filename)
        try:
            im = im.convert('RGB')
        except Exception as e:
            print("Convert image error:", filename)
            raise (e)
        rootname, _ = os.path.splitext(filename)
        im.save(rootname+ '.jpg', 'JPEG', quality=98)
        im.close()
        os.remove(filename)
        yield 'converting: ' + filename
