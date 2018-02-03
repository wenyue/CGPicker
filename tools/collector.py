#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import macro
import util


def collectPickToCG(path):
	if not os.path.exists(macro.TMP_PATH):
		return
	util.remove(path)
	cpath = os.path.join(path, macro.COLLECT_NAME)
	apath = os.path.join(path, macro.ALL_NAME)
	for scene in os.listdir(macro.TMP_PATH):
		scenePath = os.path.join(macro.TMP_PATH, scene)
		for action in os.listdir(scenePath):
			actionPath = os.path.join(scenePath, action)
			if action == macro.PICK_NAME:
				for image in os.listdir(actionPath):
					util.copy(os.path.join(actionPath, image), cpath)
			else:
				imagePath = os.path.join(actionPath, macro.IMAGE_NAME)
				for image in os.listdir(imagePath):
					util.copy(os.path.join(imagePath, image), apath)
