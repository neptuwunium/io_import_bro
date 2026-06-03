# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure, c_uint, c_ushort, c_float


class AnimHeader(LittleEndianStructure):
	_pack_ = 1
	_fields_ = [
		('bone_count', c_ushort),
		('frame_count', c_uint),
		('duration', c_float),
	]
