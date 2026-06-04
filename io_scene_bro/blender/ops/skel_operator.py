# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

import bpy
import bpy.utils.previews
from bpy.props import StringProperty

from ._import_template import _ImportTemplate
from ..import_skel import create_skeleton
from ... import __package__ as __base_package__
from ...format.skel import SkelFile


# noinspection PyTypeHints
class SkelOperator(_ImportTemplate):
	bl_idname = f'{__base_package__}.import_skel'
	bl_label = 'Import BroEngine Skeleton'
	bl_description = 'Import a BroEngine Skeleton (.skel file)'

	filter_glob: StringProperty(default='*.skel', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			name = os.path.splitext(os.path.basename(path))[0]
			blend_obj = bpy.data.objects.new(name, None)
			create_skeleton(SkelFile(file), blend_obj)
