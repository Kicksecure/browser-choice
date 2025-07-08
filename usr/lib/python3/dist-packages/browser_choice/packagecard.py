#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
packagecard.py - Card widget that displays an application package.
"""

from packagecard_ui import Ui_PackageCard

from PyQt5.QtCore import pyqtSignal

from PyQt5.QtGui import (
    QPixmap,
)

from PyQt5.QtWidgets import (
    QWidget,
)

class PackageCard(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(
        self,
        action_id: str,
        package_short_description: str,
        package_long_description: str,
        package_icon: QPixmap,
        supports_update: bool,
        supports_remove: bool,
        supports_purge: bool,
        parent: QWidget | None = None
    ):
        super(PackageCard, self).__init__(parent)
        self.ui = Ui_PackageCard()
        self.ui.setupUi(self)

        self.action_id = action_id
        self.ui.packageRadioButton.setText(package_short_description)
        self.ui.packageInfoLabel.setText(package_long_description)
        self.ui.packageIconLabel.setText("")
        self.ui.packageIconLabel.setPixmap(package_icon)
        self.supports_update = supports_update
        self.supports_remove = supports_remove
        self.supports_purge = supports_purge

        self.ui.packageRadioButton.toggled.connect(self.toggled)
