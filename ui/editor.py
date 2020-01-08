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
    SELECT = 1
    PICK = 2
    LOVE = 3


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

        self._viewMode = ViewMode.PICK
        self._lastViewMode = ViewMode.PICK
        self._lockViewMode = ViewMode.PICK
        self._globalRating = 2
        self._saveCounter = 0

        self._sidx = self._database.normalizeSceneIdx(sceneIdx)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0

        self._update()

    def refresh(self):
        self._viewMode = ViewMode.PICK
        self._lastViewMode = ViewMode.PICK
        self._lockViewMode = ViewMode.PICK
        self._globalRating = 2
        self._saveCounter = 0

        self._sidx = 0
        self._aidx = 0
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

    def isInvalid(self):
        return self.curAction is None

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
        normalViewAction = viewMenu.addAction('Normal View')
        normalViewAction.setShortcut('Q')
        normalViewAction.setCheckable(True)
        normalViewAction.triggered.connect(lambda: self.setViewMode(ViewMode.SELECT))

        pickViewAction = viewMenu.addAction('Pick View')
        pickViewAction.setShortcut('W')
        pickViewAction.setCheckable(True)
        pickViewAction.triggered.connect(lambda: self.setViewMode(ViewMode.PICK))

        loveViewAction = viewMenu.addAction('Love View')
        loveViewAction.setShortcut('E')
        loveViewAction.setCheckable(True)
        loveViewAction.triggered.connect(lambda: self.setViewMode(ViewMode.LOVE))

        viewModeGroup = QActionGroup(viewMenu)
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
        lockNormalViewAction = viewMenu.addAction('Lock Normal View')
        lockNormalViewAction.setShortcut('Ctrl+Q')
        lockNormalViewAction.setCheckable(True)
        lockNormalViewAction.triggered.connect(lambda: self.setLockViewMode(ViewMode.SELECT))

        lockPickViewAction = viewMenu.addAction('Lock Pick View')
        lockPickViewAction.setShortcut('Ctrl+W')
        lockPickViewAction.setCheckable(True)
        lockPickViewAction.triggered.connect(lambda: self.setLockViewMode(ViewMode.PICK))

        lockLoveViewAction = viewMenu.addAction('Lock Love View')
        lockLoveViewAction.setShortcut('Ctrl+E')
        lockLoveViewAction.setCheckable(True)
        lockLoveViewAction.triggered.connect(lambda: self.setLockViewMode(ViewMode.LOVE))

        lockViewModeGroup = QActionGroup(viewMenu)
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
        selectImageAction = viewMenu.addAction('&Select Image')
        selectImageAction.setShortcut('Space')
        selectImageAction.triggered.connect(self.selectImage)

        viewMenu.addSeparator()

        nextImageAction = viewMenu.addAction('Next Image')
        nextImageAction.setShortcut('Right')
        nextImageAction.triggered.connect(self.showNextImage)

        prevImageAction = viewMenu.addAction('Prev Image')
        prevImageAction.setShortcut('Left')
        prevImageAction.triggered.connect(self.showPrevImage)

        viewMenu.addSeparator()

        nextActionAction = viewMenu.addAction('Next Action')
        nextActionAction.setShortcut('Down')
        nextActionAction.triggered.connect(self.showNextAction)

        prevActionAction = viewMenu.addAction('Prev Action')
        prevActionAction.setShortcut('Up')
        prevActionAction.triggered.connect(self.showPrevAction)

        viewMenu.addSeparator()

        nextSceneAction = viewMenu.addAction('Next Scene')
        nextSceneAction.setShortcut('Ctrl+Down')
        nextSceneAction.triggered.connect(self.showNextScene)

        prevSceneAction = viewMenu.addAction('Prev Scene')
        prevSceneAction.setShortcut('Ctrl+Up')
        prevSceneAction.triggered.connect(self.showPrevScene)

    def setupToggleMenu(self, editMenu):
        togglePickAction = editMenu.addAction('Toggle Pick')
        togglePickAction.setShortcut('Tab')
        togglePickAction.triggered.connect(self.togglePick)

        toggleLoveAction = editMenu.addAction('Toggle Love')
        toggleLoveAction.setShortcut('Ctrl+Tab')
        toggleLoveAction.triggered.connect(self.toggleLove)

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

        editMenu.addSeparator()

        def setGlobalRating(rating):
            self._globalRating = rating

        ratingGroup = QActionGroup(editMenu)
        for rating in range(1, 5):
            ratingAction = editMenu.addAction('Global Rating %s' % macro.RATING_MAP[rating])
            ratingAction.setShortcut('Ctrl+%d' % rating)
            ratingAction.setCheckable(True)
            ratingAction.triggered.connect(lambda _, rating=rating: setGlobalRating(rating))
            ratingGroup.addAction(ratingAction)

            def update(ratingAction=ratingAction, rating=rating):
                ratingAction.setChecked(self._globalRating == rating)

            editMenu.aboutToShow.connect(update)

    def setupRepickMenu(self, editMenu):
        repickMenu = editMenu.addMenu('&Repick')

        repickAction = repickMenu.addAction('Repick 0')
        repickAction.setShortcut('Ctrl+Shift+9')
        repickAction.triggered.connect(lambda: self.repickScene(0, False))

        for faceNum in range(1, 6):
            repickAction = repickMenu.addAction('Repick %d' % faceNum)
            repickAction.setShortcut('Ctrl+Shift+%d' % faceNum)
            repickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, False)
            )

            repickAction = repickMenu.addAction('Repick %d (Debug)' % faceNum)
            repickAction.triggered.connect(
                lambda _, faceNum=faceNum: self.repickScene(faceNum, True)
            )

    def setupModifyMenu(self, editMenu):
        moveForwardAction = editMenu.addAction('Move Action Forward')
        moveForwardAction.setShortcut('Ctrl+Shift+Up')
        moveForwardAction.triggered.connect(self.moveActionForward)

        moveBackwardAction = editMenu.addAction('Move Action Backward')
        moveBackwardAction.setShortcut('Ctrl+Shift+Down')
        moveBackwardAction.triggered.connect(self.moveActionBackward)

        deleteSceneAction = editMenu.addAction('Delete Scene')
        deleteSceneAction.setShortcut('Ctrl+Shift+Delete')
        deleteSceneAction.triggered.connect(self.deleteScenen)

    def setViewMode(self, viewMode):
        if self._viewMode == viewMode:
            if self._viewMode == ViewMode.SELECT:
                self._viewMode = self._lastViewMode
                self._lastViewMode = ViewMode.SELECT
                self._update()
        else:
            self._lastViewMode = self._viewMode
            self._viewMode = viewMode
            self._update()

    def setLockViewMode(self, viewMode):
        self._lockViewMode = viewMode
        self.setViewMode(viewMode)

    def selectImage(self):
        if self._viewMode == ViewMode.SELECT:
            self.setViewMode(self._lastViewMode)
        else:
            if self.curImage is not None:
                self._aidx, self._iidx = self.curScene.indexImage(self.curImage)
            self.setViewMode(ViewMode.SELECT)

    def showNextImage(self):
        if self.isInvalid():
            return
        action = self.curAction
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
        self._update()

    def showPrevImage(self):
        if self.isInvalid():
            return
        action = self.curAction
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
        self._update()

    def showNextAction(self):
        if self.isInvalid() or self._viewMode != ViewMode.SELECT:
            return
        self._iidx = 0
        self._aidx = self.curScene.normalizeActionIdx(self._aidx + 1, loop=True)
        if self._aidx == 0:
            self.showHomeFlag()
        self._update()

    def showPrevAction(self):
        if self.isInvalid() or self._viewMode != ViewMode.SELECT:
            return
        self._iidx = 0
        self._aidx = self.curScene.normalizeActionIdx(self._aidx - 1, loop=True)
        if self._aidx == 0:
            self.showHomeFlag()
        self._update()

    def showNextScene(self):
        if self.isInvalid():
            return
        self._viewMode = self._lockViewMode
        self._sidx = self._database.normalizeSceneIdx(self._sidx + 1)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._imageCtrlHandler.stopDrawing()
        self.saveDatabase()
        self._update()

    def showPrevScene(self):
        if self.isInvalid():
            return
        self._viewMode = self._lockViewMode
        self._sidx = self._database.normalizeSceneIdx(self._sidx - 1)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._imageCtrlHandler.stopDrawing()
        self.saveDatabase()
        self._update()

    def togglePick(self):
        if self.isInvalid() or self.curImage is None:
            return
        image = self.curImage
        pick = self.curPick
        if pick.hasImage(image):
            pick.delImage(image)
            self._pidx = pick.normalizeImageIdx(self._pidx)
        else:
            pick.addImage(image)
        self._update()

    def toggleLove(self):
        if self.isInvalid() or self.curImage is None:
            return
        image = self.curImage
        love = self.curLove
        if love.hasImage(image):
            love.delImage(image)
            self._lidx = love.normalizeImageIdx(self._lidx)
        else:
            love.addImage(image)
            if self.curScene.getRawRating() == 0:
                self.curScene.setRating(self._globalRating)
        self._update()

    def setRating(self, rating):
        if self.isInvalid():
            return
        self.curScene.setRating(rating)
        self._update()

    def repickScene(self, faceNum, debug):
        if self.isInvalid():
            return
        from tools.picker import repickScene
        images = self.curScene.getImages()
        sceneProto = repickScene(images, faceNum, debug)
        sceneProto['love'] = self.curLove.serialize()
        sceneProto['rating'] = self.curScene.getRating()
        self.curScene.load(sceneProto)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._update()

    def repickSceneWithFaces(self, facesProto):
        if self.isInvalid():
            return
        from tools.picker import repickSceneWithFaces
        images = self.curScene.getImages()
        sceneProto = repickSceneWithFaces(images, facesProto)
        sceneProto['love'] = self.curLove.serialize()
        sceneProto['rating'] = self.curScene.getRating()
        self.curScene.load(sceneProto)
        self._aidx = 0
        self._iidx = 0
        self._pidx = 0
        self._lidx = 0
        self._update()

    def moveActionForward(self):
        if self.isInvalid() or self._viewMode != ViewMode.SELECT:
            return
        self.curScene.moveActionForward(self.curAction)
        self._aidx = self.curScene.normalizeActionIdx(self._aidx - 1)
        self._update()

    def moveActionBackward(self):
        if self.isInvalid() or self._viewMode != ViewMode.SELECT:
            return
        self.curScene.moveActionBackward(self.curAction)
        self._aidx = self.curScene.normalizeActionIdx(self._aidx + 1)
        self._update()

    def deleteScenen(self):
        if self.isInvalid():
            return
        self._database.delScene(self.curScene)
        self._sidx = self._database.normalizeSceneIdx(self._sidx)
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
        self._updateActionNum()
        self._updateFaceCtrls()
        self._updateImageCtrl()
        self._updateWindowTitle()

    def _updateActionNum(self):
        if self.isInvalid() or self.curImage is None:
            self.actionNum.setText('')
            return
        aidx, _ = self.curScene.indexImage(self.curImage)
        self.actionNum.setText('%d/%d' % (aidx + 1, self.curScene.getActionNum()))

    def _updateFaceCtrls(self):
        if self.isInvalid() or self.curImage is None:
            self.faceContainer.setVisible(False)
            return
        self.faceContainer.setVisible(True)

        for ctrl in self._faceCtrls:
            ctrl.setVisible(False)

        actionIdx = 0
        for idx in range(self.curAction.getImageNum()):
            if idx >= len(self._faceCtrls):
                ctrl = Face(self.faceContainer)
                self.faceLayout.addWidget(ctrl)
                self._faceCtrls.append(ctrl)
            else:
                ctrl = self._faceCtrls[idx]
                ctrl.setVisible(True)
            image = self.curAction.getImage(idx)
            ctrl.setFace(image, self.curScene.getFaces())
            if self.curImage == image:
                ctrl.selected(True)
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

        self._updateScrollBar()

    def _updateImageCtrl(self):
        if self.isInvalid():
            self.imgFrame.setVisible(False)
            return
        self.imgFrame.setVisible(True)
        if self.curImage is None:
            self.img.setEnabled(False)
            pixmap = QPixmap(self.curScene.getAction(0).getImage(0))
        else:
            self.img.setEnabled(True)
            pixmap = QPixmap(self.curImage)
        self.img.setPixmap(pixmap)
        self.rating.setText(macro.RATING_MAP[self.curScene.getRating()])

    def _updateWindowTitle(self):
        from PyQt5.QtCore import QCoreApplication
        applicationName = QCoreApplication.applicationName()
        if self.isInvalid():
            self.window().setWindowTitle(applicationName)
            return
        if self._viewMode == ViewMode.SELECT:
            viewModeStr = 'SELECT'
        elif self._viewMode == ViewMode.PICK:
            viewModeStr = 'PICK'
        elif self._viewMode == ViewMode.LOVE:
            viewModeStr = 'LOVE'
        self.window().setWindowTitle(
            u'%s 《%s》[%d/%d] %s' % (
                applicationName, self._database.getCGName(), self._sidx + 1,
                self._database.getSceneNum(), viewModeStr
            )
        )

    def _onFaceContainerResize(self, event):
        self._updateScrollBar()

    def _updateScrollBar(self):
        for ctrl in self._faceCtrls:
            if ctrl.getImage() == self.curImage:
                selected_ctrl = ctrl
                break
        hbar = self.faceFrame.horizontalScrollBar()
        hbarVal = selected_ctrl.pos().x() - self.faceFrame.width() / 2 + selected_ctrl.width() / 2
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
