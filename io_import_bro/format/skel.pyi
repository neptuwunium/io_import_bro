# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import IO

from mathutils import Matrix

from .structs.skel_struct import SkelHeader


class SkelFile:
	header: SkelHeader
	hierarchy: list[int]
	matrices: list[Matrix]
	names: list[str]

	def __init__(self, stream: IO[bytes]): pass
