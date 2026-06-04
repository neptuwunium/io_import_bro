# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import logging
import os

import bpy
import bpy.utils.previews

from . import _load_preview_image
from ._import_template import _SpecOperator
from .addon_preferences import AddonPreferences
from ..import_prefab import create_prefab
from ... import __package__ as __base_package__
from ...prefab import rttr
from ...prefab.loader import load_prefab
from ...prefab.rttr import RTTRObject

LOG = logging.getLogger(__name__)


# noinspection PyTypeChecker
class VehicleRegistryOperator(_SpecOperator):
	bl_idname = f'{__base_package__}.spec_vehicle'
	bl_label = 'Import HEAT Vehicle'
	bl_text = 'Vehicle'
	bl_header = 'Select a Vehicle'
	bl_description = 'Import a HEAT Vehicle Prefab'

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
			cls.get_spec()

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
				LOG.warning('module \'%s\' has prefab overrides!', module.general.name)

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
