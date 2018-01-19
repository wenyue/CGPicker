#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import macro
import util


def collectPickToCG(path):
	if not os.path.exists(macro.TMP_PATH):
		return
	path = os.path.join(path, macro.COLLECT_NAME)
	util.remove(path)
	picks = [os.path.join(macro.TMP_PATH, dirname, macro.PICK_NAME) for dirname in os.listdir(macro.TMP_PATH)]
	for pick in picks:
		for fname in os.listdir(pick):
			util.copy(os.path.join(pick, fname), path)
