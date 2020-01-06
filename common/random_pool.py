#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from common import macro
from common.database import Database


class RandomPool(object):

    def __init__(self, root):
        self._root = root
        self.load()

    def load(self):
        self._databases = []
        for dirname in os.listdir(self._root):
            CGRoot = os.path.join(self._root, dirname)
            databaseFilename = os.path.join(CGRoot, macro.DATABASE_FILE)
            if os.path.isfile(databaseFilename):
                database = Database(CGRoot)
                self._databases.append(database)

        self._calculateWeights()

    def getNextImage(self):
        raise NotImplementedError

    def _calculateWeights(self):
        raise NotImplementedError


class RatingRandomPool(RandomPool):

    def __init__(self, root):
        super(RatingRandomPool, self).__init__(root)
        self._weights = None

    def getNextImage(self):
        pass

    def _calculateWeights(self):
        for database in self._databases:
            self._calculateSceneWeight(database)

    def _calculateDatabaseWeight(self, database):
        pass

    def _calculateSceneWeight(self, scene):
        pass
