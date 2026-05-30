# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure, c_uint, c_ushort


class SkelHeader(LittleEndianStructure):
	_pack_ = 1
	_fields_ = [
		('version', c_uint),
		('bone_count', c_ushort),
		('bone_data_offset', c_uint),
	]
