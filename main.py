#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from ui.cgpicker import CGPicker


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    cgpicker = CGPicker()
    cgpicker.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
