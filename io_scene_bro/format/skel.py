# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import struct
from ctypes import sizeof
from typing import IO

from mathutils import Matrix

from .structs.skel_struct import *


class SkelFile:
	def __init__(self, stream: IO[bytes]):
		base_pos = stream.tell()
		header = SkelHeader.from_buffer_copy(stream.read(sizeof(SkelHeader)))
		self.header = header
		assert header.version == 4

		self.hierarchy = []
		self.children = []
		self.names = []
		self.matrices = []

		bone_hierarchy_offset = base_pos + 14
		bone_data_offset = base_pos + 10 + header.bone_data_offset  # offsetof(bone_data_offset) + 4

		hierarchy_offsets = struct.unpack(f'<{header.bone_count}I', stream.read(4 * header.bone_count))

		stream.seek(bone_data_offset)
		matrix_data = struct.unpack(f'<{header.bone_count * 16}f', stream.read(4 * 16 * header.bone_count))
		name_pos = stream.tell()

		for index in range(0, header.bone_count):
			stream.seek(bone_hierarchy_offset + hierarchy_offsets[index])
			(parent_id, child_count) = struct.unpack('<II', stream.read(8))
			self.hierarchy.append(parent_id)

			bone_children = []
			for child_index in range(0, child_count):
				(_, child_id) = struct.unpack('<II', stream.read(8))
				bone_children.append(child_id)
			self.children.append(bone_children)

			stream.seek(name_pos)
			name_length = struct.unpack('<I', stream.read(4))[0]
			name = stream.read(name_length).decode('utf-8')
			self.names.append(name)
			name_pos = stream.tell()

			matrix_index = index * 16
			bone_matrix = matrix_data[matrix_index:matrix_index + 16]
			self.matrices.append(Matrix([bone_matrix[i:i + 4] for i in range(0, 16, 4)]))


if __name__ == '__main__':
	import sys

	with open(sys.argv[1], 'rb') as f:
		skel = SkelFile(f)
		print(skel)
