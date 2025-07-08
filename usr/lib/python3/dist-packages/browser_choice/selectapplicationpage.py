#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
selectapplicationpage.py - Displays a list of applications to the user.
"""

import copy
import functools

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from selectapplicationpage_ui import Ui_SelectApplicationPage
from browsercard import BrowserCard
from cardview import CardView

class SelectApplicationPage(QWidget):
    def __init__(
        self,
        app_type_list: list[str],
        card_group_list: list[list[BrowserCard]],
        show_sysmaint_warning: bool,
        qube_type: str,
        show_unofficial_warning: bool,
        parent: QWidget | None = None,
    ):
        super(SelectApplicationPage, self).__init__(parent)
        self.ui = Ui_SelectApplicationPage()
        self.ui.setupUi(self)

        self.ui.continueButton.setEnabled(False)

        if not show_sysmaint_warning:
            self.ui.sysmaintWarningLabel.setVisible(False)

        match qube_type:
            case "appvm":
                self.ui.templatevmNoticeLabel.setVisible(False)
                self.ui.standalonevmNoticeLabel.setVisible(False)
            case "templatevm":
                self.ui.appvmNoticeLabel.setVisible(False)
                self.ui.standalonevmNoticeLabel.setVisible(False)
            case "standalonevm":
                self.ui.appvmNoticeLabel.setVisible(False)
                self.ui.templatevmNoticeLabel.setVisible(False)
            case _:
                self.ui.appvmNoticeLabel.setVisible(False)
                self.ui.templatevmNoticeLabel.setVisible(False)
                self.ui.standalonevmNoticeLabel.setVisible(False)

        if show_unofficial_warning:
            self.ui.fossNoticeLabel.setVisible(False)
        else:
            self.ui.nonFossWarningLabel.setVisible(False)

        self.card_view_list: list[CardView] = []
        self.app_type_list = copy.copy(app_type_list)
        self.current_card: BrowserCard | None = None

        for idx, app_type in enumerate(app_type_list):
            app_type_widget: QWidget = QWidget()
            app_type_layout: QVBoxLayout = QVBoxLayout(app_type_widget)
            card_view: CardView = CardView("BrowserCard")
            card_view.itemSelected.connect(
                functools.partial(self.ui.continueButton.setEnabled, True)
            )
            self.card_view_list.append(card_view)
            for card in card_group_list[idx]:
                card_view.add_card(card)
                card.ui.appRadioButton.toggled.connect(
                    functools.partial(
                        self.card_selected,
                        card,
                    )
                )
            app_type_layout.addWidget(card_view)
            self.ui.appChooserTabWidget.addTab(app_type_widget, app_type)

    def card_selected(self, card: BrowserCard):
        if card.ui.appRadioButton.isChecked():
            self.current_card = card

    def tab_changed(self, index: int) -> None:
        card_view: CardView = self.card_view_list[index]
        item_selected: bool = False
        for card in card_view.card_list:
            assert card is BrowserCard
            if card.ui.appRadioButton.isChecked():
                item_selected = True
                self.current_card = card
                break

        if item_selected:
            self.ui.continueButton.setEnabled(True)
        else:
            self.ui.continueButton.setEnabled(False)
