#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
browser_choice_ui.py - Wizard for installing a browser or application of the
user's choice.
"""

import sys
import traceback
import subprocess
from pathlib import Path
from typing import Tuple

from PyQt5.QtCore import (
    QRect,
)

from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
)

import browser_choice

from browsercard import BrowserCard
from packagecard import PackageCard
from cardview import CardView
from selectapplicationpage import SelectApplicationPage
from chooseinstallationpage import ChooseInstallationPage


def convert_plugins_to_browser_cards(
        plugin_data: list[browser_choice.ChoicePluginCategory],
) -> (Tuple[list[str], list[list[BrowserCard]]]):
    app_type_list: list[str] = []
    card_group_list: list[list[BrowserCard]] = []

    for plugin_category in plugin_data:
        app_type_list.append(plugin_category.category_name)
        card_group: list[BrowserCard] = []

        for plugin in plugin_category.plugin_list:
            app_installed_method_list: list[str] | None = []
            for action in plugin.action_list:
                if action.check_installed():
                    app_installed_method_list.append(action.method_name_short)

            if len(app_installed_method_list) == 0:
                app_installed_method_list = None

            new_card = BrowserCard(
                plugin.product_name,
                plugin.vendor_name,
                plugin.product_website,
                plugin.wiki_link,
                plugin.vendor_website,
                plugin.product_logo,
                plugin.vendor_logo,
                [x.method_name_short for x in plugin.action_list],
                app_installed_method_list,
            )
            card_group.append(new_card)

        card_group_list.append(card_group)

    return app_type_list, card_group_list


def check_package_installed(package_name: str) -> bool:
    check_process = subprocess.run(
        [
            "/usr/bin/bash",
            "-c",
            "--",
            "source /usr/libexec/helper-scripts/package_installed_check.bsh; "
            f"rslt=\"$(pkg_installed {package_name}\); "
            "exit $rslt",
        ],
        check=False,
    )
    if check_process.returncode == 0:
        return True
    return False


def get_qube_type() -> str:
    if not Path("/usr/share/qubes/marker-vm").is_file():
        return "none"

    if Path("/run/qubes/this-is-appvm").is_file():
        if Path("/run/qubes/persistent-rw-only").is_file():
            return "appvm"
        elif Path("/run/qubes/persistent-full").is_file():
            return "standalonevm"
        else:
            return "unknown"
    elif Path("/run/qubes/this-is-templatevm").is_file():
        return "templatevm"
    else:
        return "unknown"


def are_unofficial_plugins_present(
        plugin_data: list[browser_choice.ChoicePluginCategory],
):
    for plugin_group in plugin_data:
        for plugin in plugin_group.plugin_list:
            if not plugin.is_official_plugin:
                return True
    return False


class GlobalData:
    plugin_dir: Path | None = None
    kernel_cmdline: str | None = None


class ErrorDialog(QDialog):
    def __init__(self, error_text: str, parent: QWidget | None = None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(QRect(0, 0, 640, 480))
        self.root_layout = QVBoxLayout(self)
        self.error_label = QLabel(self)
        self.error_label.setWordWrap(True)
        self.error_label.setText(error_text)
        self.root_layout.addWidget(self.error_label)


class BrowserChoiceWindow(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(QRect(0, 0, 700, 600))
        self.root_layout = QVBoxLayout(self)

        try:
            self.plugin_data: list[browser_choice.ChoicePluginCategory] = (
                browser_choice.parse_config_dir(GlobalData.plugin_dir)
            )
        except Exception:
            error_dialog = ErrorDialog(
                "<p>Error: Could not parse a plugin! Details:</p>"
                f"<p><pre>{traceback.format_exc()}</pre></p>"
            )
            error_dialog.exec()
            sys.exit(1)

        app_type_list: list[str]
        card_group_list: list[list[BrowserCard]]
        app_type_list, card_group_list = (
            convert_plugins_to_browser_cards(self.plugin_data)
        )

        show_sysmaint_warning = False
        if (
            check_package_installed("user-sysmaint-split")
            and "boot-role=sysmaint" not in GlobalData.kernel_cmdline
        ):
            show_sysmaint_warning = True

        self.select_application_page: SelectApplicationPage = (
            SelectApplicationPage(
                app_type_list,
                card_group_list,
                show_sysmaint_warning,
                get_qube_type(),
                are_unofficial_plugins_present(self.plugin_data),
                self,
            )
        )

        self.root_layout.addWidget(self.select_application_page)


def main():
    GlobalData.plugin_dir = Path("/usr/share/browser-choice/plugins")
    kernel_cmdline_path = Path("/proc/cmdline")
    if kernel_cmdline_path.is_file():
        GlobalData.kernel_cmdline = kernel_cmdline_path.read_text(
            encoding="utf-8"
        )
    else:
        kernel_cmdline_path = Path("/proc/1/cmdline")
        GlobalData.kernel_cmdline = kernel_cmdline_path.read_text(
            encoding="utf-8"
        )

    app = QApplication(sys.argv)
    window = BrowserChoiceWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
