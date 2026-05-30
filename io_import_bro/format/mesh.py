# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import struct
from ctypes import sizeof
from typing import IO

import numpy as np

from .skel import SkelFile
from .structs.mesh_struct import *


class MeshFile:
	def __init__(self, stream: IO[bytes]):
		header = MeshHeader.from_buffer_copy(stream.read(sizeof(MeshHeader)))
		self.header = header
		assert header.version == 25
		assert header.submesh_count <= 0xff

		self.submeshes = {}
		for index in range(header.submesh_count):
			name_length = struct.unpack("<I", stream.read(4))[0]
			name = stream.read(name_length).decode("utf-8")
			submesh_header = SubmeshHeader.from_buffer_copy(stream.read(sizeof(SubmeshHeader)))
			assert submesh_header.unknown == 0

			self.submeshes[name] = submesh_header

		vertex_count = struct.unpack("<I", stream.read(4))[0]

		position_type = stream.read(1)[0]
		if position_type == 0:
			# noinspection PyTypeChecker
			self.positions = np.frombuffer(stream.read(vertex_count * 12), dtype=np.float32).reshape((-1, 3))
		elif position_type == 1:
			self.positions = np.delete(np.frombuffer(stream.read(vertex_count * 8), dtype=np.float16).reshape((-1, 4)),
			                           3, axis=1).astype(np.float32)

		self.tangents = MeshFile._decompress_normal(stream, vertex_count)
		self.normals = MeshFile._decompress_normal(stream, vertex_count)

		uv_count = struct.unpack("<I", stream.read(4))[0]
		assert uv_count <= 3

		self.uvs = []
		for index in range(uv_count):
			uv_type = stream.read(1)[0]
			if uv_type == 0:
				self.uvs.append(
					np.frombuffer(stream.read(vertex_count * 8), dtype=np.float32).reshape((-1, 2)).astype(np.float32))
			elif uv_type == 1:
				self.uvs.append(
					np.frombuffer(stream.read(vertex_count * 4), dtype=np.float16).reshape((-1, 2)).astype(np.float32))
			else:
				assert False

		color_type = stream.read(1)[0]
		if color_type == 0:
			self.colors = None
		elif color_type == 1:
			# noinspection PyTypeChecker
			self.colors = np.frombuffer(stream.read(color_type * 4), dtype=np.byte).reshape((-1, 4)) / 255.0
		else:
			assert False

		index_buffer_size = struct.unpack("<I", stream.read(4))[0]
		self.indices = stream.read(index_buffer_size * 4)

		skin_type = stream.read(1)[0]
		self.blend_weights = None
		self.blend_indices = None
		self.skeleton = None
		if skin_type != 0:
			if skin_type == 1:  # SkinningType::Soft
				# weight_count = 0x0002EB49
				# blend_indices[-1] = 0x0402EB45 = 0x04 bones at 0x02EB45
				# blend_weights[0x02EB45] = 0x00E13B12 = bone 0x00E1 weight 0x3B12
				# blend_weights[0x02EB46] = 0x00E224F9 = bone 0x00E2 weight 0x24F9
				# blend_weights[0x02EB47] = 0x00E32A2E = bone 0x00E3 weight 0x2A2E
				# blend_weights[0x02EB48] = 0x00FF2A2E = bone 0x00FF weight 0x2A2E
				# sum(bitcast_float16(blend_weights[0x02EB45:] & 0xffff)) = 1.0
				#
				# blend_indices = 8-bits for number of bones, 24-bits for index
				# blend_weights = 16-bits for index, 16 bits for weight (float16)
				#
				# cursed, but this is actually easier to import into blender
				weight_count = struct.unpack("<I", stream.read(4))[0]
				assert weight_count <= 0xffffff
				# noinspection PyTypeChecker
				self.blend_weights = np.frombuffer(stream.read(weight_count * 4), dtype=np.uint32)
				# noinspection PyTypeChecker
				self.blend_indices = np.frombuffer(stream.read(vertex_count * 4), dtype=np.uint32)
			# todo: unpack me here
			elif skin_type == 2:  # SkinningType::Hard = 1.0 weight for each bone
				self.blend_weights = None
				self.blend_indices = np.frombuffer(stream.read(vertex_count * 2), dtype=np.uint16).astype(np.uint32)
			else:
				assert False
			self.skeleton = SkelFile(stream)

	# noinspection PyUnresolvedReferences
	@classmethod
	def _decompress_normal(cls, stream, vertex_count):
		packed = np.frombuffer(stream.read(vertex_count * 4), dtype=np.uint32)
		x_int = packed & 0x3FF
		y_int = (packed >> 10) & 0x3FF
		z_int = (packed >> 20) & 0x3FF
		x = (x_int / 511.0) - 1.0
		y = (y_int / 511.0) - 1.0
		z = (z_int / 511.0) - 1.0
		x = np.clip(x, -1.0, 1.0)
		y = np.clip(y, -1.0, 1.0)
		z = np.clip(z, -1.0, 1.0)
		vectors = np.column_stack((x, y, z)).astype(np.float32)
		lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
		np.divide(vectors, lengths, out=vectors, where=lengths != 0)
		# w_int = (packed >> 30) & 0x3
		# w_signs = np.where(w_int == 0, -1.0, 1.0).astype(np.float32)
		return vectors


if __name__ == '__main__':
	import sys

	with open(sys.argv[1], 'rb') as f:
		skel = MeshFile(f)
		print(skel)
