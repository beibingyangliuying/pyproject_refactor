# -------------------------------------------------------------------------------
# Name:        rename_context
# Purpose:     The data required for renaming.
#
# Author:      chenjunhan
#
# Created:     18/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
The data required for renaming.
"""
from rope.refactor.rename import Rename
from rope.base.project import Project
from rope.base.resources import Resource


class RenameContext:
    """
    Classes that store data needed for renaming.
    """

    def __init__(self, project: Project, resource: Resource, offset=None, new_name=""):
        self._executor = Rename(
            project, resource, offset
        )  # May throw `BadIdentifierError` exception.
        self._new_name = new_name

    def execute(self):
        """
        Execute the refactor of renaming.
        """
        return self._changes.do()

    def _get_new_name(self):
        return self._new_name

    def _set_new_name(self, new_name):
        self._new_name = new_name

    def _get_description(self):
        return self._changes.get_description()

    def _get_changes(self):
        return self._executor.get_changes(self._new_name)

    def _get_module_name(self):
        return self._executor.resource.path

    description = property(_get_description)
    new_name = property(_get_new_name, _set_new_name)
    _changes = property(_get_changes)
    module_name = property(_get_module_name)
