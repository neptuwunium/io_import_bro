# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure


class SkelHeader(LittleEndianStructure):
	version: int
	bone_count: int
	bone_data_offset: int
