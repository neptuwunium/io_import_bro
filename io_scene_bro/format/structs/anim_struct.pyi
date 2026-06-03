# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure


class AnimHeader(LittleEndianStructure):
	bone_count: int
	frame_count: int
	duration: float
