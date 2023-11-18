# -------------------------------------------------------------------------------
# Name:        mainwindow
# Purpose:     Main interface
#
# Author:      chenjunhan
#
# Created:     17/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------

"""
Main interface
"""

import logging
import os
from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6.QtCore import QModelIndex, pyqtSlot, Qt
from ui.ui_mainwindow import Ui_MainWindow
from data_context.project_structure import ProjectStructure

# Configure the logging module
logging.basicConfig(filename="main.log", level=logging.DEBUG)


class MainWindow(QMainWindow):
    """
    Main interface window class.
    """

    def __init__(self):
        super().__init__()

        # Initialize the interface
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._ui.retranslateUi(self)

        # Initialize data context
        cwd = os.getcwd()
        self._context = ProjectStructure(cwd)
        logging.info("Initialize the current working directory: %s.", cwd)

        # Perform data binding
        self._reset_binding()

    def _reset_binding(self):
        self._ui.lineEdit_root.setText(self._context.project.address)
        self._ui.treeView_project.setModel(self._context.model)
        self._ui.plainTextEdit_source_code.clear()
        logging.info("Perform data binding.")

    @pyqtSlot()
    def slot_assign_root(self):
        """
        Set up the root directory of the project.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            logging.info("Set file path: %s", folder_path)

            self._context.set_root_directory(folder_path)
            self._reset_binding()

    @pyqtSlot(QModelIndex)
    def slot_show_source_code(self, index: QModelIndex):
        """

        """
        view = self.sender()
        model = view.model()

        # Link to the specified resource
        module_path = model.data(index, role=Qt.ItemDataRole.ToolTipRole)
        module = self._context.get_resource(module_path)

        # Determine the output of the source code
        if module.is_folder():
            self._ui.plainTextEdit_source_code.clear()
        else:
            self._ui.plainTextEdit_source_code.setPlainText(module.read())

    @pyqtSlot()
    def slot_do_refactor(self):
        """

        """
        pass
