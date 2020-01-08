#!/usr/bin/python3
# -*- coding: utf-8 -*-

DATABASE_FILE = 'database.json'

TMP_NAME = 'tmp'
BACKUP_NAME = 'backup'
RATING_MAP = (u'', u'⭐', u'⭐⭐', u'⭐⭐⭐', u'❤')

STAND_WIDTH = 1920
STAND_HEIGHT = 1080

# 图片缩放系数
NORMALIZE_SCALE = 1 / 32
# 色差忍耐值
ABERRATION_ENDURANCE = 6
# 场景色差阈值
SCENE_ABERRATION_THRESHOLD = 0.2
# 动作色差阈值
ACTION_ABERRATION_THRESHOLD = 0.0002

# 面部标准大小
FACE_BEST_SIZE = 0.06
# 面部下限大小
FACE_MIN_SIZE = 0.003
# 面部上限大小
FACE_MAX_SIZE = 0.3
# 面部扩展系数
FACE_EXTEND_FACTOR = 1.3
# 面部大小权重
FACE_SIZE_FACTOR = 4.0
# 面部形状权重
FACE_SHAPE_FACTOR = 3.0
# 面部左方权重
FACE_LEFT_FACTOR = 0.0
# 面部上方权重
FACE_TOP_FACTOR = 0.8
# 面部色差系数
FACE_ABERRATION_FACTOR = 0.5
# 面部加强系数
FACE_REFORCE_FACTOR = 1.3
# 面部探测系数
FACE_DETECT_FACTORS = (0.7, 1.0, 1.5, 1.8)

# 面部色差忍耐值
FACE_ABERRATION_ENDURANCE = 1

# 采样pick的数量
PICK_SAMPLE_NUM = 5
# 比较pick的数量
PICK_COMPARE_NUM = 3
