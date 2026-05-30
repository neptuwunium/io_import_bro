# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import LittleEndianStructure


class Vector2(LittleEndianStructure):
	x: float
	y: float


class Vector3(LittleEndianStructure):
	x: float
	y: float
	z: float


class Vector4(LittleEndianStructure):
	x: float
	y: float
	z: float
	y: float
