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
        self._executor = Rename(project, resource, offset)
        self._new_name = new_name

    def execute(self):
        """
        Execute the refactor of renaming.
        """
        return self.changes.do()

    def _set_new_name(self, new_name):
        self._new_name = new_name

    description = property(lambda self: self.changes.get_description())
    new_name = property(lambda self: self._new_name, _set_new_name)
    changes = property(lambda self: self._executor.get_changes(self._new_name))
    module_name = property(lambda self: self._executor.resource.path)
