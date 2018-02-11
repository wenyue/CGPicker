#!/usr/bin/python3
# -*- coding: utf-8 -*-

TMP_PATH = 'temp'
PICK_NAME = 'pick'
IMAGE_NAME = 'image'
FACE_NAME = 'face'
COLLECT_NAME = 'Simple'
ALL_NAME = 'All'
# 图片缩放系数
NORMALIZE_SCALE = 0.125
# 判断同一场景的阈值
SAME_SCENE_THRESHOLD = 0.2
# 判断同一动作的阈值
SAME_ACTION_THRESHOLD = 0.85
# 面部判断的半径
FACE_BRUSH_RADIUS = 30
FACE_BRUSH_RADIUS = int(FACE_BRUSH_RADIUS * NORMALIZE_SCALE)
# 采样pick的数量
PICK_SAMPLE_NUM = 5
# 比较pick的数量
PICK_COMPARE_NUM = 3
