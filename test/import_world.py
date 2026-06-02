# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

if __name__ == '__main__':
	import cProfile

	cProfile.run("import bpy; bpy.ops.io_scene_bro.broengine_spec_world(spec_selector='WORLD_09_MOONSHOT')",
	             "import_world.prof")

	import pstats

	p = pstats.Stats("import_world.prof")
	p.sort_stats("cumulative").print_stats(20)
