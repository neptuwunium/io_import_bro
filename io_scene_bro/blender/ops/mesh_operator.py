# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import os

from bpy.props import StringProperty

from ._import_template import _ImportTemplate
from ..import_mesh import create_mesh
from ... import __package__ as __base_package__
from ...format.mesh import MeshFile


# noinspection PyTypeHints
class MeshOperator(_ImportTemplate):
	bl_idname = f'{__base_package__}.broengine_mesh'
	bl_label = 'Import Bro Engine Mesh'
	bl_description = 'Import a Bro Engine Mesh (.mesh file)'

	filter_glob: StringProperty(default='*.mesh', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			name = os.path.splitext(os.path.basename(path))[0]
			create_mesh(MeshFile(file), name)
