# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

import bpy
import bpy.utils.previews
from bpy.props import StringProperty

from ._import_template import _ImportTemplate
from ..import_anim import create_animation
from ..import_skel import create_skeleton
from ... import __package__ as __base_package__
from ...format.anim import AnimFile


# noinspection PyTypeHints
class AnimOperator(_ImportTemplate):
	bl_idname = f'{__base_package__}.import_anim'
	bl_label = 'Import BroEngine Skeleton Animation'
	bl_description = 'Import a BroEngine Skeleton Animation (.anim file)'

	filter_glob: StringProperty(default='*.anim', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			anim_file = AnimFile(file)
			name = os.path.splitext(os.path.basename(path))[0]
			if bpy.context.selected_objects:
				armature_obj = bpy.context.selected_objects[0]
			else:
				skel_obj = bpy.data.objects.new(name, None)
				armature_obj = create_skeleton(anim_file.skeleton, skel_obj)
			create_animation(anim_file, name, armature_obj)
