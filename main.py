#!/usr/bin/env python

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from eng_beng import *
from eng_beng.functions import resource_path


def run_app():
    app = QApplication(sys.argv)
    app.setApplicationName("Bangla Dictionary")
    app.setWindowIcon(QIcon(resource_path('assets/icon.png')))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
