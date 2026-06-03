# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import IO

from mathutils import Matrix
import numpy as np
from numpy.typing import NDArray

from .skel import SkelFile
from .structs.anim_struct import AnimHeader


class AnimTrack:
	rotation: NDArray[np.float32]
	position: NDArray[np.float32]
	scale: NDArray[np.float32]
	rotation_is_const: bool
	position_is_const: bool
	scale_is_const: bool

	def __init__(self, stream: IO[bytes], frame_count: int): pass

class AnimFile:
	header: AnimHeader
	skeleton: SkelFile
	prefab_track: AnimTrack
	bones: list[AnimTrack]

	def __init__(self, stream: IO[bytes]): pass
