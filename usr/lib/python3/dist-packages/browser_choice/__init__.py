#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
__init__.py - Shared global data.
"""

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
    usersession_warn_label = 'You are currently running Browser Choice inside \
a user session. You will be unable to install most browsers from here; only \
browsers that install into the current user account will be installable. To \
install a browser, reboot, select <code>PERSISTENT Mode| SYSMAINT Session | \
system maintenance tasks</code> from the boot menu, and click <code>Install \
a Browser</code> in the System Maintenance Panel. See \
<a href="https://www.kicksecure.com/wiki/Sysmaint">Sysmaint</a> for more \
information.'
