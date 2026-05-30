# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import IO, Optional

import numpy as np
import numpy.typing as npt
from numpy.typing import NDArray

from .skel import SkelFile
from .structs.mesh_struct import MeshHeader, SubmeshHeader


class MeshFile:
	header: MeshHeader
	submeshes: dict[str, SubmeshHeader]
	positions: NDArray[np.float32]
	normals: NDArray[np.float32]
	tangents: NDArray[np.float32]
	uvs: list[NDArray[np.float32]]
	colors: Optional[NDArray[np.float32]]
	indices: NDArray[np.uint32]
	blend_weights: Optional[NDArray[np.void]]
	blend_indices: Optional[NDArray[np.void]]
	skin_indices: Optional[NDArray[np.uint16]]
	skeleton: Optional[SkelFile]

	def __init__(self, stream: IO[bytes]): pass

	@classmethod
	def _decompress_normal(cls, stream: IO[bytes], vertex_count: int) -> NDArray[np.float32]: pass
