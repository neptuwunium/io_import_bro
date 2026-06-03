# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

if __name__ == '__main__':
	import cProfile

	cProfile.run(
		'import bpy; bpy.ops.io_scene_bro.broengine_spec_vehicle(spec_selector="VEHICLE_A01_CHRYSLER_XM1_VOLCANO")',
		'import_vehicle.prof')

	import pstats

	p = pstats.Stats('import_vehicle.prof')
	p.sort_stats('cumulative').print_stats(20)
