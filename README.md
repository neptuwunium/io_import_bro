<!--
SPDX-FileCopyrightText: 2026 Neptuwunium

SPDX-License-Identifier: EUPL-1.2
-->

# io_scene_bro

3rd Party BroEngine Blender Importer, optimized for HEAT

Currently handles:

- mesh files (.mesh)
- skeleton files (.skel)
- animation files (.anim)
- materials (.material)[^vfs][^material]
- prefabs (.world, .prefab)[^vfs]
- HEAT vehicles[^vfs]
- HEAT agents[^vfs]

[^vfs]: Requires the game's VFS to be unpacked with normative paths, i.e. via [wheat](https://github.com/neptuwunium/wheat). Set the path in the settings
[^material]: Also requires decompressed DDS files. Only imports material propreties, actual shading logic needs to be implemented.

Engine File Formats are described [here](https://github.com/neptuwunium/bt/tree/develop/patterns/HEAT) and [here](https://github.com/neptuwunium/bt/blob/develop/includes/HEAT.hexpat).

## Planned

- armor files (.trimesh)

## Notice

This project is not authorized, affiliated or endorsed by Wargaming.net, Wargaming Group Limited or Wargaming International Limited.

"World of Tanks: HEAT", "World of Tanks" are registered trademarks or trademarks of Wargaming Group Limited.
