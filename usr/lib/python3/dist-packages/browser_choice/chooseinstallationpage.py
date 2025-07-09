#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=invalid-name

"""
selectapplicationpage.py - Displays a list of package installation methods
to the user.
"""

import functools
from enum import Enum

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QRadioButton,
)

from browser_choice.chooseinstallationpage_ui import Ui_ChooseInstallationPage
from browser_choice.packagecard import PackageCard
from browser_choice.cardview import CardView


class ModifyMode(Enum):
    """
    An enum indicating what kind of software modification the user wants to
    make.
    """

    Unknown = 0
    Install = 1
    UpdateAndInstall = 2
    Remove = 3
    Purge = 4


class ChooseInstallationPage(QWidget):
    """
    A wizard screen widget allowing the user to choose what repository to
    install an application from.
    """

    backClicked: pyqtSignal = pyqtSignal()
    continueClicked: pyqtSignal = pyqtSignal()

    def __init__(
        self,
        app_name: str,
        card_list: list[PackageCard],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.ui = Ui_ChooseInstallationPage()
        self.ui.setupUi(self)

        self.ui.backButton.clicked.connect(self.backClicked)
        self.ui.continueButton.clicked.connect(self.continueClicked)

        self.ui.appNameChoiceLabel.setText(
            f"Choose the package for '{app_name}' to install or remove."
        )
        self.ui.continueButton.setEnabled(False)

        self.card_view_layout = QVBoxLayout(self.ui.packageChooserWidget)
        self.card_view = CardView("PackageCard", self)
        for card in card_list:
            self.card_view.add_card(card)
            card.toggled.connect(
                functools.partial(
                    self.update_current_card,
                    card,
                )
            )
        self.card_view_layout.addWidget(self.card_view)

        self.current_card: PackageCard | None = None

        self.ui.installRadioButton.setEnabled(False)
        self.ui.noUpdateCheckbox.setEnabled(False)
        self.ui.removeRadioButton.setEnabled(False)
        self.ui.purgeRadioButton.setEnabled(False)
        self.ui.installRadioButton.setChecked(True)

        self.ui.installRadioButton.toggled.connect(
            functools.partial(self.update_available_actions)
        )
        self.ui.removeRadioButton.toggled.connect(
            functools.partial(self.update_available_actions)
        )
        self.ui.purgeRadioButton.toggled.connect(
            functools.partial(self.update_available_actions)
        )

    def uncheck_radio_button(self, radio_button: QRadioButton) -> None:
        """
        Convenience function for unchecking a radio button that is being
        disabled, and checking the "Install" radio button instead.
        """

        if radio_button.isChecked():
            radio_button.setChecked(False)
            self.ui.installRadioButton.setChecked(True)

    def update_available_actions(self) -> None:
        """
        Enables or disables software modification radio buttons and
        checkboxes as appropriate for the user's currently chosen settings.
        """

        if self.current_card is None:
            return

        self.ui.installRadioButton.setEnabled(True)

        if self.current_card.supports_remove and self.current_card.is_installed:
            self.ui.removeRadioButton.setEnabled(True)
        else:
            self.uncheck_radio_button(self.ui.removeRadioButton)
            self.ui.removeRadioButton.setEnabled(False)

        if self.current_card.supports_purge and self.current_card.is_installed:
            self.ui.purgeRadioButton.setEnabled(True)
        else:
            self.uncheck_radio_button(self.ui.purgeRadioButton)
            self.ui.purgeRadioButton.setEnabled(False)

        if self.ui.installRadioButton.isChecked():
            if self.current_card.supports_update:
                self.ui.noUpdateCheckbox.setEnabled(True)
            else:
                self.uncheck_radio_button(self.ui.noUpdateCheckbox)
                self.ui.noUpdateCheckbox.setEnabled(False)
        else:
            self.uncheck_radio_button(self.ui.noUpdateCheckbox)
            self.ui.noUpdateCheckbox.setEnabled(False)

    def update_current_card(
        self,
        source_card: PackageCard,
    ) -> None:
        """
        Qt signal handler. Triggered when the user changes the currently
        selected card.
        """

        if source_card.isChecked():
            self.ui.continueButton.setEnabled(True)
            self.current_card = source_card
            self.update_available_actions()

    # pylint: disable=too-many-return-statements
    def modifyMode(self) -> ModifyMode:
        """
        Gets the software modification mode currently selected by the user.
        """

        if self.current_card is None:
            return ModifyMode.Unknown

        if self.ui.installRadioButton.isChecked():
            if self.ui.noUpdateCheckbox.isChecked():
                return ModifyMode.Install
            if self.current_card.supports_update:
                return ModifyMode.UpdateAndInstall
            return ModifyMode.Install
        if self.ui.removeRadioButton.isChecked():
            return ModifyMode.Remove
        if self.ui.purgeRadioButton.isChecked():
            return ModifyMode.Purge
        return ModifyMode.Unknown
