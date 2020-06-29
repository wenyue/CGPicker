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
        self._dirties = set()
        self._flushes = set()
        self._saveCounter = 0
        self.load()

        self._randomDatabaseIdx()
        self._randomSceneIdx()
        self.getScene().setDatetime(self._datetime)

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

    def flush(self):
        self.save()
        for database in self._flushes:
            database.flush()
        self._flushes.clear()

    def save(self):
        for database in self._dirties:
            database.save()
        self._dirties.clear()

    def setDirty(self, databaseIdx, needToFlush=False):
        database = self._databases[databaseIdx]
        weight = self._calculateCumulativeSceneWeights(database)[-1]
        self._weights[databaseIdx] = weight

        self._dirties.add(database)
        if needToFlush:
            self._flushes.add(database)
        self._saveCounter += 1
        if self._saveCounter % 100 == 0:
            self.save()

    def randomScene(self):
        raise NotImplementedError

    def getDatabase(self):
        return self._databases[self._didx]

    def getDatabaseIdx(self):
        return self._didx

    def getScene(self):
        database = self.getDatabase()
        return database.getScene(self._sidx)

    def getSceneIdx(self):
        return self._sidx

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
        self._didx = random.choices(range(len(self._databases)), weights=self._weights)[0]

    def _randomSceneIdx(self):
        database = self.getDatabase()
        self._sidx = random.choices(
            range(database.getSceneNum()),
            cum_weights=self._calculateCumulativeSceneWeights(database)
        )[0]


class RatingRandomPool(RandomPool):
    RATING_WEIGHTS = [0, 3, 10, 30, 100]
    DAY_WEIGHT = 1.1
    DAY_MAX_WEIGHT = 0

    def __init__(self, root):
        super(RatingRandomPool, self).__init__(root)

    def randomScene(self):
        self._randomDatabaseIdx()
        self._randomSceneIdx()
        self.getScene().setDatetime(self._datetime)
        self.setDirty(self.getDatabaseIdx())

    def _calculateSceneWeight(self, scene):
        ratingWeight = self.RATING_WEIGHTS[scene.getRating()]
        days = (self._datetime - scene.getDatetime()).days
        timeWeight = min(days * self.DAY_WEIGHT, self.DAY_MAX_WEIGHT)
        return ratingWeight + timeWeight
