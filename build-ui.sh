#!/bin/bash

## Copyright (C) 2024 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

set -x
set -e
set -o nounset
set -o errtrace
set -o pipefail

dpkg -l | grep pyqt5-dev-tools
true "INFO: package qtchooser contains 'designer' program"

project_base_dir="$(dirname "$(readlink -f "${0}")")";

for ui_file in "${project_base_dir}"/ui/*; do
  ui_file_basename="$(basename "${ui_file}")"
  ui_py_file_basename="$(cut -d'.' -f1 <<< "${ui_file_basename}").py"
  pyuic5 "${ui_file}" | tee -- "${project_base_dir}/usr/lib/python3/dist-packages/browser_choice/${ui_py_file_basename}" > /dev/null
  sed -i '/^#/d' "${project_base_dir}/usr/lib/python3/dist-packages/browser_choice/${ui_py_file_basename}"
done
