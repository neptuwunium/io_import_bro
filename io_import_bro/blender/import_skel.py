# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import bpy
from mathutils import Matrix, Vector

C = Matrix((
	(1.0, 0.0, 0.0, 0.0),
	(0.0, 0.0, 1.0, 0.0),
	(0.0, 1.0, 0.0, 0.0),
	(0.0, 0.0, 0.0, 1.0)
))

MIN_BONE_LENGTH = 0.05


def create_skeleton(skel, root):
	armature = bpy.data.armatures.new(root.name)
	blend_obj = bpy.data.objects.new(root.name, armature)
	blend_obj.parent = root.parent
	root.parent = blend_obj
	bpy.context.collection.objects.link(blend_obj)

	bpy.context.view_layer.objects.active = blend_obj
	blend_obj.select_set(True)
	bpy.ops.object.mode_set(mode='EDIT')

	bones = []
	for name, matrix, parent_index, children in zip(skel.names, skel.matrices, skel.hierarchy, skel.children):
		edit_bone = armature.edit_bones.new(name)

		bones.append(edit_bone.name)

		# noinspection PyTypeChecker
		blender_matrix: Matrix = C @ matrix @ C

		edit_bone.head = blender_matrix.to_translation()

		if len(children) == 1:
			# noinspection PyTypeChecker
			child_blender_matrix: Matrix = C @ skel.matrices[children[0]] @ C
			edit_bone.tail = child_blender_matrix.to_translation()
		else:
			edit_bone.tail = edit_bone.head + (blender_matrix.to_3x3() @ Vector((0, 1, 0))) * MIN_BONE_LENGTH

		if (edit_bone.tail - edit_bone.head).length < MIN_BONE_LENGTH:
			local_y_dir = blender_matrix.to_3x3() @ Vector((0, 1, 0))
			edit_bone.tail = edit_bone.head + (local_y_dir * MIN_BONE_LENGTH)

		edit_bone.matrix = blender_matrix

		if parent_index != 0xffff:
			edit_bone.parent = armature.edit_bones[bones[parent_index]]

	bpy.ops.object.mode_set(mode='OBJECT')
	blend_obj["bro_brones"] = bones

	return blend_obj, bones


if __name__ == '__main__':
	import sys
	import os.path
	from ..format.skel import SkelFile

	with open(sys.argv[-1], 'rb') as f:
		skel_obj = bpy.data.objects.new(os.path.splitext(os.path.basename(sys.argv[-1]))[0], None)
		create_skeleton(SkelFile(f), skel_obj)
