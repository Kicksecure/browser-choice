#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
browser_choice_ui.py - Wizard for installing a browser or application of the
user's choice.
"""

import sys
import traceback
import subprocess
import functools
import signal
from pathlib import Path
from typing import (
    Tuple,
    NoReturn,
)
from types import FrameType

from PyQt5.QtCore import (
    QRect,
    QTimer,
    QProcess,
)

from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
)

from browser_choice.browser_choice_lib import (
    ChoicePluginAction,
    ChoicePlugin,
    ChoicePluginCategory,
    parse_config_dir,
)

from browser_choice.browsercard import BrowserCard
from browser_choice.packagecard import PackageCard
from browser_choice.selectapplicationpage import SelectApplicationPage
from browser_choice.chooseinstallationpage import (
    ChooseInstallationPage,
    ModifyMode,
)
from browser_choice.confirminstallationdialog import ConfirmInstallationDialog
from browser_choice.applyingchangespage import ApplyingChangesPage
from browser_choice.changescompletepage import ChangesCompletePage


def convert_plugins_to_browser_cards(
    plugin_data: list[ChoicePluginCategory],
) -> Tuple[list[str], list[list[BrowserCard]]]:
    """
    Takes a list of plugins, and returns a list of BrowserCards corresponding
    to those plugins.
    """

    app_type_list: list[str] = []
    card_group_list: list[list[BrowserCard]] = []

    for plugin_category in plugin_data:
        app_type_list.append(plugin_category.category_name)
        card_group: list[BrowserCard] = []

        for plugin in plugin_category.plugin_list:
            app_installed_method_list: list[str] | None = []
            assert app_installed_method_list is not None
            for action in plugin.action_list:
                if action.is_installed:
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
    """
    Checks if the specified package is installed.
    """

    check_process = subprocess.run(
        [
            "/usr/bin/bash",
            "-c",
            "--",
            "source /usr/libexec/helper-scripts/package_installed_check.bsh; "
            f'rslt="$(pkg_installed {package_name})"; '
            "exit $rslt",
        ],
        check=False,
    )
    if check_process.returncode == 0:
        return True
    return False


def get_qube_type() -> str:
    """
    If running under Qubes OS, returns the qube type the application is
    running under.
    """

    if not Path("/usr/share/qubes/marker-vm").is_file():
        return "none"

    if Path("/run/qubes/this-is-appvm").is_file():
        if Path("/run/qubes/persistent-rw-only").is_file():
            return "appvm"
        if Path("/run/qubes/persistent-full").is_file():
            return "standalonevm"
        return "unknown"
    if Path("/run/qubes/this-is-templatevm").is_file():
        return "templatevm"
    return "unknown"


def are_unofficial_plugins_present(
    plugin_data: list[ChoicePluginCategory],
) -> bool:
    """
    Checks to see if any loaded plugins are unofficial using the
    'official-plugin' field of each plugin.
    """

    for plugin_group in plugin_data:
        for plugin in plugin_group.plugin_list:
            if not plugin.is_official_plugin:
                return True
    return False


# pylint: disable=too-few-public-methods
class GlobalData:
    """
    Global variables for browser_choice_ui.py.
    """

    plugin_dir: Path = Path("/usr/share/browser-choice/plugins")
    kernel_cmdline: str | None = None


# pylint: disable=too-few-public-methods
class ErrorDialog(QDialog):
    """
    Displays an error message via the GUI. Only used for unexpected and fatal
    errors.
    """

    def __init__(self, error_text: str, parent: QWidget | None = None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(QRect(0, 0, 640, 480))
        self.root_layout = QVBoxLayout(self)
        self.error_label = QLabel(self)
        self.error_label.setWordWrap(True)
        self.error_label.setText(error_text)
        self.root_layout.addWidget(self.error_label)
        self.resize(self.minimumWidth(), self.minimumHeight())


# pylint: disable=too-many-instance-attributes
class BrowserChoiceWindow(QDialog):
    """
    Core BrowserChoice window.
    """

    def __init__(self, parent: QWidget | None = None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(QRect(0, 0, 700, 600))
        self.root_layout = QVBoxLayout(self)
        self.setWindowTitle("Application Chooser")

        try:
            self.plugin_data: list[ChoicePluginCategory] = parse_config_dir(
                GlobalData.plugin_dir
            )
        except Exception:
            error_dialog = ErrorDialog(
                "<p>Error: Could not parse a plugin! Details:</p>"
                f"<p><pre>{traceback.format_exc()}</pre></p>"
            )
            error_dialog.exec()
            sys.exit(1)

        self.chosen_plugin: ChoicePlugin | None = None
        self.chosen_action: ChoicePluginAction | None = None
        self.change_str: str | None = None
        self.allow_app_launch: bool = False

        self.current_page: QWidget | None = None
        self.select_application_page: SelectApplicationPage | None = None
        self.choose_installation_page: ChooseInstallationPage | None = None
        self.applying_changes_page: ApplyingChangesPage | None = None
        self.changes_complete_page: ChangesCompletePage | None = None

        self.execute_process: QProcess | None = None
        self.execute_process_successful: bool = False
        self.stdout_buffer: bytes = b""

        self.make_select_application_page()
        assert self.select_application_page is not None
        self.switch_to_page(self.select_application_page)

    def switch_to_page(self, page: QWidget) -> None:
        """
        Switches the currently visible wizard page. It is the caller's
        responsibility tp destroy the old page if appropriate.
        """

        if self.current_page is not None:
            self.current_page.hide()
        self.root_layout.addWidget(page)
        page.show()
        self.current_page = page

    def make_select_application_page(self) -> None:
        """
        Creates the page for "Step 1/4: Select Application".
        """

        ## This will only ever be called once when first instantiating the
        ## page, so we don't need to have any teardown code here.
        app_type_list: list[str]
        card_group_list: list[list[BrowserCard]]
        app_type_list, card_group_list = convert_plugins_to_browser_cards(
            self.plugin_data
        )

        show_sysmaint_warning = False
        assert GlobalData.kernel_cmdline is not None
        if (
            check_package_installed("user-sysmaint-split")
            # pylint: disable=unsupported-membership-test
            ## see https://github.com/pylint-dev/pylint/issues/3045
            and "boot-role=sysmaint" not in GlobalData.kernel_cmdline
        ):
            show_sysmaint_warning = True

        select_application_page: SelectApplicationPage = SelectApplicationPage(
            app_type_list,
            card_group_list,
            show_sysmaint_warning,
            get_qube_type(),
            are_unofficial_plugins_present(self.plugin_data),
            self,
        )
        select_application_page.cancelClicked.connect(self.exit_app)
        select_application_page.continueClicked.connect(
            self.make_and_switch_to_choose_installation_page
        )

        self.select_application_page = select_application_page

    def make_choose_installation_page(self) -> None:
        """
        Creates the page for "Step 2/4: Choose Installation Options".
        """

        if self.choose_installation_page is not None:
            for card in self.choose_installation_page.card_view.card_list:
                card.deleteLater()
            self.choose_installation_page.deleteLater()
            self.choose_installation_page = None

        assert self.select_application_page is not None

        for idx, card in enumerate(
            self.select_application_page.card_view_list[
                self.select_application_page.tabIndex()
            ].card_list
        ):
            assert isinstance(card, BrowserCard)
            if card.isChecked():
                self.chosen_plugin = self.plugin_data[
                    self.select_application_page.tabIndex()
                ].plugin_list[idx]

        assert self.chosen_plugin is not None

        package_card_list: list[PackageCard] = []
        for plugin_action in self.chosen_plugin.action_list:
            package_card = PackageCard(
                action_id=plugin_action.internal_id,
                package_short_description=plugin_action.method_name,
                package_long_description=plugin_action.method_subtext,
                package_icon=plugin_action.method_logo,
                supports_update=plugin_action.update_and_install_script
                is not None,
                supports_remove=plugin_action.uninstall_script is not None,
                supports_purge=plugin_action.purge_script is not None,
                is_installed=plugin_action.is_installed,
            )
            package_card_list.append(package_card)

        choose_installation_page = ChooseInstallationPage(
            self.chosen_plugin.product_name,
            package_card_list,
            self,
        )
        choose_installation_page.backClicked.connect(
            functools.partial(self.switch_to_page, self.select_application_page)
        )
        choose_installation_page.continueClicked.connect(
            self.confirm_installation_choice
        )
        self.choose_installation_page = choose_installation_page

    def make_and_switch_to_choose_installation_page(self) -> None:
        """
        Qt signal handler. Creates the page for "Step 2/4: Choose Installation
        Options" and switches to it.
        """

        self.make_choose_installation_page()
        assert self.choose_installation_page is not None
        self.switch_to_page(self.choose_installation_page)

    def confirm_installation_choice(self) -> None:
        """
        Prompts the user to confirm or deny their chosen software
        modifications.

        TODO: Rename this, the user might be uninstalling the application.
        """

        assert self.choose_installation_page is not None
        assert self.chosen_plugin is not None
        for idx, card in enumerate(
            self.choose_installation_page.card_view.card_list
        ):
            assert isinstance(card, PackageCard)
            if card.isChecked():
                self.chosen_action = self.chosen_plugin.action_list[idx]
                break

        assert self.chosen_action is not None

        command_str: str | None = None

        match self.choose_installation_page.modifyMode():
            case ModifyMode.UpdateAndInstall:
                self.change_str = "installed"
                self.allow_app_launch = True
                command_str = self.chosen_action.update_and_install_script
            case ModifyMode.Install:
                self.change_str = "installed"
                self.allow_app_launch = True
                command_str = self.chosen_action.install_script
            case ModifyMode.Remove:
                self.change_str = "removed"
                command_str = self.chosen_action.uninstall_script
            case ModifyMode.Purge:
                self.change_str = "purged"
                command_str = self.chosen_action.purge_script
            case _:
                error_dialog = ErrorDialog(
                    "<p>Unreachable code hit in <code>confirm_installation_choice</code>."
                )
                error_dialog.exec()
                sys.exit(1)

        assert self.change_str is not None
        assert command_str is not None

        confirm_installation_dialog = ConfirmInstallationDialog(
            app_name=self.chosen_plugin.product_name,
            repository_name=self.chosen_action.method_name_short,
            change_str=self.change_str,
            command_str=command_str,
        )
        confirm_installation_dialog.exec()

        if confirm_installation_dialog.result() == QDialog.Accepted:
            self.apply_software_changes()

    def apply_software_changes(self) -> None:
        """
        Applies the user's chosen software modifications to the system. This
        involves creating and switching to "Step 3/4: Applying Software
        Changes".
        """

        assert self.choose_installation_page is not None
        assert self.chosen_action is not None

        self.applying_changes_page = ApplyingChangesPage()
        self.applying_changes_page.continueClicked.connect(
            self.show_software_changes_complete
        )
        self.switch_to_page(self.applying_changes_page)

        match self.choose_installation_page.modifyMode():
            case ModifyMode.UpdateAndInstall:
                self.execute_process = (
                    self.chosen_action.run_update_and_install()
                )
            case ModifyMode.Install:
                self.execute_process = self.chosen_action.run_install()
            case ModifyMode.Remove:
                self.execute_process = self.chosen_action.run_uninstall()
            case ModifyMode.Purge:
                self.execute_process = self.chosen_action.run_purge()
            case _:
                error_dialog = ErrorDialog(
                    "<p>Unreachable code hit in <code>apply_software_changes</code>."
                )
                error_dialog.exec()
                sys.exit(1)

        assert self.execute_process is not None

        self.execute_process.finished.connect(self.execute_process_completed)
        self.execute_process.readyReadStandardOutput.connect(
            self.execute_process_output_received
        )

    # pylint: disable=unused-argument
    def execute_process_completed(
        self, exit_code: int, exit_status: QProcess.ExitStatus
    ) -> None:
        """
        Qt signal handler. Triggered when the script that applies software
        modifications finishes running. Finishes with log cleanup, records
        internally whether the script was successful or not, and enables
        the continue button on "Step 3/4: Applying Software Changes".
        """

        assert self.execute_process is not None
        assert self.applying_changes_page is not None

        self.stdout_buffer += (
            self.execute_process.readAllStandardOutput().data()
        )
        stdout_text: str = self.stdout_buffer.decode(encoding="utf-8")
        self.applying_changes_page.logLine(stdout_text)

        if exit_code == 0:
            self.execute_process_successful = True
        else:
            self.execute_process_successful = False
        self.applying_changes_page.setContinueEnabled(True)

    def execute_process_output_received(self) -> None:
        """
        Qt signal handler. Triggered when the script that applies software
        modifications generates output. Grabs any available output, and prints
        any lines received from the script to the log view of "Step 3/4:
        Applying Software Changes".
        """

        assert self.execute_process is not None
        assert self.applying_changes_page is not None

        self.stdout_buffer += (
            self.execute_process.readAllStandardOutput().data()
        )
        while b"\n" in self.stdout_buffer:
            cutoff_idx: int = self.stdout_buffer.index(b"\n")
            buffer_line: bytes = self.stdout_buffer[:cutoff_idx]
            self.stdout_buffer = self.stdout_buffer[cutoff_idx + 1 :]
            line_text: str = buffer_line.decode(encoding="utf-8")
            self.applying_changes_page.logLine(line_text)

    def show_software_changes_complete(self) -> None:
        """
        Creates and displays "Step 4/4: Software Changes Complete".
        """

        assert self.chosen_plugin is not None
        assert self.chosen_action is not None
        assert self.change_str is not None

        self.changes_complete_page = ChangesCompletePage(
            app_name=self.chosen_plugin.product_name,
            repository_name=self.chosen_action.method_name_short,
            change_str=self.change_str,
            did_succeed=self.execute_process_successful,
            allow_launch=self.allow_app_launch,
        )
        self.changes_complete_page.doneClicked.connect(self.finish_wizard)
        self.switch_to_page(self.changes_complete_page)

    def finish_wizard(self) -> None:
        """
        Exits the wizard, launching a newly installed application if
        applicable and requested.
        """

        assert self.changes_complete_page is not None
        assert self.chosen_action is not None

        if self.changes_complete_page.launchAppChecked():
            self.chosen_action.run_launch()
        sys.exit(0)

    @staticmethod
    def exit_app() -> None:
        """
        Immediately exits the wizard.
        """

        sys.exit(0)


# pylint: disable=unused-argument
def signal_handler(sig: int, frame: FrameType | None) -> None:
    """
    Handles SIGINT and SIGTERM.
    """

    print("Received SIGINT or SIGTERM, exiting.", file=sys.stderr)
    sys.exit(128 + sig)


def main() -> NoReturn:
    """
    Main function.
    """

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

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    timer: QTimer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    window = BrowserChoiceWindow()
    window.show()
    app.exec_()
    sys.exit(0)


if __name__ == "__main__":
    main()
