# -------------------------------------------------------------------------------
# Name:        utilities
# Purpose:     Provides commonly used utilities.
#
# Author:      chenjunhan
#
# Created:     27/11/2023
# Copyright:   (c) chenjunhan 2023
# Licence:     MIT
# -------------------------------------------------------------------------------
"""
Provides commonly used utilities.
"""


import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from rope.base import libutils
from rope.base.resources import Resource


def is_validate_resource(resource: Resource) -> bool:
    """
    Verify if `resource` is a python file or folder.
    Folders starting and ending with `__` will be ignored.
    """
    if resource.is_folder():
        if re.match(r"^(__.+__)$", resource.name):
            return False
        return True

    project = resource.project
    return libutils.is_python_file(project, resource)


def _recursive_traversal(resource: Resource, root_item: QStandardItem):
    """
    With `resource` as the root, recursively traverse all valid resources under `resource`.
    Adds child nodes to `root_item` as the root node.
    """
    if resource.is_folder():
        children = (
            child for child in resource.get_children() if is_validate_resource(child)
        )
    else:
        return

    for child in children:
        item = QStandardItem(child.name)
        item.setEditable(False)
        item.setData(child.path, Qt.ItemDataRole.ToolTipRole)

        root_item.appendRow(item)

        if child.is_folder():
            _recursive_traversal(child, item)


def get_project_model(root_resource: Resource) -> QStandardItemModel:
    """
    Take `root_resource` as the root, traverse all valid files under it, and compose the tree model.
    """
    model = QStandardItemModel()
    root_item = model.invisibleRootItem()
    _recursive_traversal(root_resource, root_item)
    return model
