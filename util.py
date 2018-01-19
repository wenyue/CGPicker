#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil


def groupby(func, elist):
	groups = []
	group = []
	preElement = None
	for element in elist:
		if preElement is None or func(preElement, element):
			group.append(element)
		else:
			groups.append(group)
			group = [element]
		preElement = element
	group and groups.append(group)
	return groups


def isImage(filepath):
	_, extend = os.path.splitext(filepath)
	return os.path.isfile(filepath) and extend.lower() == '.jpg'


def remove(path):
	if os.path.exists(path):
		shutil.rmtree(path)


def copy(fromPath, toPath):
	os.makedirs(toPath, exist_ok=True)
	shutil.copy(fromPath, toPath)
