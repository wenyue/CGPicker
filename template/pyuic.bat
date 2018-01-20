@echo off
python3 -m PyQt5.uic.pyuic -x cgpicker.ui -o ui_cgpicker.py
python3 -m PyQt5.uic.pyuic -x imageviewer.ui -o ui_imageviewer.py
python3 -m PyQt5.uic.pyuic -x face.ui -o ui_face.py
