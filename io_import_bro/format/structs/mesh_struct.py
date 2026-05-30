# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure, c_uint, c_int, c_float

from .c3dmath import Vector3


class SubmeshHeader(LittleEndianStructure):
	_pack_ = 1
	_fields_ = [
		('flags', c_uint),
		('first_triangle', c_uint),
		('vertex_count', c_uint),
		('triangle_count', c_uint),
	]


class MeshHeader(LittleEndianStructure):
	_pack_ = 1
	_fields_ = [
		('version', c_uint),
		('bbox_min', Vector3),
		('bbox_max', Vector3),
		('scale', Vector3),
		('bias', c_float),
		('flags', c_uint),
		('submesh_count', c_int),
	]
