# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import json
import sys

from io_import_bro.prefab.loader import load_prefab

if __name__ == '__main__':
	# todo: make an actual test system
	root_entity = load_prefab(sys.argv[-1], sys.argv[-2])
	print(json.dumps(root_entity, indent="\t"))
