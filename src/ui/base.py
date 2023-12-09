# -------------------------------------------------------------------------------
# Name:        base
# Purpose:     Base classes for dialogs.
#
# Author:      chenjunhan
#
# Created:     09/12/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
Base classes for dialogs.
"""
import logging
from abc import abstractmethod
from typing import Union

from PyQt6.QtWidgets import QDialog, QWidget, QMessageBox
from PyQt6.QtCore import pyqtSlot
from rope.base.resources import Resource
from rope.base.project import Project
from rope.base.change import ChangeSet


class RefactorDialog(QDialog):
    """
    The base class for all refactor dialog.
    """

    @pyqtSlot()
    def accept(self):
        """
        Execute refactor.
        """
        ifok = QMessageBox.question(
            self,
            "Question",
            "Confirm refactoring?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No,
        )
        if ifok == QMessageBox.StandardButton.No:
            return

        try:
            self._changes.do()
            super().accept()
            logging.info("Dialog: %s executed.", type(self))
        except PermissionError as exception:
            QMessageBox.warning(
                self,
                "Warning",
                str(exception),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No,
            )

    @abstractmethod
    def preview(self):
        """
        Preview the changes that refactoring will bring.
        """

    @property
    @abstractmethod
    def _changes(self) -> ChangeSet:
        pass

    @property
    def _description(self) -> str:
        return self._changes.get_description()  # type: ignore


class IdentifierRefactorDialog(RefactorDialog):
    """
    The base class for all identifier refactor dialog.
    """

    # pylint:disable=abstract-method

    def __init__(
        self,
        parent: QWidget,
        project: Project,
        resource: Resource,
        offset: Union[None, int],
    ):
        super().__init__(parent)

        self._project = project
        self._resource = resource
        self._offset = offset
