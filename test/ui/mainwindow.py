# -------------------------------------------------------------------------------
# Name:        mainwindow
# Purpose:     Main interface.
#
# Author:      chenjunhan
#
# Created:     17/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------

"""
Main interface.
"""

import logging
import os
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtCore import QModelIndex, pyqtSlot, Qt

from rope.base.exceptions import BadIdentifierError
from ui.ui_mainwindow import Ui_MainWindow
from ui.rename_dialog import RenameDialog
from context import ProjectStructuree


class MainWindow(QMainWindow):
    """
    Main interface window class.
    """

    def __init__(self):
        super().__init__()  # Main window, no need to specify parent.

        # Initialize the interface
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        # Initialize data context
        cwd = os.getcwd()
        self._context = ProjectStructuree(cwd)
        logging.info("Initialize the current working directory: %s.", cwd)

        # Perform data binding
        self._reset_binding()

    def _reset_binding(self):
        self._ui.lineEdit_root.setText(self._context.address)
        self._ui.treeView_project.setModel(self._context.model)
        self._ui.plainTextEdit_source_code.clear()
        logging.info("Class %s: Perform data binding.", MainWindow)

    def _get_resource(self, index: QModelIndex):
        """
        Search for resource.

        Raises:
            ValueError: Thrown when the QModelIndex object is not valid.
        """
        if not index.isValid():
            raise ValueError(f"Invalid index: {index}")

        view = self._ui.treeView_project
        model = view.model()
        resource_path = model.data(index, role=Qt.ItemDataRole.ToolTipRole)
        resource = self._context.get_resource(resource_path)
        return resource

    @pyqtSlot()
    def slot_assign_root(self):
        """
        Set up the root directory of the project.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Root Directory", directory=self._context.address
        )

        if folder_path:
            logging.info("Set Root Directory: %s", folder_path)

            self._context.set_root_directory(folder_path)
            self._reset_binding()

    @pyqtSlot(QModelIndex)
    def slot_show_source_code(self, index: QModelIndex):
        """
        Display the source code of the selected module.
        """
        resource = self._get_resource(index)

        # Validate resource
        if resource == self._context.root:
            QMessageBox.warning(
                self,
                "warning",
                "Ineffective resources! The root directory has been revalidated!",
                QMessageBox.StandardButton.Ok,
            )
            self._reset_binding()
        elif resource.is_folder():
            logging.info("Folder %s selected.", resource.real_path)
            self._ui.plainTextEdit_source_code.clear()
        else:
            logging.info("Read the contents of the module %s.", resource.real_path)
            self._ui.plainTextEdit_source_code.setPlainText(resource.read())

    @pyqtSlot()
    def slot_rename(self):
        """
        Execute renaming.
        """
        # Determine offset.
        text_edit = self._ui.plainTextEdit_source_code
        if not text_edit.hasFocus():
            result = QMessageBox.question(
                self,
                "question",
                "No element is selected, the module will be renamed next, continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if result == QMessageBox.StandardButton.No:
                return

            offset = None
        else:
            cursor = text_edit.textCursor()
            offset = cursor.selectionStart()

        # Determine resource.
        index = self._ui.treeView_project.currentIndex()
        resource = self._get_resource(index)

        # Show dialog.
        try:
            dialog = RenameDialog(self, self._context.project, resource, offset)
        except BadIdentifierError as exception:
            QMessageBox.warning(self, "warning", str(exception))
            return

        dialog.exec()

        # Clean up.
        self._context.validate()
        self._reset_binding()
