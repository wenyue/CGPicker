#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import random
from datetime import datetime

from common import macro
from common.database import Database


class RandomPool(object):

    def __init__(self, root):
        self._root = root
        self._datetime = datetime.now()
        self._didx = 0
        self._sidx = 0
        self._lidx = 0
        self.load()

    def load(self):
        self._databases = []
        self._weights = []
        for dirname in os.listdir(self._root):
            CGRoot = os.path.join(self._root, dirname)
            databaseFilename = os.path.join(CGRoot, macro.DATABASE_FILE)
            if os.path.isfile(databaseFilename):
                database = Database(CGRoot)
                weight = self._calculateCumulativeSceneWeights(database)[-1]
                self._databases.append(database)
                self._weights.append(weight)

    def getNextImage(self):
        raise NotImplementedError

    def _calculateCumulativeSceneWeights(self, database):
        sceneWeights = []
        totalWeight = 0
        for idx in range(database.getSceneNum()):
            scene = database.getScene(idx)
            if scene.getRating() != 0:
                totalWeight += self._calculateSceneWeight(scene)
            sceneWeights.append(totalWeight)
        return sceneWeights

    def _calculateSceneWeight(self, scene):
        raise NotImplementedError

    def _randomDatabaseIdx(self):
        self._didx = random.choices(range(len(self._databases)), weights=self._weights)

    def _randomSceneIdx(self):
        database = self._databases[self._didx]
        self._sidx = random.cloises(
            range(database.getSceneNum()),
            cum_weight=self._calculateCumulativeSceneWeights(database)
        )


class RatingRandomPool(RandomPool):
    RATING_WEIGHTS = [0, 1, 1, 1, 1]
    DAY_WEIGHT = 0.01

    def __init__(self, root):
        super(RatingRandomPool, self).__init__(root)

    def getNextImage(self):
        pass

    def _calculateSceneWeight(self, scene):
        ratingWeight = self.RATING_WEIGHTS[scene.getRating()]
        days = (self._datetime - scene.getDatetime()).days
        timeWeight = min(days * self.DAY_WEIGHT, 1)
        return ratingWeight + timeWeight
