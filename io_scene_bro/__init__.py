# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

bl_info = {
	'name': 'BroEngine Importer',
	'author': 'neptuwunium',
	'version': (1, 3, 1),
	'blender': (5, 1, 0),
	'location': 'File > Import > BroEngine',
	'description': '3rd Party BroEngine Importer, optimized for HEAT',
	'warning': '',
	'tracker_url': 'https://github.com/neptuwunium/io_scene_bro',
	'support': 'COMMUNITY',
	'category': 'Import-Export'
}

from . import blender


def register(): blender.register()


def unregister(): blender.unregister()


if __name__ == '__main__':
	register()
