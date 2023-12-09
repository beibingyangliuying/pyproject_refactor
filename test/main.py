# -------------------------------------------------------------------------------
# Name:        main
# Purpose:     Application Main Entrance.
#
# Author:      chenjunhan
#
# Created:     17/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
Application Main Entrance.
"""
import logging
import sys

from PyQt6.QtWidgets import QApplication
import ui.mainwindow


# Configure the logging module
logging.basicConfig(filename="main.log", level=logging.DEBUG)


def main():
    """
    Application Main Entrance.
    """
    app = QApplication(sys.argv)
    mainwindow = ui.mainwindow.MainWindow()
    mainwindow.show()
    app.exec()


if __name__ == "__main__":
    main()
