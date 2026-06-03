# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import json
import logging
import os.path

LOG = logging.getLogger(__name__)


class RTTRObject(dict):
	def __getattr__(self, key): return self.get(key)

	def __setattr__(self, key, value): self[key] = value

	def __delattr__(self, key):
		if key in self:
			del self[key]


def get_vfs_path(vfs_path, base_path):
	if os.path.exists(vfs_path):
		return vfs_path

	if vfs_path[0] == '/':
		vfs_path = vfs_path[1:]

	return os.path.join(base_path, vfs_path)


def load_rttr(vfs_path, base_path):
	path = get_vfs_path(vfs_path, base_path)

	if not os.path.exists(path):
		LOG.error('rttr object "%s" does not exist', vfs_path)
		return RTTRObject()

	LOG.info('loading rttr object "%s"', vfs_path)
	with open(path, 'r') as file:
		return json.load(file, object_hook=lambda d: RTTRObject(d))
