# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

bl_info = {
	'name': 'BroEngine Importer',
	'author': 'neptuwunium',
	'version': (1, 0, 1),
	'blender': (4, 5, 0),
	'location': 'File > Import',
	'description': 'Import BroEngine Assets',
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
