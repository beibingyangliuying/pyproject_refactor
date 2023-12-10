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

from ui.mainwindow import MainWindow

# Configure the logging module
logging.basicConfig(filename="main.log", level=logging.DEBUG)


def main():
    """
    Application Main Entrance.
    """
    app = QApplication(sys.argv)
    with MainWindow() as mainwindow:
        mainwindow.show()
        app.exec()


if __name__ == "__main__":
    main()
