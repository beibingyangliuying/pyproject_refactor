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
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSlot
from ui.ui_rename_dialog import Ui_Dialog
from data_context import RenameContext


class RenameDialog(QDialog):
    """
    The dialog that perform renaming.
    """

    def __init__(self, parent, project, resource, offset=None):
        super().__init__(parent)

        # Initialize the interface
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # Initialize data context
        logging.info("Try to rename.")
        self._context = RenameContext(project, resource, offset)

        # Perform data binding
        self._reset_binding()

    def _reset_binding(self):
        self._ui.lineEdit_module.setText(self._context.module_name)
        self._context.new_name = self._ui.lineEdit_new_name.text()
        self._ui.plainTextEdit.setPlainText(self._context.description)
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

        self._context.new_name = self._ui.lineEdit_new_name.text()
        self._context.execute()
        self.close()
        logging.info("Rename in %s executed.", self._context.module_name)

    @pyqtSlot()
    def cancel(self):
        """
        Cancel Renaming.
        """
        logging.info("Rename in %s canceled.", self._context.module_name)

    @pyqtSlot()
    def slot_set_new_name(self):
        self._reset_binding()
