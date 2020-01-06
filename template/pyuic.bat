@echo off
python3 -m PyQt5.uic.pyuic -x cgpicker.ui -o ui_cgpicker.py
python3 -m PyQt5.uic.pyuic -x picker_config.ui -o ui_picker_config.py
python3 -m PyQt5.uic.pyuic -x editor.ui -o ui_editor.py
python3 -m PyQt5.uic.pyuic -x face.ui -o ui_face.py
python3 -m PyQt5.uic.pyuic -x loading.ui -o ui_loading.py
