#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
browser_choice_present.py - GUI layer of browser-choice.
"""

## NOTE: This file must not be named 'browser_choice.py', it confuses mypy.
## See https://github.com/python/mypy/issues/19410

import os
import sys
import traceback
import subprocess
import functools
import signal
import datetime
from typing import (
    Tuple,
    NoReturn,
)
from types import FrameType

from PyQt5.QtCore import (
    Qt,
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
    QPushButton,
    QHBoxLayout,
)

from browser_choice.browser_choice_core import (
    ChoicePluginRepo,
    ChoicePlugin,
    ChoicePluginCategory,
    parse_config_dir,
)

from browser_choice import GlobalData
from browser_choice import get_usersession_warn_label
from browser_choice.browsercard import BrowserCard
from browser_choice.packagecard import PackageCard
from browser_choice.selectapplicationpage import SelectApplicationPage
from browser_choice.chooseinstallationpage import (
    ChooseInstallationPage,
    ManageMode,
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
            for repo in plugin.repo_list:
                if repo.is_installed:
                    app_installed_method_list.append(repo.method_name_short)

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
                [x.method_name_short for x in plugin.repo_list],
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


def write_to_log(line: str) -> None:
    """
    Writes a line of text to browser-choice's log file, if it exists.
    """

    if GlobalData.log_file is not None:
        print(line, file=GlobalData.log_file)


# pylint: disable=too-few-public-methods
class ErrorDialog(QDialog):
    """
    Displays an error message via the GUI. Only used for unexpected and fatal
    errors.
    """

    def __init__(self, error_text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setGeometry(QRect(0, 0, 640, 480))
        self.root_layout: QVBoxLayout = QVBoxLayout(self)
        self.error_label: QLabel = QLabel(self)
        self.error_label.setWordWrap(True)
        self.error_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )
        self.error_label.setText(error_text)
        self.root_layout.addWidget(self.error_label)
        self.resize(self.minimumWidth(), self.minimumHeight())


class InitWarnDialog(QDialog):
    """
    Warns the user that they are in a Qubes OS AppVM and that the application
    they install or remove will not stay permanently installed or removed.
    """

    def __init__(self, restrict_type: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setGeometry(QRect(0, 0, 470, 180))
        self.root_layout: QVBoxLayout = QVBoxLayout(self)
        self.warn_label: QLabel = QLabel(self)
        self.warn_label.setWordWrap(True)
        self.warn_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )

        if restrict_type == "appvm":
            self.warn_label.setText(GlobalData.appvm_warn_label)
        elif restrict_type == "dispvm":
            self.warn_label.setText(GlobalData.dispvm_warn_label)
        elif restrict_type == "user_session":
            self.warn_label.setText(get_usersession_warn_label())

        self.warn_label.setOpenExternalLinks(True)
        self.root_layout.addWidget(self.warn_label)
        self.root_layout.addStretch()
        self.button_layout: QHBoxLayout = QHBoxLayout(None)
        self.button_layout.addStretch()
        self.ok_button: QPushButton = QPushButton()
        self.ok_button.setText("OK")
        self.button_layout.addWidget(self.ok_button)
        self.root_layout.addLayout(self.button_layout)
        self.ok_button.clicked.connect(lambda: self.done(0))


# pylint: disable=too-many-instance-attributes
class BrowserChoiceWindow(QDialog):
    """
    Core BrowserChoice window.
    """

    def __init__(self, parent: QWidget | None = None):
        super(QWidget, self).__init__(parent)

        self.setWindowFlags(Qt.Window)

        self.in_sysmaint_session: bool = (
            subprocess.run(
                [
                    "/usr/libexec/browser-choice/user-sysmaint-split-check",
                    "needs-sysmaint",
                ],
                check=False,
            ).returncode
            == 0
        )

        self.user_sysmaint_split_installed: bool = (
            subprocess.run(
                [
                    "/usr/bin/bash",
                    "-c",
                    "--",
                    "source "
                    "/usr/libexec/helper-scripts/package_installed_check.bsh; "
                    "pkg_installed user-sysmaint-split",
                ],
                check=False,
            ).returncode
            == 0
        )

        init_warn_dialog: InitWarnDialog | None = None
        if GlobalData.qube_type in ("appvm", "dispvm"):
            init_warn_dialog = InitWarnDialog(
                restrict_type=GlobalData.qube_type
            )
            init_warn_dialog.exec()
        elif (
            self.user_sysmaint_split_installed
            and not self.in_sysmaint_session
            and GlobalData.uid != 0
        ):
            init_warn_dialog = InitWarnDialog(restrict_type="user_session")
            init_warn_dialog.exec()
        if init_warn_dialog is not None:
            init_warn_dialog.deleteLater()

        self.setGeometry(QRect(0, 0, 865, 700))
        self.root_layout = QVBoxLayout(self)
        self.setWindowTitle("Browser Choice")

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

        if GlobalData.qube_type == "templatevm":
            self.is_network_connected: bool = True
            os.environ["https_proxy"]="http://127.0.0.1:8082/"
            os.environ["http_proxy"]="http://127.0.0.1:8082/"
            os.environ["HTTPS_PROXY"]="http://127.0.0.1:8082/"
            ## Not setting HTTP_PROXY, as applications generally ignore it for
            ## security reasons. See:
            ##
            ## https://superuser.com/questions/876100/https-proxy-vs-https-proxy
            ## https://github.com/golang/go/issues/16405
            ## https://httpoxy.org/
        else:
            self.is_network_connected = (
                subprocess.run(
                    ["/usr/libexec/helper-scripts/check-network-access"],
                    check=False,
                ).returncode
                == 0
            )

        self.chosen_plugin: ChoicePlugin | None = None
        self.chosen_repo: ChoicePluginRepo | None = None
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

        select_application_page: SelectApplicationPage = SelectApplicationPage(
            app_type_list=app_type_list,
            card_group_list=card_group_list,
            restrict_type=(
                GlobalData.qube_type
                if GlobalData.qube_type != "none"
                else (
                    "user_session"
                    if (
                        self.user_sysmaint_split_installed
                        and not self.in_sysmaint_session
                        and GlobalData.uid != 0
                    )
                    else "none"
                )
            ),
            show_unofficial_warning=(
                are_unofficial_plugins_present(self.plugin_data)
            ),
            is_network_connected=self.is_network_connected,
            parent=self,
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
        for plugin_repo in self.chosen_plugin.repo_list:
            package_card = PackageCard(
                repo_id=plugin_repo.internal_id,
                package_short_description=plugin_repo.method_name,
                package_long_description=plugin_repo.method_subtext,
                package_icon=plugin_repo.method_logo,
                supports_update=(
                    plugin_repo.update_and_install_script is not None
                ),
                supports_remove=plugin_repo.uninstall_script is not None,
                supports_purge=plugin_repo.purge_script is not None,
                is_installed=plugin_repo.is_installed,
                capability_info=plugin_repo.capability_info,
                mod_requires_privileges=plugin_repo.mod_requires_privileges,
            )
            package_card_list.append(package_card)

        choose_installation_page = ChooseInstallationPage(
            self.chosen_plugin.product_name,
            card_list=package_card_list,
            is_network_connected=self.is_network_connected,
            in_sysmaint_session=self.in_sysmaint_session,
            user_sysmaint_split_installed=self.user_sysmaint_split_installed,
            parent=self,
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
        Prompts the user to confirm or deny their chosen changes to the
        software's installation. Note that this may trigger uninstallation of
        an application, it doesn't just allow installing applications.
        """

        assert self.choose_installation_page is not None
        assert self.chosen_plugin is not None
        for idx, card in enumerate(
            self.choose_installation_page.card_view.card_list
        ):
            assert isinstance(card, PackageCard)
            if card.isChecked():
                self.chosen_repo = self.chosen_plugin.repo_list[idx]
                break

        assert self.chosen_repo is not None

        command_str: str | None = None

        match self.choose_installation_page.manageMode():
            case ManageMode.UpdateAndInstall:
                self.change_str = "installed"
                if (
                    (
                        not self.in_sysmaint_session
                        or not self.user_sysmaint_split_installed
                    )
                    and not GlobalData.qube_type == "templatevm"
                    and GlobalData.uid != 0
                ):
                    self.allow_app_launch = True
                command_str = self.chosen_repo.update_and_install_script
            case ManageMode.Install:
                self.change_str = "installed"
                if (
                    (
                        not self.in_sysmaint_session
                        or not self.user_sysmaint_split_installed
                    )
                    and not GlobalData.qube_type == "templatevm"
                    and GlobalData.uid != 0
                ):
                    self.allow_app_launch = True
                command_str = self.chosen_repo.install_script
            case ManageMode.Remove:
                self.change_str = "removed"
                command_str = self.chosen_repo.uninstall_script
            case ManageMode.Purge:
                self.change_str = "purged"
                command_str = self.chosen_repo.purge_script
            case ManageMode.Run:
                command_str = self.chosen_repo.launch_script
            case _:
                error_dialog = ErrorDialog(
                    "<p>Unreachable code hit in <code>confirm_installation_choice</code>."
                )
                error_dialog.exec()
                sys.exit(1)

        if self.choose_installation_page.manageMode() == ManageMode.Run:
            assert (
                (
                    not self.in_sysmaint_session
                    or not self.user_sysmaint_split_installed
                )
                and not GlobalData.qube_type == "templatevm"
                and not GlobalData.uid == 0
            )
            if len(sys.argv) == 2:
                self.chosen_repo.run_launch(sys.argv[1])
            else:
                self.chosen_repo.run_launch()
            sys.exit(0)

        assert self.change_str is not None
        assert command_str is not None

        confirm_installation_dialog = ConfirmInstallationDialog(
            app_name=self.chosen_plugin.product_name,
            repository_name=self.chosen_repo.method_name_short,
            install_warn_str=self.chosen_repo.install_warn_text,
            change_str=self.change_str,
            command_str=command_str,
            is_apt_third_party_repo=(
                self.chosen_repo.method_type == "apt-thirdparty"
            ),
            parent=self,
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
        assert self.chosen_repo is not None

        self.applying_changes_page = ApplyingChangesPage()
        self.applying_changes_page.continueClicked.connect(
            self.show_software_changes_complete
        )
        self.switch_to_page(self.applying_changes_page)

        write_to_log(
            "----- browser-choice run on "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            "-----"
        )

        match self.choose_installation_page.manageMode():
            case ManageMode.UpdateAndInstall:
                write_to_log(
                    "Executing command: "
                    f"{self.chosen_repo.update_and_install_script}"
                )
                self.execute_process = self.chosen_repo.run_update_and_install()
            case ManageMode.Install:
                write_to_log(
                    f"Executing command: {self.chosen_repo.install_script}"
                )
                self.execute_process = self.chosen_repo.run_install()
            case ManageMode.Remove:
                write_to_log(
                    f"Executing command: {self.chosen_repo.uninstall_script}"
                )
                self.execute_process = self.chosen_repo.run_uninstall()
            case ManageMode.Purge:
                write_to_log(
                    f"Executing command: {self.chosen_repo.purge_script}"
                )
                self.execute_process = self.chosen_repo.run_purge()
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
        write_to_log(stdout_text)

        if exit_code == 0:
            self.execute_process_successful = True
            self.applying_changes_page.logLine(
                "Done, operation was successful."
            )
            write_to_log("Done, operation was successful.")
            subprocess.run(
                [
                    "/usr/bin/notify-send",
                    "browser-choice",
                    f"Browser was successfully {self.change_str}."
                ]
            )
        else:
            self.execute_process_successful = False
            self.applying_changes_page.logLine("Done, but operation failed!")
            write_to_log("Done, but operation failed!")
            subprocess.run(
                [
                    "/usr/bin/notify-send",
                    "browser-choice",
                    f"Browser could not be {self.change_str}!"
                ]
            )
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
            write_to_log(line_text)

    def show_software_changes_complete(self) -> None:
        """
        Creates and displays "Step 4/4: Software Changes Complete".
        """

        assert self.chosen_plugin is not None
        assert self.chosen_repo is not None
        assert self.change_str is not None

        self.changes_complete_page = ChangesCompletePage(
            app_name=self.chosen_plugin.product_name,
            repository_name=self.chosen_repo.method_name_short,
            app_script=self.chosen_repo.launch_script,
            change_str=self.change_str,
            did_succeed=self.execute_process_successful,
            allow_launch=self.allow_app_launch,
            in_sysmaint_session=self.in_sysmaint_session,
            user_sysmaint_split_installed=self.user_sysmaint_split_installed,
        )
        self.changes_complete_page.doneClicked.connect(self.finish_wizard)
        self.switch_to_page(self.changes_complete_page)

    def finish_wizard(self) -> None:
        """
        Exits the wizard, launching a newly installed application if
        applicable and requested.
        """

        assert self.changes_complete_page is not None
        assert self.chosen_repo is not None

        if self.changes_complete_page.launchAppChecked():
            if len(sys.argv) == 2:
                self.chosen_repo.run_launch(sys.argv[1])
            else:
                self.chosen_repo.run_launch()
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

    try:
        GlobalData.log_dir_path.mkdir(exist_ok=True)
    except Exception:
        ## Ignore a failure to create the target directory, we can survive
        ## without being able to write logs.
        pass

    if GlobalData.log_dir_path.is_dir():
        try:
            # pylint: disable=consider-using-with
            GlobalData.log_file = open(
                GlobalData.log_file_path, mode="a", encoding="utf-8"
            )
        except PermissionError:
            GlobalData.log_file = None

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
