# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import math
import os

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, Context, Property, OperatorFileListElement, TOPBAR_MT_file_import
from bpy_extras.io_utils import ImportHelper

from .import_mesh import import_mesh
from .import_skel import create_skeleton
from ..format.mesh import MeshFile
from ..format.skel import SkelFile


# noinspection PyPep8Naming
class _import_template(Operator, ImportHelper):
	bl_options = {'REGISTER', 'UNDO'}

	# noinspection PyTypeHints
	files: CollectionProperty(
		type=bpy.types.OperatorFileListElement,
		options={'HIDDEN', 'SKIP_SAVE'},
	)

	def load(self, path: str): pass

	@classmethod
	def poll(cls, _: Context):
		return True

	def draw(self, context: Context): pass

	def execute(self, _: Context):
		dirname = os.path.dirname(self.filepath)
		for file in self.files:
			# noinspection PyTypeChecker
			self.load(os.path.join(dirname, file.name))
		return {'FINISHED'}


# noinspection PyPep8Naming
class MESH_Operator(_import_template):
	bl_idname = 'import_mesh.broengine_mesh'
	bl_label = 'Import Bro Engine Mesh'

	# noinspection PyTypeHints
	filter_glob: StringProperty(default='*.mesh', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			name = os.path.splitext(os.path.basename(path))[0]
			import_mesh(MeshFile(file), name)


# noinspection PyPep8Naming
class SKEL_Operator(_import_template):
	bl_idname = 'import_mesh.broengine_skel'
	bl_label = 'Import Bro Engine Skeleton'

	# noinspection PyTypeHints
	filter_glob: StringProperty(default='*.skel', options={'HIDDEN'})

	def load(self, path):
		with open(path, 'rb') as file:
			name = os.path.splitext(os.path.basename(path))[0]
			blend_obj = bpy.data.objects.new(name, None)
			armature_obj, _ = create_skeleton(SkelFile(file), blend_obj)
			armature_obj.rotation_euler = (math.pi / 2, 0, 0)


def bro_menu_import(self, _: Context):
	self.layout.operator(MESH_Operator.bl_idname, text="Bro Engine Mesh (.mesh)")
	self.layout.operator(SKEL_Operator.bl_idname, text="Bro Engine Skeleton (.skel)")


def register():
	bpy.utils.register_class(MESH_Operator)
	bpy.utils.register_class(SKEL_Operator)
	bpy.types.TOPBAR_MT_file_import.append(bro_menu_import)


def unregister():
	bpy.utils.unregister_class(MESH_Operator)
	bpy.utils.unregister_class(SKEL_Operator)
	bpy.types.TOPBAR_MT_file_import.remove(bro_menu_import)
