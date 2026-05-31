# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

class RTTRObject(dict):
	def __getattr__(self, key): return self.get(key)

	def __setattr__(self, key, value): self[key] = value

	def __delattr__(self, key):
		if key in self:
			del self[key]
