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
from .ops.material_operator import MaterialOperator
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


def register():
	ops._init_preview_image()
	bpy.app.handlers.load_post.append(ops._reset_preview_image)
	bpy.utils.register_class(MeshOperator)
	bpy.utils.register_class(SkelOperator)
	bpy.utils.register_class(AnimOperator)
	bpy.utils.register_class(SceneOperator)
	bpy.utils.register_class(MaterialOperator)
	bpy.utils.register_class(VehicleRegistryOperator)
	bpy.utils.register_class(FrontmenRegistryOperator)
	bpy.utils.register_class(WorldRegistryOperator)
	bpy.utils.register_class(AddonPreferences)
	bpy.utils.register_class(BroMenu)
	bpy.utils.register_class(BroSpecMenu)
	bpy.types.TOPBAR_MT_file_import.append(bro_menu_import)


def unregister():
	ops._deinit_preview_image()
	bpy.app.handlers.load_post.remove(ops._reset_preview_image)
	bpy.utils.unregister_class(MeshOperator)
	bpy.utils.unregister_class(SkelOperator)
	bpy.utils.unregister_class(AnimOperator)
	bpy.utils.unregister_class(SceneOperator)
	bpy.utils.unregister_class(MaterialOperator)
	bpy.utils.unregister_class(VehicleRegistryOperator)
	bpy.utils.unregister_class(FrontmenRegistryOperator)
	bpy.utils.unregister_class(WorldRegistryOperator)
	bpy.utils.unregister_class(AddonPreferences)
	bpy.utils.unregister_class(BroMenu)
	bpy.utils.unregister_class(BroSpecMenu)
	bpy.types.TOPBAR_MT_file_import.remove(bro_menu_import)
