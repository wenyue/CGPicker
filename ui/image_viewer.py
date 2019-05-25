#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QAction, QActionGroup, QLabel
from PyQt5.QtCore import QPoint, QSize, QTimer
from PyQt5.QtGui import QPixmap
from template.ui_image_viewer import Ui_ImageViewer
from ui.face import Face
from database import data
from enum import Enum
import config


class ViewMode(Enum):
    SELECT = 1
    PICK = 2
    LOVE = 3


class ImageViewer(Ui_ImageViewer):
    def __init__(self, *args, **kwargs):
        self.root = QWidget(*args, **kwargs)
        self.setupUi(self.root)

        self.img.paintEvent = self._paintImageCtrl
        self.faceLayout = QHBoxLayout(self.faces)
        self.faceLayout.setSpacing(0)
        self.home.setVisible(False)
        self.actionNum.setStyleSheet('font-size:30px')
        self.actionNum.setText('number')

        self._faceCtrls = []
        self._view_mode = ViewMode.PICK
        self._last_view_mode = ViewMode.PICK
        self._sidx = 0
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0

    @property
    def curScene(self):
        self._sidx = data.normalizeSceneIdx(self._sidx)
        return data.getScene(self._sidx)

    @property
    def curAction(self):
        scene = self.curScene
        if not scene:
            return
        if self._view_mode == ViewMode.SELECT:
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
        if self._view_mode == ViewMode.SELECT:
            self._iidx = action.normalizeImageIdx(self._iidx)
            return action.getImage(self._iidx)
        elif self._view_mode == ViewMode.PICK:
            self._pidx = action.normalizeImageIdx(self._pidx, loop=True)
            return action.getImage(self._pidx)
        elif self._view_mode == ViewMode.LOVE:
            self._lidx = action.normalizeImageIdx(self._lidx, loop=True)
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

    def setupMainMenu(self, menubar):
        viewMenu = menubar.addMenu('&View')

        normalViewAction = QAction('&Normal view', self.root)
        normalViewAction.setShortcut('Q')
        normalViewAction.setCheckable(True)
        normalViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.SELECT))
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
        togglePickAction.setShortcut('Tab')
        togglePickAction.triggered.connect(self.togglePick)
        editMenu.addAction(togglePickAction)

        clearPickAction = QAction('&Clear pick', self.root)
        clearPickAction.setShortcut('Delete')
        clearPickAction.triggered.connect(self.clearPick)
        editMenu.addAction(clearPickAction)

        toggleLoveAction = QAction('&Toggle love', self.root)
        toggleLoveAction.setShortcut('Ctrl+Tab')
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

        modifyManuallyAction = QAction('&Modify manually', self.root)
        modifyManuallyAction.setShortcut('M')
        modifyManuallyAction.triggered.connect(self.modifyManually)
        editMenu.addAction(modifyManuallyAction)

        deleteSceneAction = QAction('&Delete scene', self.root)
        deleteSceneAction.setShortcut('Ctrl+Shift+Delete')
        deleteSceneAction.triggered.connect(self.deleteScenen)
        editMenu.addAction(deleteSceneAction)

    def updateWindowTitle(self):
        CGName = config.get('path', 'CGName')
        self._sidx = data.normalizeSceneIdx(self._sidx)
        self.root.window().setWindowTitle(u'CGPicker《%s》 [%d/%d]' %
                                          (CGName, self._sidx + 1,
                                           data.getSceneLen()))

    def show(self):
        self._sidx = 0
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()
        self.updateWindowTitle()

    def setViewMode(self, viewMode):
        if self._view_mode == viewMode:
            if self._view_mode == ViewMode.SELECT:
                self._view_mode = self._last_view_mode
                self._last_view_mode = ViewMode.SELECT
                self.update()
        else:
            self._last_view_mode = self._view_mode
            self._view_mode = viewMode
            self.update()

    def selectImage(self):
        if self._view_mode == ViewMode.SELECT:
            self.setViewMode(self._last_view_mode)
        else:
            image = self.curImage
            if image:
                self._aidx, self._iidx = self.curScene.indexImage(image)
            self.setViewMode(ViewMode.SELECT)

    def showNextImage(self):
        action = self.curAction
        if not action:
            return
        if self._view_mode == ViewMode.SELECT:
            self._iidx += 1
        elif self._view_mode == ViewMode.PICK:
            self._pidx += 1
            if self.curImage == action.getImage(0):
                self.showHomeFlag()
        elif self._view_mode == ViewMode.LOVE:
            self._lidx += 1
            if self.curImage == action.getImage(0):
                self.showHomeFlag()
        self.update()

    def showPrevImage(self):
        action = self.curAction
        if not action:
            return
        if self._view_mode == ViewMode.SELECT:
            self._iidx -= 1
        elif self._view_mode == ViewMode.PICK:
            self._pidx -= 1
            if self.curImage == action.getImage(0):
                self.showHomeFlag()
        elif self._view_mode == ViewMode.LOVE:
            self._lidx -= 1
            if self.curImage == action.getImage(0):
                self.showHomeFlag()
        self.update()

    def showNextAction(self):
        if self._view_mode == ViewMode.SELECT:
            self._aidx += 1
            if self.curAction == self.curScene.getAction(0):
                self.showHomeFlag()
            self.update()

    def showPrevAction(self):
        if self._view_mode == ViewMode.SELECT:
            self._aidx -= 1
            if self.curAction == self.curScene.getAction(0):
                self.showHomeFlag()
            self.update()

    def showNextScene(self):
        self._view_mode = ViewMode.PICK
        self._sidx += 1
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()
        self.updateWindowTitle()

    def showPrevScene(self):
        self._view_mode = ViewMode.PICK
        self._sidx -= 1
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()
        self.updateWindowTitle()

    def togglePick(self):
        image = self.curImage
        if not image:
            return
        pick = self.curPick
        if pick.isInPick(image):
            pick.delFromPick(image)
            self._pidx = pick.normalizeImageIdx(self._pidx)
        else:
            pick.addToPick(image)
        self.update()

    def clearPick(self):
        pick = self.curPick
        pick.clear()
        self.update()

    def toggleLove(self):
        image = self.curImage
        if not image:
            return
        love = self.curLove
        if love.isInPick(image):
            love.delFromPick(image)
            self._lidx = love.normalizeImageIdx(self._lidx)
        else:
            love.addToPick(image)
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
        picker.collectScene(sid, force=True)
        scenePath = os.path.join(macro.TMP_NAME, '%04d' % sid)
        tmpPath = os.path.join(scenePath, macro.TMP_NAME)
        subprocess.Popen(['explorer', tmpPath])
        scene.load()
        self.update()

    def deleteScenen(self):
        import tools.picker as picker
        scene = self.curScene
        sid = scene.getSceneId()
        picker.backupScene(sid)
        scene.load()
        self.update()

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
        if (self._view_mode == ViewMode.SELECT and self.isValid()):
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
            if self._view_mode != ViewMode.SELECT:
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

    def _paintImageCtrl(self, event):
        pw = self.img.pixmap().width()
        ph = self.img.pixmap().height()
        cw = self.imgFrame.width()
        ch = self.imgFrame.height()
        factor = min(cw / pw, ch / ph)
        self.img.resize(QSize(pw * factor, ph * factor))
        iw = self.img.width()
        ih = self.img.height()
        self.img.move(QPoint((cw - iw) / 2, (ch - ih) / 2))
        QLabel.paintEvent(self.img, event)
