# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure

from .c3dmath import Vector3


class SubmeshHeader(LittleEndianStructure):
	flags: int
	first_index: int
	vertex_count: int
	face_count: int


class MeshHeader(LittleEndianStructure):
	version: int
	bbox_min: Vector3
	bbox_max: Vector3
	scake: Vector3
	bias: float
	flags: int
	submesh_count: int
