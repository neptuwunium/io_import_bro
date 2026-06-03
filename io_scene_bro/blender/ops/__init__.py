# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

import bpy
from bpy.app.handlers import persistent

from .addon_preferences import AddonPreferences

_bro_image_collection = None


def _load_preview_image(name, asset_path):
	global _bro_image_collection
	if _bro_image_collection is None:
		return 'MESH_DATA'

	if asset_path is None:
		return 'MESH_DATA'

	if name not in _bro_image_collection:
		game_path = AddonPreferences.instance().game_data_path
		assert game_path is not None

		if asset_path[0] == '/':
			asset_path = asset_path[1:]

		if not asset_path.endswith('.dds'):
			asset_path = asset_path + '.dds'

		asset_path = os.path.join(game_path, asset_path)

		if not os.path.exists(asset_path):
			return 'MESH_DATA'

		# noinspection PyUnresolvedReferences
		_bro_image_collection.load(name, asset_path, 'IMAGE')

	# noinspection PyUnresolvedReferences
	return _bro_image_collection[name].icon_id


def _init_preview_image():
	global _bro_image_collection
	assert _bro_image_collection is None
	_bro_image_collection = bpy.utils.previews.new()


def _deinit_preview_image():
	global _bro_image_collection
	assert _bro_image_collection is not None
	bpy.utils.previews.remove(_bro_image_collection)
	_bro_image_collection = None


@persistent
def _reset_preview_image(_: str):
	_deinit_preview_image()
	_init_preview_image()
