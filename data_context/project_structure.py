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
from rope.base.project import Project
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt


class ProjectStructure:
    """
    The class that builds the structure of the project file.
    """

    def __init__(self, path):
        self.project = Project(path)

    def get_resource(self, resource_name):
        """
        Get a resource in a project.

        Args:
            param resource_name: The path of a resource in a project.  It is
        the path of a resource relative to project root.
        """
        return self.project.get_resource(resource_name)

    def validate(self):
        """
        Validate files and folders contained in this folder

        It validates all of the files and folders contained in this
        folder if some observers are interested in them.
        """
        self.project.validate()

    def set_root_directory(self, path):
        """
        Set the project root path.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified path does not exist: {path}")

        self.project.close()  # Close previous project
        self.project = Project(path)

    def _get_model(self):
        """
        Build the project tree.
        """

        def recursive_traversal(resource, root_item: QStandardItem):
            if resource.is_folder():
                children = [
                    child
                    for child in resource.get_children()
                    if child.is_folder() or child.name.endswith(r".py")
                ]
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
        root_resource = self.project.root
        recursive_traversal(root_resource, root_item)

        return model

    model = property(_get_model)
