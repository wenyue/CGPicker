#!/usr/bin/python3
# -*- coding: utf-8 -*-

TMP_NAME = 'tmp'
PICK_NAME = 'pick'
LOVE_NAME = 'love'
BACKUP_NAME = 'backup'
IMAGE_NAME = 'image'
FACE_NAME = 'face'
ALL_NAME = 'All'
SAMPLE_NAME = 'Sample'
GREATEST_NAME = '❤'

# 图片缩放系数
NORMALIZE_SCALE = 0.125
# 场景色差阈值
SCENE_ABERRATION_THRESHOLD = 0.2
# 场景色差忍耐值
SCENE_ABERRATION_ENDURANCE = 6

# 面部标准大小
FACE_BEST_SIZE = 0.06
# 面部上限大小
FACE_MAX_SIZE = 0.6
# 面部扩展系数
FACE_EXTEND_FACTOR = 1.2
# 面部加强系数
FACE_REFORCE_FACTOR = 1.8
# 面部大小系数
FACE_SIZE_FACTOR = 1.8
# 面部形状系数
FACE_SHAPE_FACTOR = 4.0
# 面部色差系数
FACE_ABERRATION_FACTOR = 0.3
# 面部探测系数
FACE_DETECT_FACTORS = (0.8, 1.0, 1.3, 1.5)

# 采样pick的数量
PICK_SAMPLE_NUM = 5
# 比较pick的数量
PICK_COMPARE_NUM = 3
