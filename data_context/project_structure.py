# -------------------------------------------------------------------------------
# Name:        project_structure
# Purpose:     Build the project file structure.
#
# Author:      chenjunhan
#
# Created:     18/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------

"""
Build the project file structure.
"""

import os
import logging
from rope.base.project import Project
from rope.base.exceptions import ResourceNotFoundError
from rope.base.resources import Resource
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt


class ProjectStructure:
    """
    The class that builds the structure of the project file.
    """

    def __init__(self, path: str):
        self._project = Project(path)  # Not intended to handle exceptions here.

    def get_resource(self, resource_name: str) -> Resource:
        """
        Get a resource in a project.
        Will validate when trying to find a resource that doesn't exist.

        Returns:
            Returns a valid resource, or the root directory if the resource
            it is trying to find does not exist.

        Args:
            param resource_name: The path of a resource in a project. It is
        the path of a resource relative to project root.
        """
        try:
            resource = self._project.get_resource(
                resource_name
            )  # Corresponding resources may not be found.
            return resource
        except ResourceNotFoundError as exception:
            logging.warning(str(exception))
            self._project.validate()
            return self._project.root

    def validate(self):
        """
        Validate files and folders contained in this folder

        It validates all of the files and folders contained in this
        folder if some observers are interested in them.
        """
        self._project.validate()

    def set_root_directory(self, path):
        """
        Set the project root path.

        Raises:
            FileNotFoundError: Thrown when a non-existent root path is specified.
        """
        if not os.path.exists(path):
            logging.warning("Project root path not found: %s.", path)
            raise FileNotFoundError(f"The specified path does not exist: {path}")

        self._project.close()  # Close previous project
        self._project = Project(path)

    def _get_project(self):
        return self._project

    def _get_model(self) -> QStandardItemModel:
        """
        Build the project tree.
        """

        def recursive_traversal(resource: Resource, root_item: QStandardItem):
            """
            Recursively traversing all .py files may take a long time.
            """
            if resource.is_folder():
                children = (
                    child
                    for child in resource.get_children()
                    if child.is_folder() or child.name.endswith(r".py")
                )  # Use the generator here.
            else:
                return

            for child in children:
                item = QStandardItem(child.name)
                item.setEditable(False)
                item.setData(child.path, Qt.ItemDataRole.ToolTipRole)

                root_item.appendRow(item)

                if child.is_folder():
                    recursive_traversal(child, item)

        # Building the tree model
        model = QStandardItemModel()
        root_item = model.invisibleRootItem()
        root_resource = self._project.root
        recursive_traversal(root_resource, root_item)

        return model

    model = property(_get_model)
    project = property(_get_project)
    address = property(lambda self: self._project.address)
    root = property(lambda self: self._project.root)
