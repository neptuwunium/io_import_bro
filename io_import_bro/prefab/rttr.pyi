# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Any


class RTTRObject(dict):
	def __getattr__(self, key: str) -> Any | None: pass

	def __setattr__(self, key: str, value: Any | None): pass

	def __delattr__(self, key: str): pass


def load_rttr(path: str, base_path: str): pass
