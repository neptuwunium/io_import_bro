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


# noinspection PyTypeChecker
class WorldRegistryOperator(_SpecOperator):
	bl_idname = f'{__base_package__}.spec_world'
	bl_label = 'Import HEAT World'
	bl_text = 'World'
	bl_header = 'Select a World'
	bl_description = 'Import a HEAT World'

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
			cls.get_spec()

		game_path = AddonPreferences.instance().game_data_path
		world_name, world_path = cls._world_names.get(self.spec_selector)
		blend_obj = bpy.data.objects.new(world_name, None)
		root_entity = load_prefab(world_path, game_path)
		create_prefab(root_entity, game_path, parent=blend_obj, cache={})
