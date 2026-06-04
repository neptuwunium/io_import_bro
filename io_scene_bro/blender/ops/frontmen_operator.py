# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

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


# noinspection PyTypeChecker
class FrontmenRegistryOperator(_SpecOperator):
	bl_idname = f'{__base_package__}.spec_frontmen'
	bl_label = 'Import HEAT Agent'
	bl_text = 'Agent'
	bl_header = 'Select a Agent'
	bl_description = 'Import a HEAT Agent Prefab'

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
			cls.get_spec()

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
