# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Self

import bpy


# noinspection PyTypeHints
class AddonPreferences(bpy.types.AddonPreferences):
	game_data_path: str

	@classmethod
	def instance(cls) -> Self: pass
