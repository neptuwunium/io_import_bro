# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import logging
import os
import time
from typing import Self

import bpy
# noinspection PyUnresolvedReferences
from bpy.props import StringProperty, CollectionProperty
# noinspection PyUnresolvedReferences
from bpy.types import Operator, Context, Property, OperatorFileListElement, ImagePreview, TOPBAR_MT_file_import
# noinspection PyUnresolvedReferences
from bpy.utils.previews import ImagePreviewCollection
# noinspection PyUnresolvedReferences
from bpy_extras.io_utils import ImportHelper
# noinspection PyUnresolvedReferences
import bpy.utils.previews

from .. import __package__ as __base_package__
from ..format.mesh import MeshFile
from ..format.skel import SkelFile
from ..prefab import rttr
from ..prefab.loader import load_prefab
from ..prefab.material import load_material
from ..prefab.rttr import RTTRObject
from .import_material import create_material
from .import_mesh import import_mesh
from .import_prefab import create_prefab
from .import_skel import create_skeleton

_bro_image_collection: ImagePreviewCollection | None = None

LOG = logging.getLogger(f'{__name__}')


def _load_preview_image(name: str, path: str) -> str:
	global _bro_image_collection
	if _bro_image_collection is None:
		return 'MESH_DATA'

	if path is None:
		return 'MESH_DATA'

	if name not in _bro_image_collection:
		game_path = AddonPreferences.instance().game_data_path
		assert game_path is not None

		if path[0] == '/':
			path = path[1:]

		if not path.endswith('.dds'):
			path = path + '.dds'

		# noinspection PyArgumentList
		path = os.path.join(game_path, path)

		# noinspection PyUnresolvedReferences
		if not os.path.exists(path):
			return 'MESH_DATA'

		_bro_image_collection.load(name, path, 'IMAGE')

	return _bro_image_collection[name].icon_id


# noinspection PyTypeHints
class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __base_package__

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


# noinspection PyTypeHints
class _ImportTemplate(Operator, ImportHelper):
	bl_options = {'REGISTER', 'UNDO'}

	files: CollectionProperty(
		type=bpy.types.OperatorFileListElement,
		options={'HIDDEN'},
	)

	directory: StringProperty(get=lambda self: AddonPreferences.instance().game_data_path or '', options={'HIDDEN'})

	def load(self, path: str): pass

	@classmethod
	def poll(cls, _): return True

	def draw(self, _): pass

	def execute(self, context: Context):
		dirname = os.path.dirname(self.filepath)
		context.preferences.edit.use_global_undo = False
		start_time = time.perf_counter()
		for file in self.files:
			# noinspection PyTypeChecker
			self.load(os.path.join(dirname, file.name))
		context.view_layer.update()
		end_time = time.perf_counter()
		logging.info("took %.6f seconds", end_time - start_time)
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}


# noinspection PyTypeHints
class _VirtualImportTemplate(_ImportTemplate):
	@classmethod
	def poll(cls, _):
		path = AddonPreferences.instance().game_data_path
		return path and os.path.exists(AddonPreferences.instance().game_data_path)


# noinspection PyTypeHints
class MeshOperator(_ImportTemplate):
	bl_idname = f'{__base_package__}.broengine_mesh'
	bl_label = 'Import Bro Engine Mesh'

	filter_glob: StringProperty(default='*.mesh', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			name = os.path.splitext(os.path.basename(path))[0]
			import_mesh(MeshFile(file), name)


# noinspection PyTypeHints
class SkelOperator(_ImportTemplate):
	bl_idname = f'{__base_package__}.broengine_skel'
	bl_label = 'Import Bro Engine Skeleton'

	filter_glob: StringProperty(default='*.skel', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			name = os.path.splitext(os.path.basename(path))[0]
			blend_obj = bpy.data.objects.new(name, None)
			create_skeleton(SkelFile(file), blend_obj)


# noinspection PyTypeHints
class SceneOperator(_VirtualImportTemplate):
	bl_idname = f'{__base_package__}.broengine_scene'
	bl_label = 'Import Bro Engine Scene'

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


# noinspection PyTypeHints
class MaterialOperator(_VirtualImportTemplate):
	bl_idname = f'{__base_package__}.broengine_material'
	bl_label = 'Import Bro Engine Material'

	filter_glob: StringProperty(default='*.material', options={'HIDDEN'})

	def load(self, path):
		game_path = AddonPreferences.instance().game_data_path
		material = load_material(path, game_path)
		create_material(material, os.path.splitext(os.path.basename(path))[0], game_path)

class SpecOperator(Operator):
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def get_spec_path(cls): return ''

	@classmethod
	def get_spec_name(cls, name: str) -> str | None: return name

	@classmethod
	def get_spec(cls) -> list[tuple[str, str, str, str, int]]: return []

	def invoke(self, context: Context, _): return context.window_manager.invoke_props_dialog(self, width=200)

	def draw_extended(self, _): pass

	def draw(self, context: Context):
		self.layout.label(text=self.bl_header)
		self.layout.template_icon_view(self, 'spec_selector', show_labels=True)
		self.layout.label(text=self.get_spec_name(self.spec_selector))
		self.draw_extended(context)

	@classmethod
	def poll(cls, _):
		path = AddonPreferences.instance().game_data_path
		if not path:
			return False
		spec_path = os.path.join(path, cls.get_spec_path())
		return os.path.exists(spec_path)

	def execute_core(self, context: Context): pass

	def execute(self, context: Context):
		context.preferences.edit.use_global_undo = False
		start_time = time.perf_counter()
		self.execute_core(context)
		end_time = time.perf_counter()
		context.view_layer.update()
		logging.info("took %.6f seconds", end_time - start_time)
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}


# noinspection PyTypeChecker
class VehicleRegistryOperator(SpecOperator):
	bl_idname = f'{__base_package__}.broengine_spec_vehicle'
	bl_label = 'Import HEAT Vehicle'
	bl_text = 'Vehicle'
	bl_header = 'Select a Vehicle'

	# noinspection PyTypeHints
	spec_selector: bpy.props.EnumProperty(
		name=bl_header,
		items=lambda self, _: VehicleRegistryOperator.get_spec()
	)

	_vehicles: list[tuple[str, str, str, str, int]] | None = None
	_vehicles_cache: str | None = None
	_vehicle_data: dict[str, RTTRObject] | None = None

	@classmethod
	def get_spec_path(cls):
		return 'vehicles/vehicles.specs'

	@classmethod
	def get_spec_name(cls, name: str) -> str | None:
		if not cls._vehicle_data:
			return None

		# noinspection PyUnresolvedReferences
		return cls._vehicle_data[name].vehicleName.message

	@classmethod
	def get_spec(cls) -> list[tuple[str, str, str, str, int]]:
		game_path = AddonPreferences.instance().game_data_path
		spec_path = os.path.join(game_path, cls.get_spec_path())

		if cls._vehicles and cls._vehicles_cache == spec_path:
			return cls._vehicles

		cls._vehicles_cache = spec_path
		vehicles = []
		names = {}
		registry = rttr.load_rttr(cls.get_spec_path(), game_path)
		if not registry: return vehicles

		for description in registry.descriptions or []:
			vehicle_spec = description.spec
			if not vehicle_spec: continue

			vehicle_spec = rttr.load_rttr(description.spec, game_path).specification
			if not vehicle_spec: continue

			vehicle_id = f'VEHICLE_{vehicle_spec.technicalName.upper()}'
			image = _load_preview_image(vehicle_id, vehicle_spec.image)
			vehicles.append((vehicle_id, vehicle_spec.vehicleName.message, '', image, len(vehicles)))
			names[vehicle_id] = vehicle_spec

		cls._vehicles = vehicles
		cls._vehicle_data = names
		return vehicles

	def draw_extended(self, _):
		# todo: list skins:
		#  customization2D: customization2D.stylesPacks[]
		#  ->-> .description.name
		#  ->-> .prefabConfig.prefab
		#  customization3D: customization2D.stylesPacks[]
		#  ->-> .description.name
		#  customization3D.modulePacks[] <- find .modulesPack
		#  ->-> .modules[].prefabConfig, customization3D
		pass

	def execute_core(self, _):
		cls = self.__class__

		if not cls._vehicle_data:
			return

		data = cls._vehicle_data[self.spec_selector]
		modules = data.modules
		if not isinstance(modules, list):
			return

		slot_assignments = {}
		slots = {}
		game_path = AddonPreferences.instance().game_data_path

		name = data.vehicleName.message
		blend_obj = bpy.data.objects.new(name, None)

		for module in modules:
			prefab_configs = module.get('general', {}).get('prefabConfig', [])
			if not isinstance(prefab_configs, list) or not prefab_configs:
				continue

			# todo: prefabOverrides
			if module.get('prefabOverrides'):
				LOG.warning('module \"%s\" has prefab overrides!', module.general.name)

			for prefab_config in prefab_configs:
				if not isinstance(prefab_config, RTTRObject):
					continue

				prefab_path = prefab_config.prefab
				if not prefab_path:
					continue

				slot = prefab_config.get('slot', {}).get('handle')
				# todo: style system

				prefab_entity = load_prefab(prefab_path, game_path)
				slot_prefab = create_prefab(prefab_entity, game_path, parent=blend_obj, slots=slots)
				if slot_prefab and slot:
					if slot not in slot_assignments:
						slot_assignments[slot] = []
					slot_assignments[slot].append(slot_prefab)
		for slot_name, slot_object in slots.items():
			if slot_name not in slot_assignments:
				continue
			for slot_prefab in slot_assignments[slot_name]:
				slot_prefab.parent = slot_object


# noinspection PyTypeChecker
class FrontmenRegistryOperator(SpecOperator):
	bl_idname = f'{__base_package__}.broengine_spec_frontmen'
	bl_label = 'Import HEAT Agent'
	bl_text = 'Agent'
	bl_header = 'Select a Agent'

	# noinspection PyTypeHints
	spec_selector: bpy.props.EnumProperty(
		name=bl_header,
		items=lambda self, _: FrontmenRegistryOperator.get_spec()
	)

	_frontmen: list[tuple[str, str, str, str, int]] | None = None
	_frontmen_cache: str | None = None
	_frontmen_data: dict[str, RTTRObject] | None = None

	@classmethod
	def get_spec_path(cls):
		return 'frontmen/frontmen.specs'

	@classmethod
	def get_spec_name(cls, name: str) -> str | None:
		if not cls._frontmen_data:
			return None

		# noinspection PyUnresolvedReferences
		return cls._frontmen_data[name].name.message

	@classmethod
	def get_spec(cls) -> list[tuple[str, str, str, str, int]]:
		game_path = AddonPreferences.instance().game_data_path
		spec_path = os.path.join(game_path, cls.get_spec_path())

		if cls._frontmen and cls._frontmen_cache == spec_path:
			return cls._frontmen

		cls._frontmen_cache = spec_path
		frontmen = []
		names = {}
		registry = rttr.load_rttr(cls.get_spec_path(), game_path)
		if not registry: return frontmen

		for frontman in registry.frontmen or []:
			frontman_id = f'FRONTMEN_{frontman.technicalName.upper()}'
			image = _load_preview_image(frontman_id, frontman.images.Medium)
			frontmen.append((frontman_id, frontman.name.message, '', image, len(frontmen)))
			names[frontman_id] = frontman

		cls._frontmen = frontmen
		cls._frontmen_data = names
		return frontmen

	def draw_extended(self, _):
		# todo: list skins:
		#  elements
		pass

	def execute_core(self, _):
		cls = self.__class__

		if not cls._frontmen_data:
			return

		data = cls._frontmen_data[self.spec_selector]
		elements = data.elements.default
		if not isinstance(elements, list):
			return

		slot_assignments = {}
		slots = {}
		game_path = AddonPreferences.instance().game_data_path

		name = data.name.message
		blend_obj = bpy.data.objects.new(name, None)

		for element in elements:
			if not isinstance(element, RTTRObject):
				continue

			prefab_path = element.prefab
			if not prefab_path:
				continue

			slot = element.get('slot', {}).get('handle')
			# todo: style system

			prefab_entity = load_prefab(prefab_path, game_path)
			slot_prefab = create_prefab(prefab_entity, game_path, parent=blend_obj, slots=slots)
			if slot_prefab and slot:
				if slot not in slot_assignments:
					slot_assignments[slot] = []
				slot_assignments[slot].append(slot_prefab)
		for slot_name, slot_object in slots.items():
			if slot_name not in slot_assignments:
				continue
			for slot_prefab in slot_assignments[slot_name]:
				slot_prefab.parent = slot_object


# noinspection PyTypeChecker
class WorldRegistryOperator(SpecOperator):
	bl_idname = f'{__base_package__}.broengine_spec_world'
	bl_label = 'Import HEAT World'
	bl_text = 'World'
	bl_header = 'Select a World'

	# noinspection PyTypeHints
	spec_selector: bpy.props.EnumProperty(
		name=bl_header,
		items=lambda self, _: WorldRegistryOperator.get_spec()
	)

	_worlds: list[tuple[str, str, str, str, int]] | None = None
	_world_cache: str | None = None
	_world_names: dict[str, tuple[str, str]] | None = None

	@classmethod
	def get_spec_path(cls):
		return 'storages/arenas_demo.specs'

	@classmethod
	def get_spec_name(cls, name: str) -> str | None:
		if not cls._world_names:
			return None

		return cls._world_names[name][0]

	@classmethod
	def get_spec(cls) -> list[tuple[str, str, str, str, int]]:
		game_path = AddonPreferences.instance().game_data_path
		spec_path = os.path.join(game_path, cls.get_spec_path())

		if cls._worlds and cls._world_cache == spec_path:
			return cls._worlds

		cls._world_cache = spec_path
		worlds = []
		names = {}
		registry = rttr.load_rttr(cls.get_spec_path(), game_path)
		if not registry: return worlds

		seen = set()
		for battle_world in registry.battleWorlds or []:
			if battle_world.baseWorldPath in seen: continue
			seen.add(battle_world.baseWorldPath)
			name = battle_world.displayName.message
			mode = battle_world.gameMode.handle
			name = name[:-(len(mode) + 1)]
			world_id = f'WORLD_{battle_world.name.upper()}'
			world_id = world_id[:-(len(mode) + 1)]
			image = _load_preview_image(world_id, battle_world.playButtonBackground)
			worlds.append((world_id, name, '', image, len(worlds)))
			names[world_id] = (name, battle_world.baseWorldPath)

		if '07_projectphoenix_pve_ftue' not in seen and '/worlds/07_projectphoenix.world' in seen:
			world_id = 'WORLD_07_PROJECTPHOENIX_PVE_FTUE'
			image = _load_preview_image('WORLD_07_PROJECTPHOENIX',
			                            '/ui/assets/worlds/07_projectphoenix/07_projectphoenix_play_button.png')
			name = 'Project Phoenix PVE'
			worlds.append((world_id, name, '', image, len(worlds)))
			names[world_id] = name

		cls._worlds = worlds
		cls._world_names = names
		return worlds

	def draw_extended(self, _):
		# todo: list game modes
		pass

	def execute_core(self, _):
		cls = self.__class__

		if not cls._world_names:
			return

		game_path = AddonPreferences.instance().game_data_path
		world_name, world_path = cls._world_names.get(self.spec_selector)
		blend_obj = bpy.data.objects.new(world_name, None)
		root_entity = load_prefab(world_path, game_path)
		create_prefab(root_entity, game_path, parent=blend_obj, cache={})


class BroSpecMenu(bpy.types.Menu):
	bl_idname = f'TOPBAR_MT_FILE_bro_file_import_spec'
	bl_label = 'Specification'

	def draw(self, _):
		self.layout.operator(VehicleRegistryOperator.bl_idname, text=VehicleRegistryOperator.bl_text)
		self.layout.operator(FrontmenRegistryOperator.bl_idname, text=FrontmenRegistryOperator.bl_text)
		self.layout.operator(WorldRegistryOperator.bl_idname, text=WorldRegistryOperator.bl_text)

	@classmethod
	def poll(cls, context: Context):
		return (VehicleRegistryOperator.poll(context) or
		        FrontmenRegistryOperator.poll(context) or
		        WorldRegistryOperator.poll(context))


class BroMenu(bpy.types.Menu):
	bl_idname = f'TOPBAR_MT_FILE_bro_file_import'
	bl_label = 'BroEngine'

	def draw(self, _):
		self.layout.operator(MeshOperator.bl_idname, text='Mesh (.mesh)')
		self.layout.operator(SkelOperator.bl_idname, text='Skeleton (.skel)')
		self.layout.operator(SceneOperator.bl_idname, text='Scene (.prefab; .world)')
		self.layout.operator(MaterialOperator.bl_idname, text='Material (.material)')
		self.layout.menu(BroSpecMenu.bl_idname, text=BroSpecMenu.bl_label)


def bro_menu_import(self, _):
	self.layout.menu(BroMenu.bl_idname, text=BroMenu.bl_label)


def register():
	global _bro_image_collection
	assert _bro_image_collection is None
	_bro_image_collection = bpy.utils.previews.new()

	bpy.utils.register_class(MeshOperator)
	bpy.utils.register_class(SkelOperator)
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
	global _bro_image_collection
	assert _bro_image_collection is not None
	bpy.utils.previews.remove(_bro_image_collection)
	_bro_image_collection = None

	bpy.utils.unregister_class(MeshOperator)
	bpy.utils.unregister_class(SkelOperator)
	bpy.utils.unregister_class(SceneOperator)
	bpy.utils.unregister_class(MaterialOperator)
	bpy.utils.unregister_class(VehicleRegistryOperator)
	bpy.utils.unregister_class(FrontmenRegistryOperator)
	bpy.utils.unregister_class(WorldRegistryOperator)
	bpy.utils.unregister_class(AddonPreferences)
	bpy.utils.unregister_class(BroMenu)
	bpy.utils.unregister_class(BroSpecMenu)
	bpy.types.TOPBAR_MT_file_import.remove(bro_menu_import)
