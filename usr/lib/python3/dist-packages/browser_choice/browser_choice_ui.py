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
import functools
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
from selectapplicationpage import SelectApplicationPage
from chooseinstallationpage import ChooseInstallationPage
from confirminstallationdialog import ConfirmInstallationDialog


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
            f"rslt=\"$(pkg_installed {package_name})\"; "
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

        self.chosen_plugin: browser_choice.ChoicePlugin | None = None
        self.chosen_action: browser_choice.ChoicePluginAction | None = None

        self.current_page: QWidget | None = None
        self.select_application_page: SelectApplicationPage | None = None
        self.choose_installation_page: ChooseInstallationPage | None = None

        self.make_select_application_page()
        self.switch_to_page(self.select_application_page)

    def switch_to_page(self, page: QWidget):
        if self.current_page is not None:
            self.current_page.hide()
        self.root_layout.addWidget(page)
        page.show()
        self.current_page = page

    def make_select_application_page(self) -> None:
        ## This will only ever be called once when first instantiating the
        ## page, so we don't need to have any teardown code here.
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

        select_application_page: SelectApplicationPage = (
            SelectApplicationPage(
                app_type_list,
                card_group_list,
                show_sysmaint_warning,
                get_qube_type(),
                are_unofficial_plugins_present(self.plugin_data),
                self,
            )
        )
        select_application_page.ui.cancelButton.clicked.connect(self.exit_app)
        select_application_page.ui.continueButton.clicked.connect(
            self.make_and_switch_to_choose_installation_page
        )

        self.select_application_page = select_application_page

    def make_choose_installation_page(self) -> None:
        if self.choose_installation_page is not None:
            for card in self.choose_installation_page.card_view.card_list:
                card.deleteLater()
            self.choose_installation_page.deleteLater()
            self.choose_installation_page = None

        for idx, card in enumerate(
            self.select_application_page.card_view_list[
                self.select_application_page.ui.appChooserTabWidget.currentIndex()
            ].card_list
        ):
            assert isinstance(card, BrowserCard)
            if card.ui.appRadioButton.isChecked():
                self.chosen_plugin = self.plugin_data[
                    self.select_application_page.ui.appChooserTabWidget.currentIndex()
                ].plugin_list[idx]

        package_card_list: list[PackageCard] = []
        for plugin_action in self.chosen_plugin.action_list:
            package_card = PackageCard(
                action_id=plugin_action.internal_id,
                package_short_description=plugin_action.method_name,
                package_long_description=plugin_action.method_subtext,
                package_icon=plugin_action.method_logo,
                supports_update=plugin_action.update_and_install_script is not None,
                supports_remove=plugin_action.uninstall_script is not None,
                supports_purge=plugin_action.purge_script is not None,
            )
            package_card_list.append(package_card)

        choose_installation_page = ChooseInstallationPage(
            self.chosen_plugin.product_name,
            package_card_list,
            self,
        )
        choose_installation_page.ui.backButton.clicked.connect(
            functools.partial(
                self.switch_to_page, self.select_application_page
            )
        )
        choose_installation_page.ui.continueButton.clicked.connect(
            self.confirm_installation_choice
        )
        self.choose_installation_page = choose_installation_page

    def make_and_switch_to_choose_installation_page(self) -> None:
        self.make_choose_installation_page()
        self.switch_to_page(self.choose_installation_page)

    def confirm_installation_choice(self):
        for idx, card in enumerate(
            self.choose_installation_page.card_view.card_list
        ):
            assert isinstance(card, PackageCard)
            if card.ui.packageRadioButton.isChecked():
                self.chosen_action = self.chosen_plugin.action_list[idx]

        action_str: str | None = None
        command_str: str | None = None

        if self.choose_installation_page.ui.installRadioButton.isChecked():
            action_str = "installed"
            if self.choose_installation_page.ui.noUpdateCheckbox.isChecked():
                command_str = self.chosen_action.install_script
            else:
                if self.chosen_action.update_and_install_script is not None:
                    command_str = self.chosen_action.update_and_install_script
                else:
                    command_str = self.chosen_action.install_script
        elif self.choose_installation_page.ui.removeRadioButton.isChecked():
            action_str = "removed"
            command_str = self.chosen_action.uninstall_script
        elif self.choose_installation_page.ui.purgeRadioButton.isChecked():
            action_str = "purged"
            command_str = self.chosen_action.purge_script

        assert action_str is not None
        assert command_str is not None

        confirm_installation_dialog = ConfirmInstallationDialog(
            app_name=self.chosen_plugin.product_name,
            repository_name=self.chosen_action.method_name_short,
            action_str=action_str,
            command_str=command_str,
        )
        confirm_installation_dialog.exec()

        ## TODO: Branch here - non-zero exit code = go back, zero = continue

    @staticmethod
    def exit_app():
        sys.exit(0)


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
