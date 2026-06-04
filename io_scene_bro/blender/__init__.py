# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import bpy
import bpy.utils.previews

from . import ops
from .import_anim import create_animation
from .import_material import create_material
from .import_mesh import create_mesh
from .import_prefab import create_prefab
from .import_skel import create_skeleton
from .ops.addon_preferences import AddonPreferences
from .ops.anim_operator import AnimOperator
from .ops.frontmen_operator import FrontmenRegistryOperator
from .ops.material_operator import *
from .ops.mesh_operator import MeshOperator
from .ops.scene_operator import SceneOperator
from .ops.skel_operator import SkelOperator
from .ops.vehicle_operator import VehicleRegistryOperator
from .ops.world_operator import WorldRegistryOperator


class BroSpecMenu(bpy.types.Menu):
	bl_idname = f'TOPBAR_MT_FILE_bro_file_import_spec'
	bl_label = 'Specification'

	def draw(self, _):
		self.layout.operator(VehicleRegistryOperator.bl_idname, text=VehicleRegistryOperator.bl_text)
		self.layout.operator(FrontmenRegistryOperator.bl_idname, text=FrontmenRegistryOperator.bl_text)
		self.layout.operator(WorldRegistryOperator.bl_idname, text=WorldRegistryOperator.bl_text)

	@classmethod
	def poll(cls, context):
		return (VehicleRegistryOperator.poll(context) or
		        FrontmenRegistryOperator.poll(context) or
		        WorldRegistryOperator.poll(context))


class BroMenu(bpy.types.Menu):
	bl_idname = f'TOPBAR_MT_FILE_bro_file_import'
	bl_label = 'BroEngine'

	def draw(self, _):
		self.layout.operator(MeshOperator.bl_idname, text='Mesh (.mesh)')
		self.layout.operator(SkelOperator.bl_idname, text='Skeleton (.skel)')
		self.layout.operator(AnimOperator.bl_idname, text='Animation (.anim)')
		self.layout.operator(SceneOperator.bl_idname, text='Scene (.prefab; .world)')
		self.layout.operator(MaterialOperator.bl_idname, text='Material (.material)')
		self.layout.menu(BroSpecMenu.bl_idname, text=BroSpecMenu.bl_label)


def bro_menu_import(self, _):
	self.layout.menu(BroMenu.bl_idname, text=BroMenu.bl_label)


CLASSES = [
	MeshOperator,
	SkelOperator,
	AnimOperator,
	SceneOperator,
	MaterialOperator,
	MaterialPanelOperator,
	BindMaterialOperator,
	BindMaterialsOperator,
	BindAllMaterialsOperator,
	VehicleRegistryOperator,
	FrontmenRegistryOperator,
	WorldRegistryOperator,
	AddonPreferences,
	BroMenu,
	BroSpecMenu,
]


def register():
	ops._init_preview_image()
	bpy.app.handlers.load_post.append(ops._reset_preview_image)

	for cls in CLASSES:
		bpy.utils.register_class(cls)

	bpy.types.TOPBAR_MT_file_import.append(bro_menu_import)


def unregister():
	ops._deinit_preview_image()
	bpy.app.handlers.load_post.remove(ops._reset_preview_image)

	for cls in CLASSES:
		bpy.utils.unregister_class(cls)

	bpy.types.TOPBAR_MT_file_import.remove(bro_menu_import)
