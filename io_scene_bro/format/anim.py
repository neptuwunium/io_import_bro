# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ctypes import sizeof
from typing import IO

import numpy as np

from .skel import SkelFile
from .structs.anim_struct import *


class AnimTrack:
	def __init__(self, stream, frame_count):
		self.rotation_is_const = stream.read(1)[0] == 1
		rotation_data = stream.read((1 if self.rotation_is_const else frame_count) * 16)
		# noinspection PyTypeChecker
		self.rotation = np.frombuffer(rotation_data, dtype=np.float32).reshape((-1, 4))[:, [3, 0, 1, 2]]

		self.position_is_const = stream.read(1)[0] == 1
		rotation_data = stream.read((1 if self.position_is_const else frame_count) * 12)
		self.position = np.frombuffer(rotation_data, dtype=np.float32).reshape((-1, 3))

		self.scale_is_const = stream.read(1)[0] == 1
		scale_data = stream.read((1 if self.scale_is_const else frame_count) * 4)
		# noinspection PyTypeChecker
		self.scale = np.frombuffer(scale_data, dtype=np.float32)


class AnimFile:
	def __init__(self, stream: IO[bytes]):
		header = AnimHeader.from_buffer_copy(stream.read(sizeof(AnimHeader)))
		self.header = header
		self.prefab_track = AnimTrack(stream, header.frame_count)
		self.bones = [AnimTrack(stream, header.frame_count) for _ in range(header.bone_count)]
		self.skeleton = SkelFile(stream)


if __name__ == '__main__':
	import sys

	with open(sys.argv[1], 'rb') as f:
		anim = AnimFile(f)
		print(anim)
