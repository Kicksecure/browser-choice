#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
confirminstallationdialog.py - Pop-up asking the user if they really want to
continue with installation.
"""

import functools

from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
)

from browser_choice.confirminstallationdialog_ui import (
    Ui_ConfirmInstallationDialog,
)


class ConfirmInstallationDialog(QDialog):
    """
    Pop-up informing the user of what command will be run to modify the
    system's software, and allowing the user to cancel if they desire.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        app_name: str,
        repository_name: str,
        change_str: str,
        command_str: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.ui = Ui_ConfirmInstallationDialog()
        self.ui.setupUi(self)

        self.ui.actionInfoLabel.setText(
            f"The application '{app_name}' from source '{repository_name}' "
            f"will be {change_str}. The following command will be executed:"
        )
        self.ui.commandLabel.setText(f"<code>{command_str}</code>")
        self.ui.backButton.clicked.connect(
            functools.partial(self.done, QDialog.Rejected)
        )
        self.ui.continueButton.clicked.connect(
            functools.partial(self.done, QDialog.Accepted)
        )
