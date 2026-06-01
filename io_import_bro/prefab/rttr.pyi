# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Any


class RTTRObject(dict):
	def __getattr__(self, key: str) -> RTTRObject | Any | None: pass

	def __setattr__(self, key: str, value: RTTRObject | Any | None): pass

	def __delattr__(self, key: str): pass


def get_vfs_path(path: str, base_path: str) -> str: pass


def load_rttr(path: str, base_path: str) -> RTTRObject: pass
