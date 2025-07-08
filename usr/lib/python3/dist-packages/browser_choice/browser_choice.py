#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
browser_choice.py - Library for browser-choice.
"""

import subprocess
import re
from pathlib import Path
from typing import Any

from PyQt5.QtCore import (
    QObject,
    QProcess,
)

from PyQt5.QtGui import (
    QImage,
    QPixmap,
)


def str_or_none(data: str) -> str | None:
    if data == "":
        return None
    return data


class ChoicePluginAction(QObject):
    def __init__(
            self,
            config_file: Path,
            internal_id: str,
            method_name: str | None,
            method_name_short: str | None,
            method_subtext: str | None,
            method_logo: QPixmap | None,
            update_and_install_script: str | None,
            install_script: str | None,
            uninstall_script: str | None,
            purge_script: str | None,
            install_status: str | None,
            precheck: str | None,
            postcheck: str | None,
            capability: str | None,
            parent: QObject | None = None
    ):
        super(QObject, self).__init__(parent)

        none_check_dict: dict[str, Any] = {
            "method_name": method_name,
            "method_name_short": method_name_short,
            "method_subtext": method_subtext,
            "method_logo": method_logo,
            "install_script": install_script,
            "install_status": install_status,
            "capability": capability,
        }
        for key, value in none_check_dict.items():
            if value is None:
                throw_config_error(config_file,
                    f"'{key}' in action '{internal_id}' cannot be None!"
                )

        self.internal_id: str = internal_id
        self.method_name: str = method_name
        self.method_name_short: str = method_name_short
        self.method_subtext: str = method_subtext
        self.method_logo: QPixmap = method_logo
        self.update_and_install_script: str | None = update_and_install_script
        self.install_script: str = install_script
        self.uninstall_script: str | None = uninstall_script
        self.purge_script: str | None = purge_script
        self.install_status: str = install_status
        self.precheck: str | None = precheck
        self.postcheck: str | None = postcheck
        self.capability: str = capability

    def __run_script(self, script: str) -> QProcess:
        output_process: QProcess = QProcess(self)
        output_process.setProgram("/usr/bin/bash")
        output_process.setArguments(
            [
                "-c",
                "--",
                script,
            ]
        )
        output_process.start()
        if not output_process.waitForStarted():
            raise OSError("Failed to start script!")
        return output_process

    def run_update_and_install(self) -> QProcess | None:
        if self.update_and_install_script is None:
            return None
        return self.__run_script(self.update_and_install_script)

    def run_install(self) -> QProcess:
        return self.__run_script(self.install_script)

    def run_uninstall(self) -> QProcess | None:
        if self.uninstall_script is None:
            return None
        return self.__run_script(self.uninstall_script)

    def run_purge(self) -> QProcess | None:
        if self.purge_script is None:
            return None
        return self.__run_script(self.purge_script)

    def check_installed(self) -> bool:
        check_process = subprocess.run(
            [
                "/usr/bin/bash",
                "-c",
                "--",
                self.install_status,
            ],
            check=False,
            capture_output=True,
        )
        if check_process.returncode == 0:
            return True
        return False

    def run_precheck(self) -> QProcess | None:
        if self.precheck is None:
            return None
        return self.__run_script(self.precheck)

    def run_postcheck(self) -> QProcess | None:
        if self.postcheck is None:
            return None
        return self.__run_script(self.postcheck)

    def check_capability(self) -> bool:
        capability_process = subprocess.run(
            [
                "/usr/bin/bash",
                "-c",
                "--",
                self.capability,
            ],
            check=False,
            capture_output=True,
        )
        if capability_process.returncode == 0:
            return True
        return False

class ChoicePlugin(QObject):
    def __init__(
        self,
        product_name: str,
        product_category: str,
        product_website: str,
        product_logo: QPixmap,
        vendor_name: str,
        vendor_website: str,
        vendor_logo: QPixmap,
        wiki_link: str,
        is_official_plugin: bool,
        action_list: list[ChoicePluginAction],
        parent: QObject | None = None,
    ):
        super(QObject, self).__init__(parent)
        self.product_name: str = product_name
        self.product_category: str = product_category
        self.product_website: str = product_website
        self.product_logo: QPixmap = product_logo
        self.vendor_name: str = vendor_name
        self.vendor_website: str = vendor_website
        self.vendor_logo: QPixmap = vendor_logo
        self.wiki_link: str = wiki_link
        self.is_official_plugin: bool = is_official_plugin
        self.action_list: list[ChoicePluginAction] = action_list

class ChoicePluginCategory(QObject):
    def __init__(
        self,
        category_name: str,
        parent: QObject | None = None
    ):
        super(QObject, self).__init__(parent)

        self.category_name = category_name
        self.plugin_list: list[ChoicePlugin] = []

    def add_plugin(self, plugin: ChoicePlugin):
        if plugin.product_category != self.category_name:
            raise ValueError(
                "Mismatch between category object and plugin category"
            )
        self.plugin_list.append(plugin)

def throw_config_error(config_file: Path, error_reason: str) -> None:
    raise ValueError(
        f"Invalid config file '{str(config_file)}' "
        f"({error_reason})"
    )

def load_image(image_path_str: str, config_file: Path, image_type: str) -> QPixmap:
    logo_file: Path = Path(image_path_str)
    if not logo_file.is_file():
        throw_config_error(config_file, f"{image_type} does not exist")
    logo_image: QImage = QImage(image_path_str)
    if logo_image.isNull():
        throw_config_error(config_file, f"{image_type} could not be loaded")
    logo_pixmap: QPixmap = QPixmap.fromImage(logo_image)
    return logo_pixmap

def parse_config_file(config_file: Path) -> ChoicePlugin:
    detect_comment_regex: re.Pattern[str] = re.compile(r"\s*#")
    detect_header_regex: re.Pattern[str] = re.compile(r"\[.*]\Z")
    hit_product_header: bool = False
    hit_action_header: bool = False
    current_action_name: str | None = None

    product_name: str | None = None
    product_category: str | None = None
    product_website: str | None = None
    product_logo: QPixmap | None = None
    vendor_name: str | None = None
    vendor_website: str | None = None
    vendor_logo: QPixmap | None = None
    wiki_link: str | None = None
    is_official_plugin: bool | None = None
    action_list: list[ChoicePluginAction] = []

    action_method_name: str | None = None
    action_method_name_short: str | None = None
    action_method_subtext: str | None = None
    action_method_logo: QPixmap | None = None
    action_update_and_install_script: str | None = None
    action_install_script: str | None = None
    action_uninstall_script: str | None = None
    action_purge_script: str | None = None
    action_install_status: str | None = None
    action_precheck: str | None = None
    action_postcheck: str | None = None
    action_capability: str | None = None

    with open(config_file, "r", encoding="utf-8") as conf_stream:
        for line in conf_stream:
            line = line.strip()
            if line == "":
                continue

            if detect_comment_regex.match(line):
                continue

            if detect_header_regex.match(line):
                current_header_name = line[1 : len(line) - 1]
                if current_header_name == "product":
                    if not hit_product_header:
                        hit_product_header = True
                    else:
                        throw_config_error(
                            config_file, "multiple product headers hit"
                        )
                    continue
                elif current_header_name.startswith("action:"):
                    if not hit_product_header:
                        throw_config_error(
                            config_file,
                            "action headers found before product header",
                        )

                    if hit_action_header:
                        assert current_action_name is not None
                        new_action: ChoicePluginAction = ChoicePluginAction(
                            config_file=config_file,
                            internal_id=current_action_name,
                            method_name=action_method_name,
                            method_name_short=action_method_name_short,
                            method_subtext=action_method_subtext,
                            method_logo=action_method_logo,
                            update_and_install_script=(
                                action_update_and_install_script
                            ),
                            install_script=action_install_script,
                            uninstall_script=action_uninstall_script,
                            purge_script=action_purge_script,
                            install_status=action_install_status,
                            precheck=action_precheck,
                            postcheck=action_postcheck,
                            capability=action_capability,
                        )
                        action_list.append(new_action)

                    hit_action_header = True
                    current_action_name = current_header_name.split(
                        ":",
                        maxsplit=1,
                    )[1]
                    continue
                else:
                    throw_config_error(
                        config_file,
                        f"unrecognized header '{current_header_name}'",
                    )

            if not "=" in line:
                throw_config_error(
                    config_file, "non-header line missing '='"
                )
            line_parts: list[str] = line.split("=", maxsplit=1)
            line_key: str = line_parts[0]
            line_val: str | None = line_parts[1]

            if not hit_product_header:
                throw_config_error(
                    config_file, "config lines before headers"
                )
            elif hit_product_header and not hit_action_header:
                if line_val == "":
                    line_val = None
                match line_key:
                    case "product-name":
                        product_name = str_or_none(line_val)
                    case "product-category":
                        product_category = str_or_none(line_val)
                    case "product-website":
                        product_website = str_or_none(line_val)
                    case "product-logo":
                        product_logo = load_image(
                            line_val, config_file, "product logo"
                        )
                    case "vendor-name":
                        vendor_name = str_or_none(line_val)
                    case "vendor-website":
                        vendor_website = str_or_none(line_val)
                    case "vendor-logo":
                        vendor_logo = load_image(
                            line_val, config_file, "vendor logo"
                        )
                    case "wiki":
                        wiki_link = str_or_none(line_val)
                    case "official-plugin":
                        if line_val.lower() == "yes":
                            is_official_plugin = True
                        elif line_val.lower() == "no":
                            is_official_plugin = False
                        else:
                            throw_config_error(
                                config_file,
                                "'official-plugin' boolean not set to 'yes' "
                                "or 'no'",
                            )
            else:
                match line_key:
                    case "method-name":
                        action_method_name = str_or_none(line_val)
                    case "method-name-short":
                        action_method_name_short = str_or_none(line_val)
                    case "method-subtext":
                        action_method_subtext = str_or_none(line_val)
                    case "method-logo":
                        action_method_logo = load_image(
                            line_val,
                            config_file,
                            f"method logo for '{current_action_name}'",
                        )
                    case "update-and-install-script":
                        action_update_and_install_script = str_or_none(line_val)
                    case "install-script":
                        action_install_script = str_or_none(line_val)
                    case "uninstall-script":
                        action_uninstall_script = str_or_none(line_val)
                    case "purge-script":
                        action_purge_script = str_or_none(line_val)
                    case "install-status":
                        action_install_status = str_or_none(line_val)
                    case "precheck":
                        action_precheck = str_or_none(line_val)
                    case "postcheck":
                        action_postcheck = str_or_none(line_val)
                    case "capability":
                        action_capability = str_or_none(line_val)

    if not hit_product_header and not hit_action_header:
        throw_config_error(config_file, "no headers found")
    elif hit_product_header and not hit_action_header:
        throw_config_error(
            config_file, "product header found but no action headers"
        )

    new_action = ChoicePluginAction(
        config_file=config_file,
        internal_id=current_action_name,
        method_name=action_method_name,
        method_name_short=action_method_name_short,
        method_subtext=action_method_subtext,
        method_logo=action_method_logo,
        update_and_install_script=action_update_and_install_script,
        install_script=action_install_script,
        uninstall_script=action_uninstall_script,
        purge_script=action_purge_script,
        install_status=action_install_status,
        precheck=action_precheck,
        postcheck=action_postcheck,
        capability=action_capability,
    )
    action_list.append(new_action)

    if product_name is None:
        throw_config_error(config_file, "no product name")
    elif product_category is None:
        throw_config_error(config_file, "no product category")
    elif product_website is None:
        throw_config_error(config_file, "no product website")
    elif product_logo is None:
        throw_config_error(config_file, "no product logo")
    elif vendor_name is None:
        throw_config_error(config_file, "no vendor name")
    elif vendor_website is None:
        throw_config_error(config_file, "no vendor website")
    elif vendor_logo is None:
        throw_config_error(config_file, "no vendor logo")
    elif wiki_link is None:
        throw_config_error(config_file, "no wiki link")
    elif is_official_plugin is None:
        throw_config_error(config_file, "no official plugin indicator")

    output_plugin: ChoicePlugin = ChoicePlugin(
        product_name=product_name,
        product_category=product_category,
        product_website=product_website,
        product_logo=product_logo,
        vendor_name=vendor_name,
        vendor_website=vendor_website,
        vendor_logo=vendor_logo,
        wiki_link=wiki_link,
        is_official_plugin=is_official_plugin,
        action_list=action_list,
    )
    return output_plugin

def parse_config_dir(config_dir: Path) -> list[ChoicePluginCategory]:
    config_file_list: list[Path] = []
    for config_file in config_dir.iterdir():
        if not config_file.is_file():
            continue
        config_file_list.append(config_file)
    config_file_list.sort()

    plugin_list: list[ChoicePlugin] = []
    for config_file in config_file_list:
        plugin_list.append(parse_config_file(config_file))

    category_dict: dict[str, ChoicePluginCategory] = {}
    for plugin in plugin_list:
        if not plugin.product_category in category_dict:
            category_dict[plugin.product_category] = ChoicePluginCategory(
                plugin.product_category,
            )
        category_dict[plugin.product_category].add_plugin(plugin)

    return list(category_dict.values())
