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
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QInputDialog
from rope.base.exceptions import BadIdentifierError, ResourceNotFoundError
from rope.base.project import Project
from rope.base.resources import Resource
from rope.refactor.topackage import ModuleToPackage

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Project <%s> closed.",self._project.address)
        self._project.close()

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

    def _get_current_resource(self) -> Resource:
        index = self._ui.treeView_project.currentIndex()
        resource = self._get_resource(index)
        return resource

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
        ifok = QMessageBox.question(
            self,
            "Question",
            "The history will be erased after resetting the root directory, continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ifok == QMessageBox.StandardButton.No:
            return

        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Root Directory", directory=self._project.address
        )

        if folder_path:
            logging.info('Project <%s> closed. Set Root Directory: %s',self._project.address,folder_path)

            self._project.close()
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
        resource = self._get_current_resource()
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

    @pyqtSlot()
    def create_resource(self):
        """
        Create python file or package.
        """
        resource = self._get_current_resource()
        if not resource.is_folder():
            QMessageBox.information(
                self,
                "Information",
                "Please select a python package!",
                QMessageBox.StandardButton.Ok,
            )
            return

        text, ifok = QInputDialog.getText(
            self, "Enter Package/Module Name", "Package/Module Name"
        )
        if not ifok:
            return

        action_name = self.sender().objectName()
        if action_name == "action_create_package":
            folder = resource.create_folder(text)
            folder.create_file("__init__.py")
            logging.info("Create Package: %s", text)
        elif action_name == "action_create_module":
            resource.create_file(text + ".py")
            logging.info("Create Module: %s", text)

        self._reset_binding()

    @pyqtSlot()
    def module2package(self):
        """
        Convert a python module to a package.
        """
        resource = self._get_current_resource()
        if resource.is_folder() or resource.name == "__init__.py":
            QMessageBox.information(
                self,
                "Information",
                "Please select a python module!",
                QMessageBox.StandardButton.Ok,
            )
            return

        refactor = ModuleToPackage(self._project, resource)
        changes = refactor.get_changes()
        ifok = QMessageBox.question(
            self,
            "Question",
            "Preview:\n" + changes.get_description(),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No,
        )
        if ifok == QMessageBox.StandardButton.Ok:
            changes.do()
            self._reset_binding()
