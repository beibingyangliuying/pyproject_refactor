# -------------------------------------------------------------------------------
# Name:        rename
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
from typing import Union

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget
from rope.base.resources import Resource
from rope.base.project import Project
from rope.refactor.rename import Rename
from rope.base.change import ChangeSet

from ui.generated.ui_rename import Ui_Dialog
from ui.base import IdentifierRefactorDialog


class RenameDialog(IdentifierRefactorDialog):
    """
    The dialog that perform renaming.
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
        self._rename = Rename(self._project, self._resource, self._offset)
        logging.info("Rename on %s.", self._resource.path)

        # Initialize the interface
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self._ui.lineEdit_module.setText(self._resource.path)

    @pyqtSlot()
    def preview(self):
        self._ui.plainTextEdit.setPlainText(self._description)

    @property
    def _new_name(self) -> str:
        return self._ui.lineEdit_new_name.text()

    @property
    def _changes(self) -> ChangeSet:
        return self._rename.get_changes(
            self._new_name, docs=self._ui.checkBox.isChecked()
        )
