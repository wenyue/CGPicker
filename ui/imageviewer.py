#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import QPoint, QSize, Qt
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
		self.star.setVisible(False)
		
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

	def showPrevPick(self):
		pass

	def showNextPick(self):
		pass

	def showScene(self):
		self._aidx = 0
		self._iidx = 0
		self.updateFaceCtrls()
		self.updateImageCtrl()

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

	def showPrevAction(self):
		scene = self.curScene
		self._aidx = scene.normalizeActionIdx(self._aidx - 1, loop = True) if scene else 0
		self._iidx = 0
		self.updateImageCtrl()
		self.updateFaceCtrls()

	def showNextAction(self):
		scene = self.curScene
		self._aidx = scene.normalizeActionIdx(self._aidx + 1, loop = True) if scene else 0
		self._iidx = 0
		self.updateImageCtrl()
		self.updateFaceCtrls()

	def switchStar(self):
		pick = self.curPick
		image = self.curImage
		if not pick or not image:
			return
		if pick.isInPick(image):
			pick.delFromPick(image)
		else:
			pick.addToPick(image)
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
		if not action:
			return
		height = self.scrollArea.height() - 35
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

	def updateImageCtrl(self):
		image = self.curImage
		if not image:
			return
		self.img.setPixmap(QPixmap(image))

	def keyPressEvent(self, event):
		QWidget.keyPressEvent(self.root, event)
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
			self.switchStar()
		else:
			event.ignore()

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
			dw = self.star.width()
			dh = self.star.height()
			starPos = QPoint(ix + iw - dw, iy + ih - dh)
			self.star.move(starPos)
		else:
			self.star.setVisible(False)

	def _updateBar(self):
		for ctrl in self._faceCtrls:
			ctrl.setEnable(False)
		ctrl = self._faceCtrls[self._iidx]
		ctrl.setEnable(True)
		hbar = self.scrollArea.horizontalScrollBar()
		val = ctrl.root.pos().x() - self.scrollArea.width() / 2 + ctrl.root.width() / 2
		hbar.setValue(val)
