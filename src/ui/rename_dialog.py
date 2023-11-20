# -------------------------------------------------------------------------------
# Name:        rename_dialog
# Purpose:     The dialog that perform renaming.
#
# Author:      chenjunhan
#
# Created:     18/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
The dialog that perform renaming.
"""
import logging
from PyQt6.QtWidgets import QDialog, QMessageBox, QWidget
from PyQt6.QtCore import pyqtSlot
from rope.refactor.rename import Rename
from rope.base.project import Project
from rope.base.resources import Resource
from ui.ui_rename_dialog import Ui_Dialog


class RenameDialog(QDialog):
    """
    The dialog that perform renaming.
    """

    def __init__(
        self, parent: QWidget, project: Project, resource: Resource, offset=None
    ):
        super().__init__(parent)

        # Initialize the interface
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # Initialize data context
        self._rename = Rename(project, resource, offset)
        logging.info("Try to rename in %s.", self._module_name)

        # Perform data binding
        self._reset_binding()

    def _reset_binding(self):
        self._ui.lineEdit_module.setText(self._module_name)
        self._ui.plainTextEdit.setPlainText(self._description)
        logging.info("Class %s: Perform data binding.", RenameDialog)

    @pyqtSlot()
    def accept(self):
        """
        Execute renaming.
        """
        # Confirms whether to perform refactoring.
        result = QMessageBox.question(
            self,
            "question",
            "Confirm refactoring?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No,
        )
        if not result:
            return

        try:
            self._changes.do()
            self.close()
            logging.info("Rename in %s executed.", self._module_name)
        except PermissionError as exception:
            QMessageBox.warning(
                self,
                "warning",
                str(exception),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No,
            )

    @pyqtSlot()
    def cancel(self):
        """
        Cancel Renaming.
        """
        logging.info("Rename in %s canceled.", self._module_name)

    @pyqtSlot()
    def slot_set_new_name(self):
        """
        Re-preview the changes when finished entering the new name.
        """
        self._reset_binding()

    @property
    def _module_name(self):
        return self._rename.resource.path

    @property
    def _new_name(self):
        return self._ui.lineEdit_new_name.text()

    @property
    def _changes(self):
        return self._rename.get_changes(self._new_name)

    @property
    def _description(self):
        return self._changes.get_description()
