#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=invalid-name

"""
packagecard.py - Card widget that displays an application package.
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from browser_choice.packagecard_ui import Ui_PackageCard


class PackageCard(QWidget):
    """
    Displays information about a package, and provides a radio button for
    selecting that package.
    """

    toggled = pyqtSignal(bool)

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        action_id: str,
        package_short_description: str,
        package_long_description: str,
        package_icon: QPixmap,
        supports_update: bool,
        supports_remove: bool,
        supports_purge: bool,
        is_installed: bool,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.ui = Ui_PackageCard()
        self.ui.setupUi(self)

        self.action_id = action_id
        self.ui.packageRadioButton.setText(package_short_description)
        self.ui.packageRadioButton.toggled.connect(self.toggled)
        self.ui.packageIconLabel.setText("")
        self.ui.packageIconLabel.setPixmap(package_icon)
        self.supports_update = supports_update
        self.supports_remove = supports_remove
        self.supports_purge = supports_purge
        self.is_installed = is_installed
        if is_installed:
            self.ui.packageInfoLabel.setText(
                f"{package_long_description} (Installed)"
            )
        else:
            self.ui.packageInfoLabel.setText(package_long_description)

    def isChecked(self) -> bool:
        """
        Returns True if this card is selected.
        """

        return self.ui.packageRadioButton.isChecked()
