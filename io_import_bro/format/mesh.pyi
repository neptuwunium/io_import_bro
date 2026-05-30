# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import IO, Optional

import numpy as np
import numpy.typing as npt

from .skel import SkelFile
from .structs.mesh_struct import MeshHeader, SubmeshHeader


class MeshFile:
	header: MeshHeader
	submeshes: dict[str, SubmeshHeader]
	positions: npt.NDArray[np.float32]
	normals: npt.NDArray[np.float32]
	tangents: npt.NDArray[np.float32]
	uvs: list[npt.NDArray[np.float32]]
	colors: Optional[npt.NDArray[np.float32]]
	indices: bytes
	blend_weights: Optional[npt.NDArray[np.uint32]]
	blend_indices: Optional[npt.NDArray[np.uint32]]
	skeleton: Optional[SkelFile]

	def __init__(self, stream: IO[bytes]): pass

	@classmethod
	def _decompress_normal(cls, stream: IO[bytes], vertex_count: int) -> np.typing.NDArray[np.float32]: pass
