#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QLabel, QActionGroup
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QPixmap
from template.ui_viewer import Ui_Viewer

from common import macro


class Viewer(QWidget, Ui_Viewer):

    class SceneInfo(object):

        def __init__(self, randomPool):
            self.database = randomPool.getDatabase()
            self.databaseIdx = randomPool.getDatabaseIdx()
            self.scene = randomPool.getScene()
            self.sceneIdx = randomPool.getSceneIdx()

    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self._viewMenu = None
        self._editMenu = None
        self._imageCtrlHandler = ImageCtrlHandler(self.imgFrame)
        self._history = []

    def init(self, randomPool):
        self._randomPool = randomPool

        self._history.append(self.SceneInfo(self._randomPool))
        self._hidx = 0
        self._lidx = 0

        self._update()

    def refresh(self):
        self._lidx = 0
        self._update()

    def setVisible(self, isVisible):
        super(Viewer, self).setVisible(isVisible)
        self._setMenuEnabled(isVisible)

    def _setMenuEnabled(self, isEnabled):
        if self._viewMenu:
            for action in self._viewMenu.actions():
                action.setEnabled(isEnabled)
            self._viewMenu.menuAction().setVisible(isEnabled)
        if self._editMenu:
            for action in self._editMenu.actions():
                action.setEnabled(isEnabled)
            self._editMenu.menuAction().setVisible(isEnabled)

    def setupMainMenu(self, menubar):
        # Viewe menu
        viewMenu = menubar.addMenu('&View')
        self._viewMenu = viewMenu

        prevImageAction = viewMenu.addAction('Previous')
        prevImageAction.setShortcut('Left')
        prevImageAction.triggered.connect(self.showPrevImage)

        nextImageAction = viewMenu.addAction('Next')
        nextImageAction.setShortcut('Right')
        nextImageAction.triggered.connect(self.showNextImage)

        # Edit menu
        editMenu = menubar.addMenu('&Edit')
        self._editMenu = editMenu

        self.setupRatingMenu(editMenu)

        #  Refresh visibility
        self._setMenuEnabled(self.isVisible())

    def setupRatingMenu(self, editMenu):
        ratingGroup = QActionGroup(editMenu)
        for rating in range(1, 5):
            ratingAction = editMenu.addAction('Rating %s' % macro.RATING_MAP[rating])
            ratingAction.setShortcut('%d' % rating)
            ratingAction.setCheckable(True)
            ratingAction.triggered.connect(lambda _, rating=rating: self.setRating(rating))
            ratingGroup.addAction(ratingAction)

            def update(ratingAction=ratingAction, rating=rating):
                checked = self.curScene.getRawRating() == rating if self.curScene else False
                ratingAction.setChecked(checked)

            editMenu.aboutToShow.connect(update)

    @property
    def curDatabase(self):
        return self._history[self._hidx].database

    @property
    def curDatabaseIdx(self):
        return self._history[self._hidx].databaseIdx

    @property
    def curScene(self):
        return self._history[self._hidx].scene

    @property
    def curSceneIdx(self):
        return self._history[self._hidx].sceneIdx

    @property
    def curLove(self):
        return self.curScene.getLove()

    @property
    def curImage(self):
        return self.curLove.getImage(self._lidx)

    def isInvalid(self):
        return self.curScene != self.curDatabase.getScene(self.curSceneIdx)

    def showPrevImage(self):
        if self._lidx > 0:
            self._lidx -= 1
        else:
            if self._hidx > 0:
                self._hidx -= 1
                self._lidx = self.curLove.getImageNum() - 1
            else:
                return
        self._update()

    def showNextImage(self):
        self._lidx += 1
        if self._lidx == self.curLove.getImageNum():
            self._lidx = 0
            self._hidx += 1
            if self._hidx == len(self._history):
                self._randomPool.randomScene()
                imageInfo = self.SceneInfo(self._randomPool)
                self._history.append(imageInfo)

        self._update()

    def setRating(self, rating):
        if self.isInvalid():
            return
        self.curScene.setRating(rating)
        self._randomPool.setDirty(self.curDatabaseIdx)
        self._update()

    def _update(self):
        self._updateImageCtrl()
        self._updateWindowTitle()

    def _updateImageCtrl(self):
        if self.isInvalid():
            self.imgFrame.setVisible(False)
            return
        self.imgFrame.setVisible(True)
        pixmap = QPixmap(self.curImage)
        self.img.setPixmap(pixmap)
        self.rating.setText(macro.RATING_MAP[self.curScene.getRating()])

    def _updateWindowTitle(self):
        from PyQt5.QtCore import QCoreApplication
        applicationName = QCoreApplication.applicationName()
        if self.isInvalid():
            self.window().setWindowTitle(applicationName)
            return
        self.window().setWindowTitle(
            u'%s 《%s》[%d/%d]' % (
                applicationName, self.curDatabase.getCGName(), self.curSceneIdx + 1,
                self.curDatabase.getSceneNum()
            )
        )


class ImageCtrlHandler(object):

    def __init__(self, frameCtrl):
        self.frameCtrl = frameCtrl
        self.frameCtrl.resizeEvent = self._onResize
        self.rating = frameCtrl.findChild(QLabel, 'rating')
        self.rating.paintEvent = self._paintRatingCtrl
        self.img = frameCtrl.findChild(QLabel, 'img')
        self.img.paintEvent = self._paintImgCtrl

    def _onResize(self, event):
        self._updateRating(event)

    def _paintRatingCtrl(self, event):
        self._updateRating(event)
        QLabel.paintEvent(self.rating, event)

    def _paintImgCtrl(self, event):
        pw = self.img.pixmap().width()
        ph = self.img.pixmap().height()
        cw = self.frameCtrl.width()
        ch = self.frameCtrl.height()
        factor = min(cw / pw, ch / ph)
        self.img.resize(QSize(pw * factor, ph * factor))
        iw = self.img.width()
        ih = self.img.height()
        self.img.move(QPoint((cw - iw) / 2, (ch - ih) / 2))
        QLabel.paintEvent(self.img, event)

    def _updateRating(self, event):
        rw = self.rating.width()
        rh = self.rating.height()
        cw = self.frameCtrl.width()
        ch = self.frameCtrl.height()
        self.rating.move(QPoint((cw - rw - 3), (ch - rh - 3)))
