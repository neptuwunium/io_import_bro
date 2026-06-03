# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import math

import bpy
from mathutils import Matrix, Vector

from .. import __package__ as __base_package__

C = Matrix((
	(1.0, 0.0, 0.0, 0.0),
	(0.0, 0.0, 1.0, 0.0),
	(0.0, 1.0, 0.0, 0.0),
	(0.0, 0.0, 0.0, 1.0)
))

MIN_BONE_LENGTH = 0.01
ICOSPHERE_SCALE = 0.1

def _create_icosphere(name=f"{__base_package__}.skeleton_shape"):
	if name in bpy.data.objects:
		return bpy.data.objects[name]

	phi = (1.0 + math.sqrt(5.0)) / 2.0

	vertices = [
		(-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
		(0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
		(phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)
	]

	vertices = [Vector(v).normalized() * ICOSPHERE_SCALE for v in vertices]

	faces = [
		(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
		(1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
		(3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
		(9, 8, 1), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7)
	]

	mesh = bpy.data.meshes.new(name=name)
	mesh.from_pydata(vertices, [], faces)
	mesh.update()
	return bpy.data.objects.new(name, mesh)


def create_skeleton(skel, root):
	armature = bpy.data.armatures.new(root.name)
	armature['bro_source_matrix'] =  skel.matrices.copy()

	blend_obj = bpy.data.objects.new(root.name, armature)
	blend_obj.parent = root.parent
	root.parent = blend_obj
	bpy.context.collection.objects.link(blend_obj)

	bpy.context.view_layer.objects.active = blend_obj
	blend_obj.select_set(True)
	bpy.ops.object.mode_set(mode='EDIT')

	skel_values = zip(skel.names, skel.matrices, skel.hierarchy, skel.children)
	for name, matrix, parent_index, children in skel_values:
		edit_bone = armature.edit_bones.new(name)

		# noinspection PyTypeChecker
		edit_bone.matrix = C @ matrix.transposed() @ C
		edit_bone.length = MIN_BONE_LENGTH

		if parent_index != 0xffff:
			edit_bone.parent = armature.edit_bones[skel.names[parent_index]]

	bpy.ops.object.mode_set(mode='OBJECT')

	shape = _create_icosphere()

	for pose_bone in blend_obj.pose.bones:
		pose_bone.custom_shape = shape

	return blend_obj


if __name__ == '__main__':
	import sys
	import os.path
	from ..format.skel import SkelFile

	with open(sys.argv[-1], 'rb') as f:
		skel_obj = bpy.data.objects.new(os.path.splitext(os.path.basename(sys.argv[-1]))[0], None)
		create_skeleton(SkelFile(f), skel_obj)
