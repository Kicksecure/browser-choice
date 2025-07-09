#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=invalid-name

"""
browsercard.py - Card widget that displays an application (in this case,
a web browser).
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from browser_choice.browsercard_ui import Ui_BrowserCard


class BrowserCard(QWidget):
    """
    Displays information about an application such as a web browser, and
    provides a radio button for selecting that application.
    """

    toggled: pyqtSignal = pyqtSignal()

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        app_name: str,
        vendor_name: str,
        app_url: str,
        wiki_url: str,
        vendor_url: str,
        app_icon: QPixmap,
        vendor_icon: QPixmap,
        installation_method_list: list[str],
        installed_method_list: list[str] | None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.ui = Ui_BrowserCard()
        self.ui.setupUi(self)

        self.ui.appRadioButton.setText(app_name)
        self.ui.appRadioButton.toggled.connect(self.toggled)
        self.ui.appVendorLabel.setText(
            f'<a href="{vendor_url}">{vendor_name}</a>'
        )
        self.ui.appWikiLabel.setText(
            f'<a href="{app_url}">App info</a>, '
            f'<a href="{wiki_url}">Wiki</a>'
        )
        self.ui.appIconLabel.setText("")
        self.ui.appIconLabel.setPixmap(app_icon)
        self.ui.appVendorIconLabel.setText("")
        self.ui.appVendorIconLabel.setPixmap(vendor_icon)
        inst_method_text: str = "<ul>"
        for installation_method in installation_method_list:
            inst_method_text += f"<li>{installation_method}</li>"
        inst_method_text += "</ul>"
        self.ui.availableInstallListLabel.setText(inst_method_text)
        if installed_method_list is None:
            self.ui.installedHeaderLabel.setVisible(False)
            self.ui.installedLabel.setVisible(False)
        else:
            installed_method_text = "<ul>"
            installed_method_text += "".join(
                [f"<li>{x}</li>" for x in installed_method_list]
            )
            installed_method_text += "</ul>"
            self.ui.installedLabel.setText(installed_method_text)

    def isChecked(self) -> bool:
        """
        Returns True if this card is selected.
        """

        return self.ui.appRadioButton.isChecked()
