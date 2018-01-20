#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import QPoint, QSize, Qt, QTimer
from PyQt5.QtGui import QPixmap
from template.ui_imageviewer import Ui_ImageViewer
from ui.face import Face
from database import data


class ImageViewer(Ui_ImageViewer):

	def __init__(self, *args, **kwargs):
		self.root = QWidget(*args, **kwargs)
		self.setupUi(self.root)
		self.root.keyPressEvent = self.keyPressEvent
		self.img.paintEvent = self.paintEvent
		self.faceLayout = QHBoxLayout(self.faces)
		self.faceLayout.setSpacing(0)
		self.star.setVisible(False)
		self.home.setVisible(False)
		self.actionNum.setStyleSheet("font-size:30px")
		self.starNum.setStyleSheet("font-size:30px")

		self._faceCtrls = []
		self._sidx = 0
		self._aidx = 0
		self._iidx = 0

	@property
	def curScene(self):
		return data.getScene(self._sidx)

	@property
	def curAction(self):
		scene = self.curScene
		return scene.getAction(self._aidx) if scene else None

	@property
	def curPick(self):
		scene = self.curScene
		return scene.getPick() if scene else None

	@property
	def curImage(self):
		action = self.curAction
		return action.getImage(self._iidx) if action else None

	def isValid(self):
		return self.curImage is not None

	def showPrevPick(self):
		image = self.curImage
		pick = self.curPick
		scene = self.curScene
		index, pickImage = pick.findNearestImage(image, -1)
		if index is None:
			return
		elif index == 0:
			self.showHomeFlag()
		self._aidx, self._iidx = scene.indexImage(pickImage)
		self.updateImageCtrl()
		self.updateFaceCtrls()

	def showNextPick(self):
		image = self.curImage
		pick = self.curPick
		scene = self.curScene
		index, pickImage = pick.findNearestImage(image, 1)
		if index is None:
			return
		elif index == 0:
			self.showHomeFlag()
		self._aidx, self._iidx = scene.indexImage(pickImage)
		self.updateImageCtrl()
		self.updateFaceCtrls()

	def show(self):
		self._sidx = 0
		self._aidx = 0
		self._iidx = 0
		if not self.isValid():
			return
		self.showScene()

	def showScene(self):
		self._aidx = 0
		self.showAction()

	def showPrevScene(self):
		self._sidx = data.normalizeSceneIdx(self._sidx - 1)
		self.showScene()

	def showNextScene(self):
		self._sidx = data.normalizeSceneIdx(self._sidx + 1)
		self.showScene()

	def showPrevImage(self):
		action = self.curAction
		self._iidx = action.normalizeImageIdx(self._iidx - 1) if action else 0
		self.updateImageCtrl()

	def showNextImage(self):
		action = self.curAction
		self._iidx = action.normalizeImageIdx(self._iidx + 1) if action else 0
		self.updateImageCtrl()

	def showAction(self):
		action = self.curAction
		pick = self.curPick
		self._iidx = next(
			(idx for idx, image in enumerate(action.getImages()) if pick.isInPick(image)),
			0) if action and pick else 0
		self.updateImageCtrl()
		self.updateFaceCtrls()

	def showPrevAction(self):
		scene = self.curScene
		self._aidx = scene.normalizeActionIdx(self._aidx - 1, loop=True) if scene else 0
		if self._aidx == 0:
			self.showHomeFlag()
		self.showAction()

	def showNextAction(self):
		scene = self.curScene
		self._aidx = scene.normalizeActionIdx(self._aidx + 1, loop=True) if scene else 0
		if self._aidx == 0:
			self.showHomeFlag()
		self.showAction()

	def switchStar(self):
		pick = self.curPick
		image = self.curImage
		if pick.isInPick(image):
			pick.delFromPick(image)
		else:
			pick.addToPick(image)
		self.updateImageCtrl()
		self.updateFaceStars()

	def replaceStar(self):
		action = self.curAction
		pick = self.curPick
		image = self.curImage
		[
			pick.delFromPick(img)
			for img in action.getImages()
			if pick.isInPick(img) and img != image
		]
		self.switchStar()

	def clearPick(self):
		pick = self.curPick
		pick.clear()
		self.updateImageCtrl()
		self.updateFaceStars()

	def clearFaceCtrls(self):
		for ctrl in self._faceCtrls:
			self.faceLayout.removeWidget(ctrl.root)
			ctrl.root.setParent(None)
		self._faceCtrls = []

	def updateFaceStars(self):
		pick = self.curPick
		action = self.curAction
		faces = action.getFaces()
		for fidx, face in enumerate(faces):
			ctrl = self._faceCtrls[fidx]
			ctrl.star.setVisible(pick.isInPick(face))

	def updateFaceCtrls(self):
		self.clearFaceCtrls()
		action = self.curAction
		height = self.scrollArea.height() - 20
		faces = action.getFaces()
		for face in faces:
			pixmap = QPixmap(face)
			width = pixmap.width() / pixmap.height() * height
			pixmap = pixmap.scaled(QSize(width, height))
			ctrl = Face(self.faces)
			ctrl.setPixmap(pixmap)
			self.faceLayout.addWidget(ctrl.root)
			self._faceCtrls.append(ctrl)
		self.updateFaceStars()
		self.updateActionNum()

	def updateActionNum(self):
		self.actionNum.setText('%d/%d' % (self._aidx + 1, self.curScene.getActionLen()))

	def updateImageCtrl(self):
		image = self.curImage
		self.img.setPixmap(QPixmap(image))

	def keyPressEvent(self, event):  # noqa
		QWidget.keyPressEvent(self.root, event)
		if not self.isValid():
			return
		if event.key() == Qt.Key_Left:
			self.showPrevPick()
		elif event.key() == Qt.Key_Right:
			self.showNextPick()
		elif event.key() == Qt.Key_Up:
			self.showPrevScene()
		elif event.key() == Qt.Key_Down:
			self.showNextScene()
		elif event.key() == Qt.Key_A:
			self.showPrevImage()
		elif event.key() == Qt.Key_D:
			self.showNextImage()
		elif event.key() == Qt.Key_W:
			self.showPrevAction()
		elif event.key() == Qt.Key_S:
			self.showNextAction()
		elif event.key() == Qt.Key_Q:
			self.replaceStar()
		elif event.key() == Qt.Key_E:
			self.switchStar()
		elif event.key() == Qt.Key_F:
			self.clearPick()
		else:
			event.ignore()

	def showHomeFlag(self):
		self.home.setVisible(True)
		cw = self.imgFrame.width()
		ch = self.imgFrame.height()
		hw = self.home.width()
		hh = self.home.height()
		self.home.move(QPoint((cw - hw) / 2, (ch - hh) / 2))
		QTimer.singleShot(500, lambda: self.home.setVisible(False))

	def paintEvent(self, event):
		if self.curImage:
			self._updateImage()
			self._updateIcons()
			self._updateBar()
		QLabel.paintEvent(self.img, event)

	def _updateImage(self):
		pixmap = self.img.pixmap()
		pw = pixmap.width()
		ph = pixmap.height()
		cw = self.imgFrame.width()
		ch = self.imgFrame.height()
		factor = min(cw / pw, ch / ph)
		self.img.resize(QSize(pw * factor, ph * factor))
		iw = self.img.width()
		ih = self.img.height()
		self.img.move(QPoint((cw - iw) / 2, (ch - ih) / 2))

	def _updateIcons(self):
		pick = self.curPick
		image = self.curImage
		if pick.isInPick(image):
			self.star.setVisible(True)
			ix = self.img.pos().x()
			iy = self.img.pos().y()
			iw = self.img.width()
			ih = self.img.height()
			sw = self.star.width()
			sh = self.star.height()
			sx = ix + iw - sw
			sy = iy + ih - sh
			self.star.move(QPoint(sx, sy))
			self.starNum.setText(str(pick.getImageLen()))
			nw = self.starNum.width()
			nh = self.starNum.height()
			nx = sx + (sw - nw) / 2
			ny = sy + (sh - nh) / 2
			self.starNum.move(QPoint(nx, ny))
		else:
			self.star.setVisible(False)
			self.starNum.setText('')

	def _updateBar(self):
		for ctrl in self._faceCtrls:
			ctrl.setEnable(False)
		ctrl = self._faceCtrls[self._iidx]
		ctrl.setEnable(True)
		hbar = self.scrollArea.horizontalScrollBar()
		val = ctrl.root.pos().x() - self.scrollArea.width() / 2 + ctrl.root.width() / 2
		hbar.setValue(val)
