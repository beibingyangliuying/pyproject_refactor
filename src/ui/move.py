# -------------------------------------------------------------------------------
# Name:        move
# Purpose:     The dialog that perform moving.
#
# Author:      chenjunhan
#
# Created:     05/12/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
The dialog that perform moving.
"""
import logging
from typing import Union

from PyQt6.QtWidgets import QWidget, QInputDialog, QMessageBox
from PyQt6.QtCore import pyqtSlot
from rope.refactor.move import create_move, MoveGlobal, MoveModule, MoveMethod
from rope.base.resources import Resource
from rope.base.project import Project
from rope.base.change import ChangeSet

from ui.generated.ui_move import Ui_Dialog
from ui.base import IdentifierRefactorDialog


class MoveDialog(IdentifierRefactorDialog):
    """
    The dialog that perform moving.
    """

    def __init__(
        self,
        parent: QWidget,
        project: Project,
        resource: Resource,
        offset: Union[None, int],
    ):
        super().__init__(parent, project, resource, offset)

        # Initialize data context
        self._move = create_move(self._project, self._resource, self._offset)
        logging.info("Move on %s", self._resource.path)

        # Initialize the interface
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self._ui.label_mode.setText(type(self._move).__name__)
        self._ui.lineEdit_module.setText(resource.path)

    @pyqtSlot()
    def set_destination(self):
        """
        Set destination.
        """
        cls = type(self._move)

        if cls == MoveModule:
            packages = [
                module.parent.path
                for module in self._project.get_python_files()
                if module.name == "__init__.py"
            ]
            packages.append("")  # Root directory
            text, ifok = QInputDialog.getItem(
                self, "Select Package", "Package", packages, 0, False
            )
        elif cls == MoveGlobal:
            modules = (module.path for module in self._project.get_python_files())
            text, ifok = QInputDialog.getItem(
                self, "Select Module", "Module", modules, 0, False
            )
        elif cls == MoveMethod:
            text, ifok = QInputDialog.getText(self, "Enter Attribute", "Attribute")

        if ifok:
            self._ui.lineEdit_destination.setText(text)
            self.preview()

    @pyqtSlot()
    def preview(self):
        try:
            description = self._description
        except Exception as exception:  # todo:Capture exceptions at a finer level.
            QMessageBox.warning(
                self, "Warning", str(exception), QMessageBox.StandardButton.Ok
            )
            self._ui.lineEdit_destination.clear()
            self._ui.plainTextEdit.clear()
            return

        self._ui.plainTextEdit.setPlainText(description)

    @property
    def _destination(self) -> Union[str, Resource]:
        text = self._ui.lineEdit_destination.text()

        if isinstance(self._move, (MoveGlobal, MoveModule)):
            return self._project.get_resource(text)

        return text

    @property
    def _changes(self) -> ChangeSet:
        return self._move.get_changes(self._destination)
