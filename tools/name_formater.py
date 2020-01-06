#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import itertools

from common import utils


def tokenLength(token):
    try:
        value = int(token)
    except ValueError:
        return 0
    return len(str(value))


def formatToken(token, num_of_digit):
    try:
        value = int(token)
    except ValueError:
        return token
    return '%0*d' % (num_of_digit, value)


def formatImageNames(path):
    # nod: number of digit
    max_nod = []
    for fname in os.listdir(path):
        filename = os.path.join(path, fname)
        if not utils.isImage(filename):
            continue
        rootname, _ = os.path.splitext(fname)
        nameTokens = rootname.split('_')
        token_nod = [tokenLength(token) for token in nameTokens]
        zip_nod = itertools.zip_longest(max_nod, token_nod, fillvalue=0)
        max_nod = [max(v1, v2) for v1, v2 in zip_nod]

    for fname in os.listdir(path):
        filename = os.path.join(path, fname)
        if not utils.isImage(filename):
            continue
        rootname, extend = os.path.splitext(fname)
        nameTokens = rootname.split('_')
        nameTokens = [
            formatToken(token, max_nod[index])
            for index, token in enumerate(nameTokens)
        ]
        expectedName = '_'.join(nameTokens) + extend.lower()
        if expectedName == filename:
            continue
        expectedName = os.path.join(path, expectedName)
        os.rename(filename, expectedName)
