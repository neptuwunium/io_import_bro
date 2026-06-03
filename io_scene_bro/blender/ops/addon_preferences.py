# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Self

import bpy

from ... import __package__ as __base_package__


# noinspection PyTypeHints
class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __base_package__
	bl_description = 'BroEngine Importer Settings'

	game_data_path: bpy.props.StringProperty(
		name='Game Data Path',
		description='Path to the game\'s extracted VFS root',
		subtype='DIR_PATH',
		default='')

	def draw(self, _):
		self.layout.prop(self, 'game_data_path')

	@classmethod
	def instance(cls) -> Self:
		return bpy.context.preferences.addons[cls.bl_idname].preferences
