# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import bpy
from mathutils import Matrix, Vector, Quaternion

C = Matrix((
	(1.0, 0.0, 0.0, 0.0),
	(0.0, 0.0, 1.0, 0.0),
	(0.0, 1.0, 0.0, 0.0),
	(0.0, 0.0, 0.0, 1.0)
))

def create_animation(anim, root):
	bpy.context.view_layer.objects.active = root
	bpy.ops.object.mode_set(mode='POSE')

	for pose_bone in root.pose.bones:
		pose_bone.rotation_mode = 'QUATERNION'

	if not root.animation_data:
		root.animation_data_create()

	action = bpy.data.actions.new(name="ImportedAnimation")
	root.animation_data.action = action
	skel = anim.skeleton

	for frame_index in range(anim.header.frame_count):
		for bone_index, track in enumerate(anim.bones):
			pos = track.position[frame_index] if not track.position_is_const else track.position[0]
			rot = track.rotation[frame_index] if not track.rotation_is_const else track.rotation[0]
			scale = track.scale[frame_index] if not track.scale_is_const else track.scale[0]

			# noinspection PyTypeChecker
			anim_loc = Matrix.Translation(Vector(pos))
			anim_quat = Quaternion(rot)
			anim_quat.conjugate()
			anim_rot = anim_quat.to_matrix().to_4x4()
			anim_scale = Matrix.Scale(scale, 4)

			# noinspection PyTypeChecker
			local_mat = anim_loc @ anim_rot @ anim_scale
			blender_mat = C @ local_mat @ C

			# this is borked
			pose_bone = root.pose.bones[skel.names[bone_index]]
			pose_bone.matrix = blender_mat

			if not track.position_is_const or frame_index == 0:
				pose_bone.keyframe_insert(data_path="location", frame=frame_index)
			if not track.rotation_is_const or frame_index == 0:
				pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_index)
			if not track.scale_is_const or frame_index == 0:
				pose_bone.keyframe_insert(data_path="scale", frame=frame_index)
	bpy.ops.object.mode_set(mode='OBJECT')

if __name__ == '__main__':
	import sys
	import os.path
	from ..format.anim import AnimFile
	from .import_skel import create_skeleton

	with open(sys.argv[-1], 'rb') as f:
		skel_obj = bpy.data.objects.new(os.path.splitext(os.path.basename(sys.argv[-1]))[0], None)
		anim_file = AnimFile(f)
		armature_obj = create_skeleton(anim_file.skeleton, skel_obj)
		create_animation(anim_file, armature_obj)
