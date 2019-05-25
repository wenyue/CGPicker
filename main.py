#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import traceback

logger = open('log.txt', 'w')


def excepthook(excType, excValue, tb):
    exception_list = traceback.format_exception(excType, excValue, tb)
    logger.writelines(exception_list)
    logger.flush()


sys.stderr = logger
sys.stdout = logger
sys.excepthook = excepthook


def main():
    from PyQt5 import QtWidgets
    from PyQt5.QtCore import QCoreApplication
    from ui.cgpicker import CGPicker

    QCoreApplication.setApplicationName('CGPicker')

    app = QtWidgets.QApplication(sys.argv)
    cgpicker = CGPicker()
    cgpicker.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
