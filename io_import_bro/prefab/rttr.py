# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import json
import os.path


class RTTRObject(dict):
	def __getattr__(self, key): return self.get(key)

	def __setattr__(self, key, value): self[key] = value

	def __delattr__(self, key):
		if key in self:
			del self[key]


def get_vfs_path(path, base_path):
	if os.path.exists(path):
		return path

	if path[0] == '/':
		path = path[1:]

	path = os.path.join(base_path, path)

	return path


def load_rttr(path, base_path):
	path = get_vfs_path(path, base_path)

	if not os.path.exists(path):
		return RTTRObject()

	with open(path, 'r') as file:
		return json.load(file, object_hook=lambda d: RTTRObject(d))
