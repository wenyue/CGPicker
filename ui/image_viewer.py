#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QAction, QActionGroup
from PyQt5.QtCore import QPoint, QSize, QTimer
from PyQt5.QtGui import QPixmap
from template.ui_image_viewer import Ui_ImageViewer
from ui.face import Face
from database import data
from enum import Enum


class ViewMode(Enum):
    NORMAL = 1
    PICK = 2
    LOVE = 3


class ImageViewer(Ui_ImageViewer):
    def __init__(self, *args, **kwargs):
        self.root = QWidget(*args, **kwargs)
        self.setupUi(self.root)

        self.root.resizeEvent = self.resizeEvent
        self.faceLayout = QHBoxLayout(self.faces)
        self.faceLayout.setSpacing(0)
        self.home.setVisible(False)
        self.actionNum.setStyleSheet("font-size:30px")

        self._faceCtrls = []
        self._sidx = 0
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._view_mode = ViewMode.NORMAL

    @property
    def curScene(self):
        self._sidx = data.normalizeSceneIdx(self._sidx)
        return data.getScene(self._sidx)

    @property
    def curAction(self):
        scene = self.curScene
        if not scene:
            return
        if self._view_mode == ViewMode.NORMAL:
            self._aidx = scene.normalizeActionIdx(self._aidx, loop=True)
            return scene.getAction(self._aidx)
        elif self._view_mode == ViewMode.PICK:
            return scene.getPick()
        elif self._view_mode == ViewMode.LOVE:
            return scene.getLove()

    @property
    def curImage(self):
        action = self.curAction
        if not action:
            return
        if self._view_mode == ViewMode.NORMAL:
            self._iidx = action.normalizeImageIdx(self._iidx)
            return action.getImage(self._iidx)
        elif self._view_mode == ViewMode.PICK:
            self._pidx = action.normalizeImageIdx(self._pidx)
            return action.getImage(self._pidx)
        elif self._view_mode == ViewMode.LOVE:
            self._lidx = action.normalizeImageIdx(self._lidx)
            return action.getImage(self._lidx)

    @property
    def curPick(self):
        scene = self.curScene
        return scene.getPick() if scene else None

    @property
    def curLove(self):
        scene = self.curScene
        return scene.getLove() if scene else None

    def isValid(self):
        return self.curImage is not None

    def setViewMode(self, viewMode):
        if self._view_mode == viewMode:
            self._view_mode = ViewMode.NORMAL
        else:
            self._view_mode = viewMode
        self.update()

    def setupMainMenu(self, menubar):
        viewMenu = menubar.addMenu('&View')

        normalViewAction = QAction('&Normal view', self.root)
        normalViewAction.setShortcut('Q')
        normalViewAction.setCheckable(True)
        normalViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.NORMAL))
        viewMenu.addAction(normalViewAction)

        pickViewAction = QAction('&Pick view', self.root)
        pickViewAction.setShortcut('W')
        pickViewAction.setCheckable(True)
        pickViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.PICK))
        viewMenu.addAction(pickViewAction)

        loveViewAction = QAction('&Love view', self.root)
        loveViewAction.setShortcut('E')
        loveViewAction.setCheckable(True)
        loveViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.LOVE))
        viewMenu.addAction(loveViewAction)

        viewModeGroup = QActionGroup(self.root)
        viewModeGroup.addAction(normalViewAction)
        viewModeGroup.addAction(pickViewAction)
        viewModeGroup.addAction(loveViewAction)
        normalViewAction.setChecked(True)

        viewMenu.addSeparator()

        selectImageAction = QAction('&Select image', self.root)
        selectImageAction.setShortcut('Space')
        selectImageAction.triggered.connect(self.selectImage)
        viewMenu.addAction(selectImageAction)

        viewMenu.addSeparator()

        nextImageAction = QAction('Next image', self.root)
        nextImageAction.setShortcut('Right')
        nextImageAction.triggered.connect(self.showNextImage)
        viewMenu.addAction(nextImageAction)

        prevImageAction = QAction('Prev image', self.root)
        prevImageAction.setShortcut('Left')
        prevImageAction.triggered.connect(self.showPrevImage)
        viewMenu.addAction(prevImageAction)

        viewMenu.addSeparator()

        self.nextActionAction = QAction('Next action', self.root)
        self.nextActionAction.setShortcut('Down')
        self.nextActionAction.triggered.connect(self.showNextAction)
        viewMenu.addAction(self.nextActionAction)

        self.prevActionAction = QAction('Prev action', self.root)
        self.prevActionAction.setShortcut('Up')
        self.prevActionAction.triggered.connect(self.showPrevAction)
        viewMenu.addAction(self.prevActionAction)

        viewMenu.addSeparator()

        nextSceneAction = QAction('Next scene', self.root)
        nextSceneAction.setShortcut('Ctrl+Down')
        nextSceneAction.triggered.connect(self.showNextScene)
        viewMenu.addAction(nextSceneAction)

        prevSceneAction = QAction('Prev scene', self.root)
        prevSceneAction.setShortcut('Ctrl+Up')
        prevSceneAction.triggered.connect(self.showPrevScene)
        viewMenu.addAction(prevSceneAction)

        editMenu = menubar.addMenu('&Edit')

        togglePickAction = QAction('&Toggle pick', self.root)
        togglePickAction.setShortcut('D')
        togglePickAction.triggered.connect(self.togglePick)
        editMenu.addAction(togglePickAction)

        toggleLoveAction = QAction('&Toggle love', self.root)
        toggleLoveAction.setShortcut('S')
        toggleLoveAction.triggered.connect(self.toggleLove)
        editMenu.addAction(toggleLoveAction)

        editMenu.addSeparator()

        for faceNum in range(1, 5):
            RepickAction = QAction('Repick %d' % faceNum, self.root)
            RepickAction.setShortcut('%d' % faceNum)
            RepickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, False))
            editMenu.addAction(RepickAction)

            RepickAction = QAction('Repick %d (debug)' % faceNum, self.root)
            RepickAction.setShortcut('Ctrl+%d' % faceNum)
            RepickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, True))
            editMenu.addAction(RepickAction)

        editMenu.addSeparator()

        clearPickAction = QAction('&Clear pick', self.root)
        clearPickAction.setShortcut('C')
        clearPickAction.triggered.connect(self.clearPick)
        editMenu.addAction(clearPickAction)

        modifyManuallyAction = QAction('&Modify manually', self.root)
        modifyManuallyAction.setShortcut('M')
        modifyManuallyAction.triggered.connect(self.modifyManually)
        editMenu.addAction(modifyManuallyAction)

    def show(self):
        self.update()

    def resizeEvent(self, event):
        self.update()

    def showNextImage(self):
        action = self.curAction
        if not action:
            return
        if self._view_mode == ViewMode.NORMAL:
            self._iidx += 1
        elif self._view_mode == ViewMode.PICK:
            self._pidx += 1
        elif self._view_mode == ViewMode.LOVE:
            self._lidx += 1
        self.update()

    def showPrevImage(self):
        action = self.curAction
        if not action:
            return
        if self._view_mode == ViewMode.NORMAL:
            self._iidx -= 1
        elif self._view_mode == ViewMode.PICK:
            self._pidx -= 1
        elif self._view_mode == ViewMode.LOVE:
            self._lidx -= 1
        self.update()

    def showNextAction(self):
        if self._view_mode == ViewMode.NORMAL:
            self._aidx += 1
            if self.curAction == self.curScene.getAction(0):
                self.showHomeFlag()
            self.update()

    def showPrevAction(self):
        if self._view_mode == ViewMode.NORMAL:
            self._aidx -= 1
            if self.curAction == self.curScene.getAction(0):
                self.showHomeFlag()
            self.update()

    def showNextScene(self):
        self._sidx += 1
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()

    def showPrevScene(self):
        self._sidx -= 1
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()

    def togglePick(self):
        pick = self.curPick
        image = self.curImage
        if pick.isInPick(image):
            pick.delFromPick(image)
        else:
            pick.addToPick(image)
        self.update()

    def toggleLove(self):
        love = self.curLove
        image = self.curImage
        if love.isInPick(image):
            love.delFromPick(image)
        else:
            love.addToPick(image)
        self.update()

    def selectImage(self):
        if self._view_mode != ViewMode.NORMAL:
            image = self.curImage
            self._aidx, self._iidx = self.curScene.indexImage(image)
            self.setViewMode(ViewMode.NORMAL)

    def clearPick(self):
        pick = self.curPick
        pick.clear()
        self.update()

    def repickScene(self, faceNum, debug):
        import importlib
        import tools.picker as picker
        importlib.reload(picker)
        scene = self.curScene
        picker.repickScene(scene.getSceneId(), faceNum, debug)
        scene.load()
        self.update()

    def modifyManually(self):
        import tools.picker as picker
        import macro
        import subprocess
        import os
        scene = self.curScene
        sid = scene.getSceneId()
        picker.backupScene(sid)
        picker.collectScene(sid)
        scenePath = os.path.join(macro.TMP_NAME, '%04d' % sid)
        tmpPath = os.path.join(scenePath, macro.TMP_NAME)
        subprocess.Popen(['explorer', tmpPath])

    def showHomeFlag(self):
        self.home.setVisible(True)
        cw = self.imgFrame.width()
        ch = self.imgFrame.height()
        hw = self.home.width()
        hh = self.home.height()
        self.home.move(QPoint((cw - hw) / 2, (ch - hh) / 2))
        QTimer.singleShot(500, lambda: self.home.setVisible(False))

    def update(self):
        self._updateActionNum()
        self._updateFaceCtrls()
        self._updateImageCtrl()

    def _updateActionNum(self):
        if (self._view_mode == ViewMode.NORMAL and self.isValid()):
            self.actionNum.setText('%d/%d' % (self._aidx + 1,
                                              self.curScene.getActionLen()))
        else:
            self.actionNum.setText('')

    def _updateFaceCtrls(self):
        if not self.isValid():
            self.faceFrame.setVisible(False)
            return
        self.faceFrame.setVisible(True)

        for ctrl in self._faceCtrls:
            ctrl.root.setVisible(False)

        faces = self.curAction.getFaces()
        scene = self.curScene
        actionIdx = 0
        ctrlIdx = 0
        selected_face = self.curAction.getFaceByImage(self.curImage)
        selected_ctrl = None
        for face in faces:
            if ctrlIdx >= len(self._faceCtrls):
                ctrl = Face(self.faces)
                self.faceLayout.addWidget(ctrl.root)
                self._faceCtrls.append(ctrl)
            else:
                ctrl = self._faceCtrls[ctrlIdx]
                ctrl.root.setVisible(True)
            ctrlIdx += 1
            ctrl.setFace(face)
            if face == selected_face:
                ctrl.selected(True)
                selected_ctrl = ctrl
            else:
                ctrl.selected(False)
            ctrl.star.setVisible(self.curPick.isInPick(face))
            ctrl.circle.setVisible(self.curLove.isInPick(face))
            if self._view_mode != ViewMode.NORMAL:
                while scene.getAction(actionIdx).indexImage(face) is None:
                    actionIdx += 1
                ctrl.starNum.setText(
                    '%d' % len(scene.getAction(actionIdx).getImages()))
            else:
                ctrl.starNum.setText('')

        hbar = self.faceFrame.horizontalScrollBar()
        hbarVal = selected_ctrl.root.pos().x() - self.faceFrame.width(
        ) / 2 + selected_ctrl.root.width() / 2
        hbar.setValue(hbarVal)

    def _updateImageCtrl(self):
        if not self.isValid():
            self.imgFrame.setVisible(False)
            return
        self.imgFrame.setVisible(True)

        image = self.curImage
        pixmap = QPixmap(image)
        self.img.setPixmap(pixmap)

        pw = pixmap.width()
        ph = pixmap.height()
        cw = self.imgFrame.width()
        ch = self.imgFrame.height()
        factor = min(cw / pw, ch / ph)
        self.img.resize(QSize(pw * factor, ph * factor))
        iw = self.img.width()
        ih = self.img.height()
        self.img.move(QPoint((cw - iw) / 2, (ch - ih) / 2))
