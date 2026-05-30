# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import bpy


def create_skeleton(skel, root):
	armature = bpy.data.armatures.new(root.name)
	blend_obj = bpy.data.objects.new(root.name, armature)
	root.parent = blend_obj
	bpy.context.collection.objects.link(blend_obj)

	bpy.context.view_layer.objects.active = blend_obj
	blend_obj.select_set(True)
	bpy.ops.object.mode_set(mode='EDIT')

	bones = []
	for name, matrix, parent_index in zip(skel.names, skel.matrices, skel.hierarchy):
		edit_bone = armature.edit_bones.new(name)

		bones.append(edit_bone.name)

		edit_bone.head = (0, 0, 0)
		edit_bone.tail = (0, 0.1, 0)
		edit_bone.matrix = matrix

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
