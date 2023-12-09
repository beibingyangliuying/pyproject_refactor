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
from ui.move import MoveDialog
from ui.generated.ui_mainwindow import Ui_MainWindow
from utilities import get_project_model


class MainWindow(QMainWindow):
    """
    Main interface window class.
    """

    _identifier_refactor_dialogs = {
        "action_rename": RenameDialog,
        "action_move": MoveDialog,
    }

    def __init__(self):
        super().__init__()

        # Initialize data context
        cwd = os.getcwd()
        self._project = Project(cwd)
        logging.info("Initialize the current working directory: %s.", cwd)

        # Initialize the interface
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        # Perform data binding
        self._reset_binding()

    def _reset_binding(self):
        """
        - Refresh the project root directory display.
        - Rebuild the project tree.
        - Clear the source code preview area.
        """
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
            raise ValueError(f"Invalid index: {index}.")

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
    def set_project(self):
        """
        Reset the project root path.
        If the root path is reset, the operation history will be erased.
        """
        ok = QMessageBox.question(
            self,
            "Question",
            "The history will be erased after resetting the root directory, continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ok == QMessageBox.StandardButton.No:
            return

        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Root Directory", directory=self._project.address
        )

        if folder_path:
            logging.info("Set Root Directory: %s", folder_path)

            self._project = Project(folder_path)
            self._reset_binding()

    @pyqtSlot(QModelIndex)
    def show_source_code(self, index: QModelIndex):
        """
        Display the source code of the selected module.
        If a folder is selected, the source code will be blank.
        """
        resource = self._get_resource(index)
        text_edit = self._ui.plainTextEdit_source_code

        # Validate resource
        if resource == self._project.root:  # A non-existent resource is selected.
            QMessageBox.warning(
                self,
                "Warning",
                "Ineffective resources! The project has been revalidated!",
                QMessageBox.StandardButton.Ok,
            )
            self._reset_binding()
        elif resource.is_folder():
            logging.info("Package %s selected.", resource.path)
            text_edit.clear()
        else:
            logging.info("Module %s read.", resource.path)
            text_edit.setPlainText(resource.read())

    @pyqtSlot()
    def identifier_refactor(self):
        """
        An `identifier refactor` is a refactoring behavior that
        requires the `project`, `resource` and `offset` parameters.
        """
        # Determine resource.
        index = self._ui.treeView_project.currentIndex()
        resource = self._get_resource(index)
        if resource == self._project.root:
            QMessageBox.information(
                self,
                "Information",
                "Please select a python file or package first!",
                QMessageBox.StandardButton.Ok,
            )
            return

        # Determine offset.
        offset = self._get_offset()

        # Determine dialog and refactor
        try:
            action_name = self.sender().objectName()
            dialog = self._identifier_refactor_dialogs[action_name](
                self, self._project, resource, offset
            )
            dialog.exec()
        except KeyError:
            QMessageBox.warning(
                self,
                "Warning",
                f"Refactoring not yet supported: {action_name}",
                QMessageBox.StandardButton.Ok,
            )
            return
        except BadIdentifierError as exception:
            QMessageBox.warning(self, "Warning", str(exception))
            return
        finally:
            self._reset_binding()
