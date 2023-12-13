# -------------------------------------------------------------------------------
# Name:        extract
# Purpose:     The dialog that performing extracting.
#
# Author:      chenjunhan
#
# Created:     10/12/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
The dialog that performing extracting.
"""
from PyQt6.QtWidgets import QWidget
from rope.base.project import Project
from rope.base.resources import Resource

from ui.base import RefactorDialog


class ExtractDialog(RefactorDialog):
    def __init__(
        self,
        parent: QWidget,
        project: Project,
        resource: Resource,
        offsets: tuple[int, int],
    ):
        super().__init__(parent)

        # Initialize data context
        self._project = project
        self._resource = resource
        self._start_offset = offsets[0]
        self._end_offset = offsets[1]
