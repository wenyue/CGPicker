#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os


def convertImages(path):
    tasks = []
    for root, _, files in os.walk(path):
        for filename in files:
            _, extend = os.path.splitext(filename)
            if extend.lower() not in ('.png', '.bmp'):
                continue
            filename = os.path.join(root, filename)
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
