@echo off
python3 -m PyQt5.uic.pyuic -x cgpicker.ui -o ui_cgpicker.py
python3 -m PyQt5.uic.pyuic -x cgpicker_config.ui -o ui_cgpicker_config.py
python3 -m PyQt5.uic.pyuic -x image_viewer.ui -o ui_image_viewer.py
python3 -m PyQt5.uic.pyuic -x face.ui -o ui_face.py
python3 -m PyQt5.uic.pyuic -x loading.ui -o ui_loading.py
