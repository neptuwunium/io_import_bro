# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

import bpy
import bpy.utils.previews
from bpy.props import StringProperty

from ._import_template import _VirtualImportTemplate
from .addon_preferences import AddonPreferences
from ..import_prefab import create_prefab
from ... import __package__ as __base_package__
from ...prefab.loader import load_prefab


# noinspection PyTypeHints
class SceneOperator(_VirtualImportTemplate):
	bl_idname = f'{__base_package__}.broengine_scene'
	bl_label = 'Import BroEngine Scene'
	bl_description = 'Import a BroEngine Scene Prefab (.prefab, .world file)'

	filter_glob: StringProperty(default='*.prefab;*.world', options={'HIDDEN'})

	def load(self, path):
		game_path = AddonPreferences.instance().game_data_path
		root_entity = load_prefab(path, game_path)
		cache = None
		if path.endswith('.world'):
			cache = {}
		name = os.path.splitext(os.path.basename(path))[0]
		blend_obj = bpy.data.objects.new(name, None)
		create_prefab(root_entity, game_path, parent=blend_obj, cache=cache)
