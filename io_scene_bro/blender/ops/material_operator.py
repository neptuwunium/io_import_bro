# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel

from ._import_template import _VirtualImportTemplate
from .addon_preferences import AddonPreferences
from ..import_material import create_material, bind_material, bind_materials, MATERIAL_DATA_KEY
from ... import __package__ as __base_package__
from ...prefab.material import load_material


# noinspection PyTypeHints
class MaterialOperator(_VirtualImportTemplate):
	bl_idname = f'{__base_package__}.broengine_material'
	bl_label = 'Import BroEngine Material'
	bl_description = 'Import a BroEngine Material Snapshot (.material file)'

	filter_glob: StringProperty(default='*.material', options={'HIDDEN'})

	def load(self, path):
		game_path = AddonPreferences.instance().game_data_path
		material = load_material(path, game_path)
		create_material(material, os.path.splitext(os.path.basename(path))[0], game_path)


class MaterialPanelOperator(Panel):
	bl_idname = f'MATERIAL_PT_broengine_material_panel'
	bl_label = 'BroEngine'
	bl_description = 'BroEngine Material Utilities'
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "material"

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj is not None and obj.active_material is not None and MATERIAL_DATA_KEY in obj.active_material

	def draw(self, _):
		col = self.layout.column()
		col.label(text="Property Utilities:")
		col.operator(BindMaterialOperator.bl_idname, text="Re-Bind Material", icon='NODETREE')
		row = col.row()
		row.operator(BindMaterialsOperator.bl_idname, text="Selected", icon='NODETREE')
		row.operator(BindAllMaterialsOperator.bl_idname, text="All", icon='NODETREE')


class BindMaterialOperator(Operator):
	bl_idname = f'{__base_package__}.bind_material'
	bl_label = 'Bind BroEngine Material'
	bl_description = 'Reattaches material properties to node groups if the material was imported by this addon.'

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj is not None and obj.active_material is not None and MATERIAL_DATA_KEY in obj.active_material

	# noinspection PyMethodMayBeStatic
	def execute(self, context):
		context.preferences.edit.use_global_undo = False
		bind_material(context.active_object.active_material)
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}


class BindMaterialsOperator(Operator):
	bl_idname = f'{__base_package__}.bind_materials'
	bl_label = 'Bind BroEngine Materials'
	bl_description = 'Attaches material properties to node groups if the material was imported by this addon.'

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) > 0

	# noinspection PyMethodMayBeStatic
	def execute(self, context):
		context.preferences.edit.use_global_undo = False
		bind_materials(context.selected_objects)
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}


class BindAllMaterialsOperator(Operator):
	bl_idname = f'{__base_package__}.bind_all_materials'
	bl_label = 'Bind All BroEngine Materials'
	bl_description = 'Attaches material properties to node groups for all materials imported by this addon.'

	@classmethod
	def poll(cls, _):
		return len(bpy.data.materials) > 0

	# noinspection PyMethodMayBeStatic
	def execute(self, context):
		context.preferences.edit.use_global_undo = False
		bind_materials()
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}
