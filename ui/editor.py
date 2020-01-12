#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QActionGroup
from PyQt5.QtCore import QPoint, QSize, QRect, QTimer, Qt
from PyQt5.QtGui import QPixmap, QPen, QPainter
from template.ui_editor import Ui_Editor

from ui.face import Face

from common import macro


class ViewMode(Enum):
    PICK = 1
    LOVE = 2


class Editor(QWidget, Ui_Editor):

    def __init__(self, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.faceContainer.resizeEvent = self._onFaceContainerResize
        self.faceLayout = QHBoxLayout(self.faceContainer)
        self.faceLayout.setSpacing(3)
        self.home.setVisible(False)
        self.actionNum.setStyleSheet('font-size:30px')
        self.actionNum.setText('number')

        self._viewMenu = None
        self._editMenu = None
        self._imageCtrlHandler = ImageCtrlHandler(self.imgFrame)
        self._faceCtrls = []

    def init(self, database, sceneIdx):
        self._database = database

        self._globalRating = 2

        self.refresh(sceneIdx)

    def refresh(self, sceneIdx=0):
        self._viewMode = ViewMode.PICK
        self._lockViewMode = ViewMode.PICK
        self._selectingMode = False
        self._saveCounter = 0

        self._sidx = self._database.normalizeSceneIdx(sceneIdx)
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0

        self._update()

    def setVisible(self, isVisible):
        super(Editor, self).setVisible(isVisible)
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

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            facesProto = self._imageCtrlHandler.stopDrawing()
            if facesProto:
                self.repickSceneWithFaces(facesProto)
                event.accept()

    def setupMainMenu(self, menubar):
        # View menu
        viewMenu = menubar.addMenu('&View')
        self._viewMenu = viewMenu
        self.setupViewModeMenu(viewMenu)

        viewMenu.addSeparator()
        self.setupLockViewModeMenu(viewMenu)

        viewMenu.addSeparator()
        self.setupNavigatorMenu(viewMenu)

        # Edit menu
        editMenu = menubar.addMenu('&Edit')
        self._editMenu = editMenu
        self.setupToggleMenu(editMenu)

        editMenu.addSeparator()
        self.setupRatingMenu(editMenu)

        editMenu.addSeparator()
        self.setupRepickMenu(editMenu)

        editMenu.addSeparator()
        self.setupModifyMenu(editMenu)

        #  Refresh visibility
        self._setMenuEnabled(self.isVisible())

    def setupViewModeMenu(self, viewMenu):
        pickViewAction = viewMenu.addAction('Pick View')
        pickViewAction.setCheckable(True)
        pickViewAction.triggered.connect(lambda: self.setViewMode(ViewMode.PICK))

        loveViewAction = viewMenu.addAction('Love View')
        loveViewAction.setCheckable(True)
        loveViewAction.triggered.connect(lambda: self.setViewMode(ViewMode.LOVE))

        viewModeGroup = QActionGroup(viewMenu)
        viewModeGroup.addAction(pickViewAction)
        viewModeGroup.addAction(loveViewAction)

        def update():
            if self._viewMode == ViewMode.PICK:
                pickViewAction.setChecked(True)
            elif self._viewMode == ViewMode.LOVE:
                loveViewAction.setChecked(True)
            else:
                print('Invalid view mode')

        viewMenu.aboutToShow.connect(update)

        swtichViewAction = viewMenu.addAction('Switch View')
        swtichViewAction.setShortcut('Q')
        swtichViewAction.setAutoRepeat(False)
        swtichViewAction.triggered.connect(self.switchViewMode)

    def setupLockViewModeMenu(self, viewMenu):
        lockPickViewAction = viewMenu.addAction('Lock Pick View')
        lockPickViewAction.setCheckable(True)
        lockPickViewAction.triggered.connect(lambda: self.setLockViewMode(ViewMode.PICK))

        lockLoveViewAction = viewMenu.addAction('Lock Love View')
        lockLoveViewAction.setCheckable(True)
        lockLoveViewAction.triggered.connect(lambda: self.setLockViewMode(ViewMode.LOVE))

        lockViewModeGroup = QActionGroup(viewMenu)
        lockViewModeGroup.addAction(lockPickViewAction)
        lockViewModeGroup.addAction(lockLoveViewAction)

        def update():
            if self._lockViewMode == ViewMode.PICK:
                lockPickViewAction.setChecked(True)
            elif self._lockViewMode == ViewMode.LOVE:
                lockLoveViewAction.setChecked(True)
            else:
                print('Invalid view mode')

        viewMenu.aboutToShow.connect(update)

        swtichLockViewAction = viewMenu.addAction('Switch Lock View')
        swtichLockViewAction.setShortcut('Ctrl+Q')
        swtichLockViewAction.setAutoRepeat(False)
        swtichLockViewAction.triggered.connect(self.switchLockViewMode)

    def setupNavigatorMenu(self, viewMenu):
        prevImageAction = viewMenu.addAction('Prev Image')
        prevImageAction.setShortcuts(['Left', 'A'])
        prevImageAction.triggered.connect(self.showPrevImage)

        nextImageAction = viewMenu.addAction('Next Image')
        nextImageAction.setShortcuts(['Right', 'D'])
        nextImageAction.triggered.connect(self.showNextImage)

        viewMenu.addSeparator()

        prevSceneAction = viewMenu.addAction('Prev Scene')
        prevSceneAction.setShortcuts(['Up', 'W'])
        prevSceneAction.triggered.connect(self.showPrevScene)

        nextSceneAction = viewMenu.addAction('Next Scene')
        nextSceneAction.setShortcuts(['Down', 'S'])
        nextSceneAction.triggered.connect(self.showNextScene)

    def setupToggleMenu(self, editMenu):
        toggleSelectingModeAction = editMenu.addAction('&Selecting Mode')
        toggleSelectingModeAction.setShortcut('Space')
        toggleSelectingModeAction.setAutoRepeat(False)
        toggleSelectingModeAction.setCheckable(True)
        toggleSelectingModeAction.triggered.connect(self.toggleSelectingMode)

        def update():
            toggleSelectingModeAction.setChecked(self._selectingMode)

        editMenu.aboutToShow.connect(update)

        toggleLoveAction = editMenu.addAction('Toggle Love')
        toggleLoveAction.setShortcut('F')
        toggleLoveAction.setAutoRepeat(False)
        toggleLoveAction.triggered.connect(self.toggleLove)

    def setupRatingMenu(self, editMenu):
        ratingGroup = QActionGroup(editMenu)
        for rating in range(0, 5):
            ratingAction = editMenu.addAction('Rating %s' % macro.RATING_MAP[rating])
            ratingAction.setShortcut('%d' % rating)
            ratingAction.setAutoRepeat(False)
            ratingAction.setCheckable(True)
            ratingAction.triggered.connect(lambda _, rating=rating: self.setRating(rating))
            ratingGroup.addAction(ratingAction)

            def update(ratingAction=ratingAction, rating=rating):
                checked = self.curScene.getRawRating() == rating if self.curScene else False
                ratingAction.setChecked(checked)

            editMenu.aboutToShow.connect(update)

        editMenu.addSeparator()

        ratingGroup = QActionGroup(editMenu)
        for rating in range(0, 5):
            ratingAction = editMenu.addAction('Global Rating %s' % macro.RATING_MAP[rating])
            ratingAction.setShortcut('Ctrl+%d' % rating)
            ratingAction.setAutoRepeat(False)
            ratingAction.setCheckable(True)
            ratingAction.triggered.connect(lambda _, rating=rating: self.setGlobalRating(rating))
            ratingGroup.addAction(ratingAction)

            def update(ratingAction=ratingAction, rating=rating):
                ratingAction.setChecked(self._globalRating == rating)

            editMenu.aboutToShow.connect(update)

    def setupRepickMenu(self, editMenu):
        repickMenu = editMenu.addMenu('&Repick')

        repickAction = repickMenu.addAction('Repick 0')
        repickAction.setShortcut('Ctrl+Shift+9')
        repickAction.setAutoRepeat(False)
        repickAction.triggered.connect(lambda: self.repickScene(0, False))

        for faceNum in range(1, 6):
            repickAction = repickMenu.addAction('Repick %d' % faceNum)
            repickAction.setShortcut('Ctrl+Shift+%d' % faceNum)
            repickAction.setAutoRepeat(False)
            repickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, False)
            )

            repickAction = repickMenu.addAction('Repick %d (Debug)' % faceNum)
            repickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, True)
            )

    def setupModifyMenu(self, editMenu):
        moveActionForwardAction = editMenu.addAction('Move Action Forward')
        moveActionForwardAction.setShortcut('Ctrl+Shift+Left')
        moveActionForwardAction.setAutoRepeat(False)
        moveActionForwardAction.triggered.connect(self.moveActionForward)

        moveActionBackwardAction = editMenu.addAction('Move Action Backward')
        moveActionBackwardAction.setShortcut('Ctrl+Shift+Right')
        moveActionBackwardAction.setAutoRepeat(False)
        moveActionBackwardAction.triggered.connect(self.moveActionBackward)

        deleteActionAction = editMenu.addAction('Delete Action')
        deleteActionAction.setShortcut('Ctrl+Shift+Backspace')
        deleteActionAction.setAutoRepeat(False)
        deleteActionAction.triggered.connect(self.deleteAction)

        editMenu.addSeparator()

        moveSceneForwardAction = editMenu.addAction('Move Scene Forward')
        moveSceneForwardAction.setShortcut('Ctrl+Shift+Up')
        moveSceneForwardAction.setAutoRepeat(False)
        moveSceneForwardAction.triggered.connect(self.moveSceneForward)

        moveSceneBackwardAction = editMenu.addAction('Move Scene Backward')
        moveSceneBackwardAction.setShortcut('Ctrl+Shift+Down')
        moveSceneBackwardAction.setAutoRepeat(False)
        moveSceneBackwardAction.triggered.connect(self.moveSceneBackward)

        deleteSceneAction = editMenu.addAction('Delete Scene')
        deleteSceneAction.setShortcut('Ctrl+Shift+Delete')
        deleteSceneAction.setAutoRepeat(False)
        deleteSceneAction.triggered.connect(self.deleteScene)

        splitSceneAction = editMenu.addAction('Split Scene')
        splitSceneAction.setShortcut('Ctrl+Shift+\\')
        splitSceneAction.setAutoRepeat(False)
        splitSceneAction.triggered.connect(self.splitScene)

        mergeSceneAction = editMenu.addAction('Merge Scene')
        mergeSceneAction.setShortcut('Ctrl+Shift+M')
        mergeSceneAction.setAutoRepeat(False)
        mergeSceneAction.triggered.connect(self.mergeScene)

    @property
    def curScene(self):
        return self._database and self._database.getScene(self._sidx)

    @property
    def curSceneIdx(self):
        return self._sidx

    @property
    def curAction(self):
        scene = self.curScene
        if not scene:
            return None
        if self._viewMode == ViewMode.PICK:
            return scene.getAction(self._pidx)
        elif self._viewMode == ViewMode.LOVE:
            return scene.getLoveAction(self._lidx)
        return None

    @property
    def curImage(self):
        action = self.curAction
        if not action:
            return
        if self._selectingMode:
            return action.getImage(self._iidx)
        else:
            if self._viewMode == ViewMode.PICK:
                return action.getPick()
            elif self._viewMode == ViewMode.LOVE:
                return action.getPick()
        return None

    def isInvalid(self):
        return self.curScene is None

    def setViewMode(self, viewMode):
        if self._selectingMode:
            return
        self._viewMode = viewMode
        self._update()

    def switchViewMode(self):
        if self._selectingMode:
            self._selectingMode = False
            self._update()
            return
        if self._viewMode == ViewMode.PICK:
            self.setViewMode(ViewMode.LOVE)
        elif self._viewMode == ViewMode.LOVE:
            self.setViewMode(ViewMode.PICK)
        else:
            print('Invalid view mode')

    def setLockViewMode(self, viewMode):
        if self._selectingMode:
            return
        self._lockViewMode = viewMode
        self.setViewMode(viewMode)

    def switchLockViewMode(self):
        if self._lockViewMode == ViewMode.PICK:
            self.setLockViewMode(ViewMode.LOVE)
        elif self._viewMode == ViewMode.LOVE:
            self.setLockViewMode(ViewMode.PICK)
        else:
            print('Invalid view mode')

    def toggleSelectingMode(self):
        if self.isInvalid() or self.curImage is None:
            return
        if self._selectingMode:
            if self._viewMode == ViewMode.PICK:
                self.curAction.setPick(self.curImage)
            elif self._viewMode == ViewMode.LOVE:
                self.curAction.setPick(self.curImage)
            else:
                print('Invalid view mode')
        else:
            self._iidx = self.curAction.indexImage(self.curImage)
        self._selectingMode = not self._selectingMode
        self._update()

    def showPrevImage(self):
        if self.isInvalid():
            return
        if self._selectingMode:
            self._iidx = self.curAction.normalizeImageIdx(self._iidx - 1)
        else:
            if self._viewMode == ViewMode.PICK:
                self._pidx = self.curScene.normalizeActionIdx(self._pidx - 1, loop=True)
                if self._pidx == 0:
                    self.showHomeFlag()
            elif self._viewMode == ViewMode.LOVE:
                self._lidx = self.curScene.normalizeLoveActionIdx(self._lidx - 1, loop=True)
                if self._lidx == 0:
                    self.showHomeFlag()
            else:
                print('Invalid view mode')
        self._update()

    def showNextImage(self):
        if self.isInvalid():
            return
        if self._selectingMode:
            self._iidx = self.curAction.normalizeImageIdx(self._iidx + 1)
        else:
            if self._viewMode == ViewMode.PICK:
                self._pidx = self.curScene.normalizeActionIdx(self._pidx + 1, loop=True)
                if self._pidx == 0:
                    self.showHomeFlag()
            elif self._viewMode == ViewMode.LOVE:
                self._lidx = self.curScene.normalizeLoveActionIdx(self._lidx + 1, loop=True)
                if self._lidx == 0:
                    self.showHomeFlag()
            else:
                print('Invalid view mode')
        self._update()

    def showPrevScene(self):
        if self.isInvalid():
            return
        self._viewMode = self._lockViewMode
        self._selectingMode = False
        self._sidx = self._database.normalizeSceneIdx(self._sidx - 1)
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._imageCtrlHandler.stopDrawing()
        self.saveDatabase()
        self._update()

    def showNextScene(self):
        if self.isInvalid():
            return
        self._viewMode = self._lockViewMode
        self._selectingMode = False
        self._sidx = self._database.normalizeSceneIdx(self._sidx + 1)
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._imageCtrlHandler.stopDrawing()
        self.saveDatabase()
        self._update()

    def toggleLove(self):
        if self.isInvalid() or self.curImage is None or self._selectingMode:
            return
        action = self.curAction
        if action.isLove():
            action.setLove(False)
        else:
            action.setLove(True)
            if self.curScene.getRawRating() < 0:
                self.curScene.setRating(self._globalRating)
        self._lidx = self.curScene.normalizeLoveActionIdx(self._lidx)
        self._update()

    def setRating(self, rating):
        if self.isInvalid():
            return
        self.curScene.setRating(rating)
        self._update()

    def setGlobalRating(self, rating):
        self._globalRating = rating
        self.setRating(rating)

    def repickScene(self, faceNum, debug):
        if self.isInvalid():
            return
        from tools.picker import repickScene
        self._repickSceneWithFunction(lambda images: repickScene(images, faceNum, debug))

    def repickSceneWithFaces(self, facesProto):
        if self.isInvalid():
            return
        from tools.picker import repickSceneWithFaces
        self._repickSceneWithFunction(lambda images: repickSceneWithFaces(images, facesProto))

    def _repickSceneWithFunction(self, pickFunc):
        rating = self.curScene.getRawRating()
        images = []
        loves = []
        for action in self.curScene.getActions():
            images += action.getImages()
            if action.isLove():
                loves.append(action.getPick())
        sceneProto = pickFunc(images)
        self.curScene.load(sceneProto)
        self.curScene.setRating(rating)
        for love in loves:
            for action in self.curScene.getActions():
                if action.hasImage(love):
                    action.setLove(True)
                    action.setPick(love)
        self._selectingMode = False
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._update()

    def moveActionForward(self):
        if self.isInvalid() or self._viewMode != ViewMode.PICK or self._selectingMode:
            return
        action = self.curScene.getAction(self._pidx)
        self.curScene.moveActionForward(action)
        self._pidx = self.curScene.normalizeActionIdx(self._pidx - 1)
        self._update()

    def moveActionBackward(self):
        if self.isInvalid() or self._viewMode != ViewMode.PICK or self._selectingMode:
            return
        action = self.curScene.getAction(self._pidx)
        self.curScene.moveActionBackward(action)
        self._pidx = self.curScene.normalizeActionIdx(self._pidx + 1)
        self._update()

    def deleteAction(self):
        if self.isInvalid() or self._viewMode != ViewMode.PICK or self._selectingMode:
            return
        action = self.curScene.getAction(self._pidx)
        if self.curScene.delAction(action):
            self._pidx = self.curScene.normalizeActionIdx(self._pidx)
            self._update()
        else:
            self.deleteScene()

    def moveSceneForward(self):
        if self.isInvalid():
            return
        self._database.moveSceneForward(self.curScene)
        self._sidx = self._database.normalizeSceneIdx(self._sidx - 1)
        self._update()

    def moveSceneBackward(self):
        if self.isInvalid():
            return
        self._database.moveSceneBackward(self.curScene)
        self._sidx = self._database.normalizeSceneIdx(self._sidx + 1)
        self._update()

    def deleteScene(self):
        if self.isInvalid():
            return
        self._database.delScene(self.curScene)
        self._updateCurScene()

    def splitScene(self):
        if self.isInvalid() or self._viewMode != ViewMode.PICK or self._selectingMode:
            return
        action = self.curScene.getAction(self._pidx)
        if self._database.splitScene(self.curScene, action):
            self._sidx += 1
            self._updateCurScene()

    def mergeScene(self):
        if self.isInvalid():
            return
        if self._database.mergeScene(self.curScene):
            self._sidx -= 1
            self._updateCurScene()

    def _updateCurScene(self):
        self._viewMode = self._lockViewMode
        self._selectingMode = False
        self._sidx = self._database.normalizeSceneIdx(self._sidx)
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._imageCtrlHandler.stopDrawing()
        self._update()

    def saveDatabase(self):
        self._saveCounter += 1
        if self._saveCounter % 10 == 0:
            self._database.save()

    def showHomeFlag(self):
        self.home.setVisible(True)
        cw = self.imgFrame.width()
        ch = self.imgFrame.height()
        hw = self.home.width()
        hh = self.home.height()
        self.home.move(QPoint((cw - hw) / 2, (ch - hh) / 2))
        QTimer.singleShot(200, lambda: self.home.setVisible(False))

    def _update(self):
        self._updateWindowTitle()
        self._updateImageCtrl()
        self._updateActionNum()
        self._updateFaceCtrls()

    def _updateWindowTitle(self):
        from PyQt5.QtCore import QCoreApplication
        applicationName = QCoreApplication.applicationName()
        if self.isInvalid():
            self.window().setWindowTitle(applicationName)
            return
        viewModeStr = ''
        if self._viewMode == ViewMode.PICK:
            viewModeStr = 'PICK'
        elif self._viewMode == ViewMode.LOVE:
            viewModeStr = 'LOVE'
        if self._selectingMode:
            selectingStr = 'selecting'
        else:
            selectingStr = ''
        self.window().setWindowTitle(
            u'%s 《%s》[%d/%d] %s %s' % (
                applicationName, self._database.getCGName(), self._sidx + 1,
                self._database.getSceneNum(), viewModeStr, selectingStr
            )
        )

    def _updateImageCtrl(self):
        if self.isInvalid():
            self.imgFrame.setVisible(False)
            return
        self.imgFrame.setVisible(True)
        pixmap = None
        if self.curImage is None:
            self.img.setEnabled(False)
            firstImage = self.curScene.getAction(0).getImage(0)
            pixmap = QPixmap(firstImage)
        else:
            self.img.setEnabled(True)
            pixmap = QPixmap(self.curImage)
        self.img.setPixmap(pixmap)
        self.rating.setText(macro.RATING_MAP[self.curScene.getRating()])

    def _updateActionNum(self):
        if self.isInvalid() or self.curImage is None:
            self.actionNum.setText('')
            return
        if self._selectingMode:
            self.actionNum.setText('%d/%d SELECT' % (self._iidx + 1, self.curAction.getImageNum()))
        else:
            if self._viewMode == ViewMode.PICK:
                self.actionNum.setText(
                    '%d/%d PICK' % (self._pidx + 1, self.curScene.getActionNum())
                )
            elif self._viewMode == ViewMode.LOVE:
                self.actionNum.setText(
                    '%d/%d LOVE' % (self._lidx + 1, self.curScene.getLoveActionNum())
                )
            else:
                print('Invalid view mode')

    def _updateFaceCtrls(self):
        if self.isInvalid():
            self.faceFrame.setVisible(False)
            return
        self.faceFrame.setVisible(True)

        for ctrl in self._faceCtrls:
            ctrl.setVisible(False)

        if self._selectingMode:
            self._updateImageFaceCtrls()
        else:
            if self._viewMode == ViewMode.PICK:
                self._updatePickFaceCtrls()
            elif self._viewMode == ViewMode.LOVE:
                self._updateLoveFaceCtrls()
            else:
                print('Invalid view mode')

        self._updateScrollBar()

    def _getFaceCtrl(self, idx):
        ctrl = None
        if idx == len(self._faceCtrls):
            ctrl = Face(self.faceContainer)
            self.faceLayout.addWidget(ctrl)
            self._faceCtrls.append(ctrl)
        elif idx < len(self._faceCtrls):
            ctrl = self._faceCtrls[idx]
            ctrl.setVisible(True)
        else:
            print('Get face ctrl out of index')
        return ctrl

    def _updatePickFaceCtrls(self):
        for idx, action in enumerate(self.curScene.getActions()):
            ctrl = self._getFaceCtrl(idx)
            ctrl.setFace(action.getPick(), self.curScene.getFaces())
            ctrl.selected(self._pidx == idx)
            ctrl.star.setVisible(action.isLove())
            ctrl.circle.setVisible(False)
            ctrl.setText(str(action.getImageNum()))

    def _updateLoveFaceCtrls(self):
        for idx, action in enumerate(self.curScene.getLoveActions()):
            ctrl = self._getFaceCtrl(idx)
            ctrl.setFace(action.getPick(), self.curScene.getFaces())
            ctrl.selected(self._lidx == idx)
            ctrl.star.setVisible(action.isLove())
            ctrl.circle.setVisible(False)
            ctrl.setText(str(action.getImageNum()))

    def _updateImageFaceCtrls(self):
        selectedImage = self.curAction.getPick()
        for idx, image in enumerate(self.curAction.getImages()):
            ctrl = self._getFaceCtrl(idx)
            ctrl.setFace(image, self.curScene.getFaces())
            ctrl.selected(self._iidx == idx)
            ctrl.star.setVisible(False)
            ctrl.circle.setVisible(selectedImage == image)
            ctrl.setText('')

    def _onFaceContainerResize(self, event):
        self._updateScrollBar()

    def _updateScrollBar(self):
        selectedCtrl = None
        for ctrl in self._faceCtrls:
            if ctrl.getImage() == self.curImage:
                selectedCtrl = ctrl
                break
        if selectedCtrl is None:
            return
        hbar = self.faceFrame.horizontalScrollBar()
        hbarVal = selectedCtrl.pos().x() - self.faceFrame.width() / 2 + selectedCtrl.width() / 2
        hbar.setValue(hbarVal)


class ImageCtrlHandler(object):
    LINE_WIDTH = 3

    class FaceData(object):
        MIN_RADIUS = 10

        def __init__(self, center, imageCtrl):
            self.x = center.x()
            self.y = center.y()
            self.r = self.MIN_RADIUS
            self._ctrlSize = imageCtrl.size()
            self._imageSize = imageCtrl.pixmap().size()

        def onMove(self, pos):
            self.r = max(abs(pos.x() - self.x), abs(pos.y() - self.y), self.MIN_RADIUS)

        def serialize(self):
            left = max(0, self.x - self.r)
            right = min(self._ctrlSize.width(), self.x + self.r)
            top = max(0, self.y - self.r)
            bottom = min(self._ctrlSize.height(), self.y + self.r)
            widthFactor = self._imageSize.width() / self._ctrlSize.width()
            heightFactor = self._imageSize.height() / self._ctrlSize.height()
            return [
                left * widthFactor, top * heightFactor, right * widthFactor, bottom * heightFactor
            ]

    def __init__(self, frameCtrl):
        self.frameCtrl = frameCtrl
        self.frameCtrl.resizeEvent = self._onResize
        self.rating = frameCtrl.findChild(QLabel, 'rating')
        self.rating.paintEvent = self._paintRatingCtrl
        self.img = frameCtrl.findChild(QLabel, 'img')
        self.img.paintEvent = self._paintImgCtrl
        self.img.mousePressEvent = self._mousePressOnImgCtrl
        self.img.mouseReleaseEvent = self._mouseReleaseOnImgCtrl
        self.img.mouseMoveEvent = self._mouseMoveOnImgCtrl

        self._faces = []
        self._drawingFace = False

    def stopDrawing(self):
        facesProto = [face.serialize() for face in self._faces]
        self._faces.clear()
        self._drawingFace = False
        return facesProto

    def _onResize(self, event):
        self._updateRating(event)

    def _paintRatingCtrl(self, event):
        self._updateRating(event)
        QLabel.paintEvent(self.rating, event)

    def _paintImgCtrl(self, event):
        self._paintImage(event)
        self._paintFaces(event)

    def _paintImage(self, event):
        pw = self.img.pixmap().width()
        ph = self.img.pixmap().height()
        cw = self.img.parent().width()
        ch = self.img.parent().height()
        factor = min(cw / pw, ch / ph)
        self.img.resize(QSize(pw * factor, ph * factor))
        iw = self.img.width()
        ih = self.img.height()
        self.img.move(QPoint((cw - iw) / 2, (ch - ih) / 2))
        QLabel.paintEvent(self.img, event)

    def _paintFaces(self, event):
        painter = QPainter()
        painter.begin(self.img)
        painter.setPen(QPen(Qt.red, self.LINE_WIDTH, Qt.SolidLine))
        for face in self._faces:
            left = max(self.LINE_WIDTH // 2, face.x - face.r)
            right = min(self.img.width() - self.LINE_WIDTH, face.x + face.r)
            top = max(self.LINE_WIDTH // 2, face.y - face.r)
            bottom = min(self.img.height() - self.LINE_WIDTH, face.y + face.r)
            painter.drawRect(QRect(QPoint(left, top), QPoint(right, bottom)))
        painter.end()

    def _updateRating(self, event):
        rw = self.rating.width()
        rh = self.rating.height()
        cw = self.frameCtrl.width()
        ch = self.frameCtrl.height()
        self.rating.move(QPoint((cw - rw - 3), (ch - rh - 3)))

    def _mousePressOnImgCtrl(self, event):
        event.accept()
        if not (event.modifiers() & Qt.ControlModifier):
            return
        if event.button() == Qt.LeftButton:
            self._drawingFace = True
            self._faces.append(self.FaceData(event.pos(), self.img))
            self.img.repaint()
        elif event.button() == Qt.RightButton:
            self._drawingFace = False
            if self._faces:
                self._faces.pop()
                self.img.repaint()

    def _mouseReleaseOnImgCtrl(self, event):
        event.accept()
        if not (event.modifiers() & Qt.ControlModifier):
            return
        if event.button() == Qt.LeftButton:
            self._drawingFace = False

    def _mouseMoveOnImgCtrl(self, event):
        event.accept()
        if not (event.modifiers() & Qt.ControlModifier):
            return
        if self._drawingFace:
            face = self._faces[-1]
            face.onMove(event.pos())
            self.img.repaint()
