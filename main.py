#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

logger = open('log.txt', 'w')
sys.stderr = logger
sys.stdout = logger


def main():
    from PyQt5 import QtWidgets
    from ui.cgpicker import CGPicker
    app = QtWidgets.QApplication(sys.argv)
    cgpicker = CGPicker()
    cgpicker.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
