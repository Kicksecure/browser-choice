#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
cardview.py - Widget that displays a horizontal-scrolling list of cards.
"""

from browsercard import BrowserCard
from packagecard import PackageCard

from PyQt5.QtCore import (
    pyqtSignal, Qt
)

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QScrollArea,
    QButtonGroup,
    QLayout,
)

class CardView(QScrollArea):
    itemSelected: pyqtSignal = pyqtSignal()

    def __init__(self, card_type: str, parent: QWidget | None = None):
        super(CardView, self).__init__(parent)

        if card_type != "BrowserCard" and card_type != "PackageCard":
            raise ValueError(
                "card_type must be 'BrowserCard' or 'PackageCard'"
            )

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.card_type: str = card_type
        self.root_widget: QWidget = QWidget(self)
        self.min_width: int = 0
        self.min_height: int = 0
        self.card_list: list[BrowserCard] = []
        self.scroll_layout: QHBoxLayout = QHBoxLayout(self.root_widget)
        self.scroll_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setWidget(self.root_widget)
        self.radio_button_group: QButtonGroup = QButtonGroup(self)

    def add_card(self, card: BrowserCard | PackageCard):
        if isinstance(card, BrowserCard) and self.card_type != "BrowserCard":
            raise ValueError(
                "This CardView does not support BrowserCards!"
            )
        elif isinstance(
            card, PackageCard
        ) and self.card_type != "PackageCard":
            raise ValueError(
                "This CardView does not support PackageCards!"
            )

        if card.height() > self.min_height:
            self.min_height = card.height()
        self.min_width += card.width()
        self.root_widget.setMinimumSize(self.min_width, self.min_height + 10)

        self.scroll_layout.addWidget(card)
        self.card_list.append(card)
        if isinstance(card, BrowserCard):
            self.radio_button_group.addButton(card.ui.appRadioButton)
            card.ui.appRadioButton.toggled.connect(self.itemSelected)
        elif isinstance(card, PackageCard):
            self.radio_button_group.addButton(card.ui.packageRadioButton)
            card.ui.packageRadioButton.toggled.connect(self.itemSelected)
