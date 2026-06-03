# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

from bpy.props import StringProperty

from ._import_template import _VirtualImportTemplate
from .addon_preferences import AddonPreferences
from ..import_material import create_material
from ... import __package__ as __base_package__
from ...prefab.material import load_material


# noinspection PyTypeHints
class MaterialOperator(_VirtualImportTemplate):
	bl_idname = f'{__base_package__}.broengine_material'
	bl_label = 'Import Bro Engine Material'
	bl_description = 'Import a Bro Engine Material Snapshot (.material file)'

	filter_glob: StringProperty(default='*.material', options={'HIDDEN'})

	def load(self, path):
		game_path = AddonPreferences.instance().game_data_path
		material = load_material(path, game_path)
		create_material(material, os.path.splitext(os.path.basename(path))[0], game_path)
