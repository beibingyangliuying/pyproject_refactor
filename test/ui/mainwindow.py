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
from typing import Union
from PyQt6.QtCore import QModelIndex, pyqtSlot, Qt
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from rope.base.exceptions import BadIdentifierError, ResourceNotFoundError
from rope.base.project import Project
from rope.base.resources import Resource
from ui.rename import RenameDialog
from ui.ui_mainwindow import Ui_MainWindow
from utilities import get_project_model


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
        self._project = Project(cwd)
        logging.info("Initialize the current working directory: %s.", cwd)

        # Perform data binding
        self._reset_binding()

    def _reset_binding(self):
        self._project.validate()

        self._ui.lineEdit_root.setText(self._project.address)
        self._ui.treeView_project.setModel(get_project_model(self._project.root))
        self._ui.plainTextEdit_source_code.clear()

        logging.info("Class %s: Perform data binding.", MainWindow)

    def _get_resource(self, index: QModelIndex) -> Resource:
        """
        Get a resource in a project.

        Returns:
            Returns a valid resource, or the root directory if the resource
            it is trying to find does not exist.

        Raises:
            ValueError: Thrown when the QModelIndex object is not valid.
        """
        if not index.isValid():
            raise ValueError(f"Invalid index: {index}")

        view = self._ui.treeView_project
        model = view.model()
        resource_path = model.data(index, role=Qt.ItemDataRole.ToolTipRole)

        try:
            resource = self._project.get_resource(resource_path)
            return resource
        except ResourceNotFoundError as exception:
            logging.warning(str(exception))
            return self._project.root

    def _get_offset(self) -> Union[None, int]:
        text_edit = self._ui.plainTextEdit_source_code
        if not text_edit.hasFocus():
            offset = None
        else:
            cursor = text_edit.textCursor()
            offset = cursor.selectionStart()
        return offset

    @pyqtSlot()
    def slot_assign_root(self):
        """
        Reset the project root path.
        If the root path is reset, the operation history will be erased.
        """
        result = QMessageBox.question(
            self,
            "Question",
            "The history will be erased after resetting the root directory, continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.No:
            return

        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Root Directory", directory=self._project.address
        )

        if folder_path:
            logging.info("Set Root Directory: %s", folder_path)

            self._project = Project(folder_path)
            self._reset_binding()

    @pyqtSlot(QModelIndex)
    def slot_show_source_code(self, index: QModelIndex):
        """
        Display the source code of the selected module.
        If a folder is selected, the source code will be blank.
        """
        resource = self._get_resource(index)
        text_edit = self._ui.plainTextEdit_source_code

        # Validate resource
        if resource == self._project.root:
            QMessageBox.warning(
                self,
                "Warning",
                "Ineffective resources! The project has been revalidated!",
                QMessageBox.StandardButton.Ok,
            )
            self._reset_binding()
        elif resource.is_folder():
            logging.info("Folder %s selected.", resource.real_path)
            text_edit.clear()
        else:
            logging.info("Read the contents of the module %s.", resource.real_path)
            text_edit.setPlainText(resource.read())

    @pyqtSlot()
    def slot_rename(self):
        """
        Execute renaming.
        """
        # Determine resource.
        index = self._ui.treeView_project.currentIndex()
        resource = self._get_resource(index)

        # Determine offset.
        offset = self._get_offset()
        if offset is None:
            result = QMessageBox.question(
                self,
                "Question",
                f"No element selected, the module <{resource.path}> will be renamed, continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if result == QMessageBox.StandardButton.No:
                return

        # Show dialog.
        try:
            dialog = RenameDialog(self, self._project, resource, offset)
            dialog.exec()
        except BadIdentifierError as exception:
            QMessageBox.warning(self, "Warning", str(exception))
            return
        finally:
            self._reset_binding()
