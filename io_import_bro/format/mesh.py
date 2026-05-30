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
		assert header.flags == 0
		assert header.submesh_count <= 0xff

		self.submeshes = []
		for index in range(header.submesh_count):
			name_length = struct.unpack("<I", stream.read(4))[0]
			name = stream.read(name_length).decode("utf-8")
			submesh_header = SubmeshHeader.from_buffer_copy(stream.read(sizeof(SubmeshHeader)))
			assert submesh_header.flags == 0
			self.submeshes.append((name, submesh_header))

		vertex_count = struct.unpack("<I", stream.read(4))[0]

		position_type = stream.read(1)[0]
		if position_type == 0:
			self.positions = np.frombuffer(stream.read(vertex_count * 12), dtype=np.float32).reshape((-1, 3))
		elif position_type == 1:
			self.positions = (np.delete(
				np.frombuffer(stream.read(vertex_count * 8), dtype=np.float16).reshape((-1, 4)), 3, axis=1)
			                  .astype(np.float32))

		self.tangents = MeshFile._decompress_normal(stream, vertex_count)
		self.normals = MeshFile._decompress_normal(stream, vertex_count)

		uv_count = struct.unpack("<I", stream.read(4))[0]
		assert uv_count <= 3

		self.uv_layers = []
		for index in range(uv_count):
			uv_type = stream.read(1)[0]
			if uv_type == 0:
				self.uv_layers.append(np.frombuffer(stream.read(vertex_count * 8), dtype=np.float32).reshape((-1, 2)))
			elif uv_type == 1:
				self.uv_layers.append(
					np.frombuffer(stream.read(vertex_count * 4), dtype=np.float16).reshape((-1, 2)).astype(np.float32))
			else:
				assert False

		color_type = stream.read(1)[0]
		if color_type == 0:
			self.colors = None
		elif color_type == 1:
			# noinspection PyTypeChecker
			self.colors = np.frombuffer(stream.read(vertex_count * 4), dtype=np.byte).reshape((-1, 4)) / 255.0
		else:
			assert False

		index_buffer_size = struct.unpack("<I", stream.read(4))[0]
		index_buffer = stream.read(index_buffer_size * 4)
		index_dtype = np.uint32 if vertex_count > 0xffff else np.uint16
		if vertex_count < 0xffff and index_buffer_size % 3 == 2:
			index_buffer = index_buffer[:(index_buffer_size * 4) - 2]

		# noinspection PyTypeChecker
		self.indices = np.frombuffer(index_buffer, dtype=index_dtype).astype(np.uint32).reshape((-1, 3))

		skin_type = stream.read(1)[0]
		self.blend_weights = None
		self.blend_indices = None
		self.skin_indices = None
		self.skeleton = None
		if skin_type != 0:
			if skin_type == 1:  # SkinningType::Soft
				# blend_indices = 8-bits for number of bones, 24-bits for index
				# blend_weights = 16-bits for index, 16 bits for weight (float16)
				#
				# cursed, but this is actually easier to import into blender
				weight_count = struct.unpack("<I", stream.read(4))[0]
				assert weight_count <= 0xffffff
				self.blend_weights = np.frombuffer(stream.read(weight_count * 4), dtype=np.dtype([
					('weight', np.float16),
					('index', np.uint16),
				]))
				indirection = np.frombuffer(stream.read(vertex_count * 4), dtype=np.uint32)
				self.blend_indices = np.column_stack((indirection & 0xffffff, np.uint8(indirection >> 24)))
			elif skin_type == 2:  # SkinningType::Hard = 1.0 weight for each bone
				# noinspection PyTypeChecker
				self.skin_indices = np.frombuffer(stream.read(vertex_count * 2), dtype=np.uint16)
			else:
				assert False

			self.skeleton = SkelFile(stream)

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
		mesh = MeshFile(f)
		print(mesh)
