#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QAction, QActionGroup
from PyQt5.QtCore import QPoint, QSize, QTimer, Qt
from PyQt5.QtGui import QPixmap
from template.ui_image_viewer import Ui_ImageViewer

from ui.face import Face
from database import data

RatingMap = (u'#', u'☆', u'☆☆', u'☆☆☆', u'❤')


class ViewMode(Enum):
    SELECT = 1
    PICK = 2
    LOVE = 3


class ImageViewer(QWidget, Ui_ImageViewer):
    def __init__(self, *args, **kwargs):
        super(ImageViewer, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.img.paintEvent = self._paintImageCtrl
        self.faceLayout = QtWidgets.QHBoxLayout(self.faces)
        self.faceLayout.setSpacing(0)
        self.home.setVisible(False)
        self.actionNum.setStyleSheet('font-size:30px')
        self.actionNum.setText('number')

        self._faceCtrls = []
        self._viewMode = ViewMode.PICK
        self._lastViewMode = ViewMode.PICK
        self._lockViewMode = ViewMode.PICK
        self._sidx = 0
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._saveCounter = 0
        self._globalRating = 2

    def mousePressEvent(self, event):
        super(ImageViewer, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.selectImage()
        elif event.button() == Qt.RightButton:
            self.toggleLove()
        elif event.button() == Qt.MiddleButton:
            self.togglePick()
        elif event.button() == Qt.ForwardButton:
            if self._viewMode == ViewMode.SELECT:
                self.setViewMode(ViewMode.SELECT)
            elif self._viewMode == ViewMode.PICK:
                self.setViewMode(ViewMode.LOVE)
            elif self._viewMode == ViewMode.LOVE:
                self.setViewMode(ViewMode.PICK)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        super(ImageViewer, self).mouseDoubleClickEvent(event)
        if event.button() == Qt.BackButton:
            self.showNextScene()
        elif event.button() == Qt.ForwardButton:
            self.showPrevScene()
        event.accept()

    def wheelEvent(self, event):
        super(ImageViewer, self).wheelEvent(event)
        numDegrees = event.angleDelta() / 8
        numSteps = (numDegrees / 15).y()

        if event.buttons() & Qt.BackButton:
            for _ in range(numSteps, 0):
                self.showNextAction()
            for _ in range(0, numSteps):
                self.showPrevAction()
        else:
            for _ in range(numSteps, 0):
                self.showNextImage()
            for _ in range(0, numSteps):
                self.showPrevImage()
        event.accept()

    @property
    def curScene(self):
        return data.getScene(self._sidx)

    @property
    def curAction(self):
        scene = self.curScene
        if not scene:
            return
        if self._viewMode == ViewMode.SELECT:
            return scene.getAction(self._aidx)
        elif self._viewMode == ViewMode.PICK:
            return scene.getPick()
        elif self._viewMode == ViewMode.LOVE:
            return scene.getLove()

    @property
    def curImage(self):
        action = self.curAction
        if not action:
            return
        if self._viewMode == ViewMode.SELECT:
            return action.getImage(self._iidx)
        elif self._viewMode == ViewMode.PICK:
            return action.getImage(self._pidx)
        elif self._viewMode == ViewMode.LOVE:
            return action.getImage(self._lidx)

    @property
    def curPick(self):
        scene = self.curScene
        return scene.getPick() if scene else None

    @property
    def curLove(self):
        scene = self.curScene
        return scene.getLove() if scene else None

    def setupMainMenu(self, menubar):
        viewMenu = menubar.addMenu('&View')
        self.setupViewModeMenu(viewMenu)

        viewMenu.addSeparator()
        self.setupLockViewModeMenu(viewMenu)

        viewMenu.addSeparator()
        self.setupNavigatorMenu(viewMenu)

        editMenu = menubar.addMenu('&Edit')
        self.setupToggleMenu(editMenu)

        editMenu.addSeparator()
        self.setupRatingMenu(editMenu)

        editMenu.addSeparator()
        self.setupRepickMenu(editMenu)

        editMenu.addSeparator()
        self.setupModifyMenu(editMenu)

    def setupViewModeMenu(self, viewMenu):
        normalViewAction = QAction('&Normal View', self)
        normalViewAction.setShortcut('Q')
        normalViewAction.setCheckable(True)
        normalViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.SELECT))
        viewMenu.addAction(normalViewAction)

        pickViewAction = QAction('&Pick View', self)
        pickViewAction.setShortcut('W')
        pickViewAction.setCheckable(True)
        pickViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.PICK))
        viewMenu.addAction(pickViewAction)

        loveViewAction = QAction('&Love View', self)
        loveViewAction.setShortcut('E')
        loveViewAction.setCheckable(True)
        loveViewAction.triggered.connect(
            lambda: self.setViewMode(ViewMode.LOVE))
        viewMenu.addAction(loveViewAction)

        viewModeGroup = QActionGroup(self)
        viewModeGroup.addAction(normalViewAction)
        viewModeGroup.addAction(pickViewAction)
        viewModeGroup.addAction(loveViewAction)

        def update():
            if self._viewMode == ViewMode.SELECT:
                normalViewAction.setChecked(True)
            elif self._viewMode == ViewMode.PICK:
                pickViewAction.setChecked(True)
            elif self._viewMode == ViewMode.LOVE:
                loveViewAction.setChecked(True)

        viewMenu.aboutToShow.connect(update)

    def setupLockViewModeMenu(self, viewMenu):
        lockNormalViewAction = QAction('&Lock Normal View', self)
        lockNormalViewAction.setShortcut('Ctrl+Q')
        lockNormalViewAction.setCheckable(True)
        lockNormalViewAction.triggered.connect(
            lambda: self.setLockViewMode(ViewMode.SELECT))
        viewMenu.addAction(lockNormalViewAction)

        lockPickViewAction = QAction('&Lock Pick View', self)
        lockPickViewAction.setShortcut('Ctrl+W')
        lockPickViewAction.setCheckable(True)
        lockPickViewAction.triggered.connect(
            lambda: self.setLockViewMode(ViewMode.PICK))
        viewMenu.addAction(lockPickViewAction)

        lockLoveViewAction = QAction('&Lock Love View', self)
        lockLoveViewAction.setShortcut('Ctrl+E')
        lockLoveViewAction.setCheckable(True)
        lockLoveViewAction.triggered.connect(
            lambda: self.setLockViewMode(ViewMode.LOVE))
        viewMenu.addAction(lockLoveViewAction)

        lockViewModeGroup = QActionGroup(self)
        lockViewModeGroup.addAction(lockNormalViewAction)
        lockViewModeGroup.addAction(lockPickViewAction)
        lockViewModeGroup.addAction(lockLoveViewAction)

        def update():
            if self._lockViewMode == ViewMode.SELECT:
                lockNormalViewAction.setChecked(True)
            elif self._lockViewMode == ViewMode.PICK:
                lockPickViewAction.setChecked(True)
            elif self._lockViewMode == ViewMode.LOVE:
                lockLoveViewAction.setChecked(True)

        viewMenu.aboutToShow.connect(update)

    def setupNavigatorMenu(self, viewMenu):
        selectImageAction = QAction('&Select Image', self)
        selectImageAction.setShortcut('Space')
        selectImageAction.triggered.connect(self.selectImage)
        viewMenu.addAction(selectImageAction)

        viewMenu.addSeparator()

        nextImageAction = QAction('Next Image', self)
        nextImageAction.setShortcut('Right')
        nextImageAction.triggered.connect(self.showNextImage)
        viewMenu.addAction(nextImageAction)

        prevImageAction = QAction('Prev Image', self)
        prevImageAction.setShortcut('Left')
        prevImageAction.triggered.connect(self.showPrevImage)
        viewMenu.addAction(prevImageAction)

        viewMenu.addSeparator()

        self.nextActionAction = QAction('Next Action', self)
        self.nextActionAction.setShortcut('Down')
        self.nextActionAction.triggered.connect(self.showNextAction)
        viewMenu.addAction(self.nextActionAction)

        self.prevActionAction = QAction('Prev Action', self)
        self.prevActionAction.setShortcut('Up')
        self.prevActionAction.triggered.connect(self.showPrevAction)
        viewMenu.addAction(self.prevActionAction)

        viewMenu.addSeparator()

        nextSceneAction = QAction('Next Scene', self)
        nextSceneAction.setShortcut('Ctrl+Down')
        nextSceneAction.triggered.connect(self.showNextScene)
        viewMenu.addAction(nextSceneAction)

        prevSceneAction = QAction('Prev Scene', self)
        prevSceneAction.setShortcut('Ctrl+Up')
        prevSceneAction.triggered.connect(self.showPrevScene)
        viewMenu.addAction(prevSceneAction)

    def setupToggleMenu(self, editMenu):
        togglePickAction = QAction('&Toggle Pick', self)
        togglePickAction.setShortcut('Tab')
        togglePickAction.triggered.connect(self.togglePick)
        editMenu.addAction(togglePickAction)

        toggleLoveAction = QAction('&Toggle Love', self)
        toggleLoveAction.setShortcut('Ctrl+Tab')
        toggleLoveAction.triggered.connect(self.toggleLove)
        editMenu.addAction(toggleLoveAction)

    def setupRatingMenu(self, editMenu):
        def setRating(rating):
            self.curScene.setRating(rating)
            self.update()

        ratingGroup = QActionGroup(self)
        for rating in range(1, 5):
            ratingAction = QAction('Rating %s' % RatingMap[rating], self)
            ratingAction.setShortcut('%d' % rating)
            ratingAction.setCheckable(True)
            ratingAction.triggered.connect(
                lambda _, rating=rating: setRating(rating))
            ratingGroup.addAction(ratingAction)
            editMenu.addAction(ratingAction)

            def update(ratingAction=ratingAction, rating=rating):
                ratingAction.setChecked(self.curScene.getRawRating() == rating)

            editMenu.aboutToShow.connect(update)

        def setGlobalRating(rating):
            self._globalRating = rating

        ratingGroup = QActionGroup(self)
        editMenu.addSeparator()
        for rating in range(1, 5):
            ratingAction = QAction('Global Rating %s' % RatingMap[rating],
                                   self)
            ratingAction.setShortcut('Ctrl+%d' % rating)
            ratingAction.setCheckable(True)
            ratingAction.triggered.connect(
                lambda _, rating=rating: setGlobalRating(rating))
            ratingGroup.addAction(ratingAction)
            editMenu.addAction(ratingAction)

            def update(ratingAction=ratingAction, rating=rating):
                ratingAction.setChecked(self._globalRating == rating)

            editMenu.aboutToShow.connect(update)

    def setupRepickMenu(self, editMenu):
        repickMenu = editMenu.addMenu('&Repick')
        for faceNum in range(1, 6):
            repickAction = QAction('Repick %d' % faceNum, self)
            repickAction.setShortcut('Ctrl+Shift+%d' % faceNum)
            repickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, False))
            repickMenu.addAction(repickAction)

            repickAction = QAction('Repick %d (Debug)' % faceNum, self)
            repickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, True))
            repickMenu.addAction(repickAction)

    def setupModifyMenu(self, editMenu):
        deleteSceneAction = QAction('&Delete Scene', self)
        deleteSceneAction.setShortcut('Ctrl+Shift+Delete')
        deleteSceneAction.triggered.connect(self.deleteScenen)
        editMenu.addAction(deleteSceneAction)

    def refresh(self):
        self._sidx = 0
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()

    def setViewMode(self, viewMode):
        if self._viewMode == viewMode:
            if self._viewMode == ViewMode.SELECT:
                self._viewMode = self._lastViewMode
                self._lastViewMode = ViewMode.SELECT
                self.update()
        else:
            self._lastViewMode = self._viewMode
            self._viewMode = viewMode
            self.update()

    def setLockViewMode(self, viewMode):
        self._lockViewMode = viewMode
        self.setViewMode(viewMode)

    def selectImage(self):
        if self._viewMode == ViewMode.SELECT:
            self.setViewMode(self._lastViewMode)
        else:
            if self.curImage:
                self._aidx, self._iidx = self.curScene.indexImage(
                    self.curImage)
            self.setViewMode(ViewMode.SELECT)

    def showNextImage(self):
        action = self.curAction
        if not action:
            return
        if self._viewMode == ViewMode.SELECT:
            self._iidx = action.normalizeImageIdx(self._iidx + 1)
        elif self._viewMode == ViewMode.PICK:
            self._pidx = action.normalizeImageIdx(self._pidx + 1, loop=True)
            if self._pidx == 0:
                self.showHomeFlag()
        elif self._viewMode == ViewMode.LOVE:
            self._lidx = action.normalizeImageIdx(self._lidx + 1, loop=True)
            if self._lidx == 0:
                self.showHomeFlag()
        self.update()

    def showPrevImage(self):
        action = self.curAction
        if not action:
            return
        if self._viewMode == ViewMode.SELECT:
            self._iidx = action.normalizeImageIdx(self._iidx - 1)
        elif self._viewMode == ViewMode.PICK:
            self._pidx = action.normalizeImageIdx(self._pidx - 1, loop=True)
            if self._pidx == 0:
                self.showHomeFlag()
        elif self._viewMode == ViewMode.LOVE:
            self._lidx = action.normalizeImageIdx(self._lidx - 1, loop=True)
            if self._lidx == 0:
                self.showHomeFlag()
        self.update()

    def showNextAction(self):
        if self._viewMode != ViewMode.SELECT:
            return
        self._iidx = 0
        self._aidx = self.curScene.normalizeActionIdx(
            self._aidx + 1, loop=True)
        if self._aidx == 0:
            self.showHomeFlag()
        self.update()

    def showPrevAction(self):
        if self._viewMode != ViewMode.SELECT:
            return
        self._iidx = 0
        self._aidx = self.curScene.normalizeActionIdx(
            self._aidx - 1, loop=True)
        if self._aidx == 0:
            self.showHomeFlag()
        self.update()

    def showNextScene(self):
        self._viewMode = self._lockViewMode
        self._sidx = data.normalizeSceneIdx(self._sidx + 1)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.saveDatabase()
        self.update()

    def showPrevScene(self):
        self._viewMode = self._lockViewMode
        self._sidx = data.normalizeSceneIdx(self._sidx - 1)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.saveDatabase()
        self.update()

    def togglePick(self):
        image = self.curImage
        if not image:
            return
        pick = self.curPick
        if pick.hasImage(image):
            pick.delImage(image)
            self._pidx = pick.normalizeImageIdx(self._pidx)
        else:
            pick.addImage(image)
        self.update()

    def toggleLove(self):
        image = self.curImage
        if not image:
            return
        love = self.curLove
        if love.hasImage(image):
            love.delImage(image)
            self._lidx = love.normalizeImageIdx(self._lidx)
        else:
            love.addImage(image)
            if self.curScene.getRawRating() == 0:
                self.curScene.setRating(self._globalRating)
        self.update()

    def repickScene(self, faceNum, debug):
        from tools.picker import repickScene
        images = self.curScene.getImages()
        sceneProto = repickScene(images, faceNum, debug)
        self.curScene.load(sceneProto)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self.update()

    def deleteScenen(self):
        data.delScene(self.curScene)
        self._sidx = data.normalizeSceneIdx(self._sidx)
        self.update()

    def saveDatabase(self):
        self._saveCounter += 1
        if self._saveCounter % 5 == 0:
            data.save()

    def showHomeFlag(self):
        self.home.setVisible(True)
        cw = self.imgFrame.width()
        ch = self.imgFrame.height()
        hw = self.home.width()
        hh = self.home.height()
        self.home.move(QPoint((cw - hw) / 2, (ch - hh) / 2))
        QTimer.singleShot(200, lambda: self.home.setVisible(False))

    def update(self):
        self._updateActionNum()
        self._updateFaceCtrls()
        self._updateImageCtrl()
        self._updateWindowTitle()

    def _updateActionNum(self):
        if (self._viewMode == ViewMode.SELECT):
            self.actionNum.setText('%d/%d' % (self._aidx + 1,
                                              self.curScene.getActionNum()))
        else:
            self.actionNum.setText('')

    def _updateFaceCtrls(self):
        if self.curAction is None:
            self.faceFrame.setVisible(False)
            return
        self.faceFrame.setVisible(True)

        for ctrl in self._faceCtrls:
            ctrl.setVisible(False)

        actionIdx = 0
        for idx in range(self.curAction.getImageNum()):
            if idx >= len(self._faceCtrls):
                ctrl = Face(self.faces)
                self.faceLayout.addWidget(ctrl)
                self._faceCtrls.append(ctrl)
            else:
                ctrl = self._faceCtrls[idx]
                ctrl.setVisible(True)
            image = self.curAction.getImage(idx)
            ctrl.setFace(image, self.curScene.getFaces())
            if self.curImage == image:
                ctrl.selected(True)
                selected_ctrl = ctrl
            else:
                ctrl.selected(False)
            ctrl.star.setVisible(self.curPick.hasImage(image))
            ctrl.circle.setVisible(self.curLove.hasImage(image))
            if self._viewMode != ViewMode.SELECT:
                action = self.curScene.getAction(actionIdx)
                while action.indexImage(image) is None:
                    actionIdx += 1
                    action = self.curScene.getAction(actionIdx)
                ctrl.starNum.setText(str(action.getImageNum()))
            else:
                ctrl.starNum.setText('')
        hbar = self.faceFrame.horizontalScrollBar()
        hbarVal = selected_ctrl.pos().x() - self.faceFrame.width(
        ) / 2 + selected_ctrl.width() / 2
        hbar.setValue(hbarVal)

    def _updateImageCtrl(self):
        if self.curImage is None:
            self.imgFrame.setVisible(False)
            return
        self.imgFrame.setVisible(True)
        pixmap = QPixmap(self.curImage)
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
        QtWidgets.QLabel.paintEvent(self.img, event)

    def _updateWindowTitle(self):
        ratingStr = RatingMap[self.curScene.getRating()]
        if self._viewMode == ViewMode.SELECT:
            viewModeStr = 'SELECT'
        elif self._viewMode == ViewMode.PICK:
            viewModeStr = 'PICK'
        elif self._viewMode == ViewMode.LOVE:
            viewModeStr = 'LOVE'
        self.window().setWindowTitle(u'CGPicker 《%s》[%d/%d] (%s) %s' %
                                     (data.getCGName(), self._sidx + 1,
                                      data.getSceneNum(), ratingStr,
                                      viewModeStr))
