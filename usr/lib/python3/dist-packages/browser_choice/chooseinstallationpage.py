#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
selectapplicationpage.py - Displays a list of package installation methods
to the user.
"""

import functools

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
)

from chooseinstallationpage_ui import Ui_ChooseInstallationPage
from packagecard import PackageCard
from cardview import CardView

class ChooseInstallationPage(QWidget):
    def __init__(
        self,
        card_list: list[PackageCard],
        parent: QWidget | None = None,
    ):
        super(ChooseInstallationPage, self).__init__(parent)
        self.ui = Ui_ChooseInstallationPage()
        self.ui.setupUi(self)

        self.card_view_layout = QVBoxLayout(self.ui.packageChooserWidget)
        self.card_view = CardView("PackageCard")
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

        self.ui.installRadioButton.toggled.connect(
            functools.partial(
                self.update_available_actions
            )
        )
        self.ui.removeRadioButton.toggled.connect(
            functools.partial(
                self.update_available_actions
            )
        )
        self.ui.purgeRadioButton.toggled.connect(
            functools.partial(
                self.update_available_actions
            )
        )

    def update_available_actions(self):
        self.ui.installRadioButton.setEnabled(True)

        if self.current_card.supports_remove:
            self.ui.removeRadioButton.setEnabled(True)
        else:
            self.ui.removeRadioButton.setChecked(False)
            self.ui.removeRadioButton.setEnabled(False)

        if self.current_card.supports_purge:
            self.ui.purgeRadioButton.setEnabled(True)
        else:
            self.ui.purgeRadioButton.setChecked(False)
            self.ui.purgeRadioButton.setEnabled(False)

        if self.ui.installRadioButton.isChecked():
            if self.current_card.supports_update:
                self.ui.noUpdateCheckbox.setEnabled(True)
            else:
                self.ui.noUpdateCheckbox.setChecked(False)
                self.ui.noUpdateCheckbox.setEnabled(False)
        else:
            self.ui.noUpdateCheckbox.setChecked(False)
            self.ui.noUpdateCheckbox.setEnabled(False)

    def update_current_card(
        self,
        source_card: PackageCard,
    ):
        self.current_card = source_card
        self.update_available_actions()
