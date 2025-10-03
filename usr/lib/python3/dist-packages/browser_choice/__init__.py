#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
__init__.py - Shared global data.
"""

import re
import os
from pathlib import Path
from typing import TextIO


# pylint: disable=too-many-return-statements
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
        if Path("/run/qubes/persistent-none").is_file():
            return "dispvm"
        if Path("/run/qubes/persistent-full").is_file():
            return "standalonevm"
        return "unknown"
    if Path("/run/qubes/this-is-templatevm").is_file():
        return "templatevm"
    return "unknown"


def get_qubes_version() -> str:
    """
    If running under Qubes OS, returns the Qubes OS version this VM is running
    under.
    """

    marker_path: Path = Path("/usr/share/qubes/marker-vm")
    if not marker_path.is_file():
        return "0"

    try:
        marker_lines: list[str] = marker_path.read_text(encoding="utf-8").split(
            "\n"
        )
        marker_version: str | None = None
        detect_comment_regex: re.Pattern[str] = re.compile(r"\s*#")
        for marker_line in marker_lines:
            if detect_comment_regex.match(marker_line):
                continue
            marker_version = marker_line
            break
        if marker_version is not None:
            return marker_version
    except Exception:
        pass

    return "0"


def get_usersession_warn_label() -> str:
    """
    Gets the usersession_warn_label string appropriate for the current
    environment.
    """

    if GlobalData.qube_type == "none":
        return GlobalData.usersession_warn_label_nonqubes
    if GlobalData.qubes_version == "4.2":
        return GlobalData.usersession_warn_label_qubes_old
    if GlobalData.qube_type in ("appvm", "dispvm"):
        return GlobalData.usersession_warn_label_qubes_new_appvm
    return GlobalData.usersession_warn_label_qubes_new_template


# pylint: disable=too-few-public-methods
class GlobalData:
    """
    Global variables for browser_choice.
    """

    plugin_dir: Path = Path("/usr/share/browser-choice/plugins")
    log_dir_path: Path = Path.home().joinpath(".local/share/browser-choice")
    log_file_path: Path = log_dir_path.joinpath("log.txt")
    log_file: TextIO | None = None
    qube_type: str = get_qube_type()
    qubes_version: str = get_qubes_version()
    uid = os.getuid()

    appvm_warn_label = 'You are currently running Browser Choice \
inside a Qubes OS App Qube. You can install or uninstall applications, but \
these changes will be reverted after a reboot. This is because most system \
files in App Qubes are reset upon reboot. See \
<a href="https://www.qubes-os.org/doc/templates/">Qubes Templates</a> for \
more information.'
    dispvm_warn_label = 'You are currently running Browser Choice \
inside a Qubes OS Disposable. You can install or uninstall \
applications, but these changes will be reverted after a reboot. This is \
because all files in Disposables are reset upon reboot. See \
<a href="https://www.qubes-os.org/doc/how-to-use-disposables/">How to use \
Disposables</a> for more information.'
    templatevm_warn_label = 'You are currently running Browser Choice inside \
a Qubes OS Template. Applications installed in this Template will be \
available in all App Qubes based on it. See \
<a href="https://www.qubes-os.org/doc/templates/">Qubes Templates</a> for \
more information.'
    standalonevm_warn_label = 'You are currently running Browser Choice inside a \
Qubes OS Standalone. Applications installed in this Qube will only be \
available within this Qube. See \
<a href="https://www.qubes-os.org/doc/templates/">Qubes Templates</a> for \
more information.'
    usersession_warn_label_nonqubes = 'You are currently running Browser \
Choice inside a user session. You will be unable to install most browsers \
from here; only browsers that install into the current user account will be \
installable. To install a browser, reboot, select <code>PERSISTENT Mode | \
SYSMAINT Session | system maintenance tasks</code> from the boot menu, and \
click <code>Install a Browser</code> in the System Maintenance Panel. See \
<a href="https://www.kicksecure.com/wiki/Sysmaint">Sysmaint</a> for more \
information.'
    usersession_warn_label_qubes_old = 'You are currently running Browser \
Choice as a normal user. You will be unable to install most browsers from \
here; only browsers that install into the current user account will be \
installable. To install a browser, open a terminal in dom0, run \
<code>qvm-run -u root VMNAME xfce4-terminal</code>, then run \
<code>browser-choice</code> from that terminal. See <a \
href="https://www.kicksecure.com/wiki/Sysmaint">Sysmaint</a> for more \
information.'
    usersession_warn_label_qubes_new_appvm = 'You are currently running \
Browser Choice as a normal user. You will be unable to install most browsers \
from here; only browsers that install into the current user account will be \
installable. To install other browsers in this qube, run \
<code>browser-choice</code> in this qube\'s template. See <a \
href="https://www.kicksecure.com/wiki/Sysmaint">Sysmaint</a> for more \
information.'
    usersession_warn_label_qubes_new_template = 'You are currently running \
Browser Choice as a normal user. You will be unable to install most browsers \
from here; only browsers that install into the current user account will be \
installable. To install other browsers in this qube, shut the qube down. Then \
in dom0, open Qube Manager, select this qube, click "Settings", click the \
"Advanced" tab, set the boot mode to "default (PERSISTENT Mode - SYSMAINT \
Session)", and click "OK". Then boot this qube and launch Browser Choice \
again. See <a href="https://www.kicksecure.com/wiki/Sysmaint">Sysmaint</a> \
for more information.'
