# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import bpy
from mathutils import Matrix, Vector, Quaternion

from .import_skel import ARMATURE_DATA_KEY

C = Matrix((
	(1.0, 0.0, 0.0, 0.0),
	(0.0, 0.0, 1.0, 0.0),
	(0.0, 1.0, 0.0, 0.0),
	(0.0, 0.0, 0.0, 1.0)
))


def create_animation(anim, anim_name, root):
	if not ARMATURE_DATA_KEY in root.data:
		return

	bpy.context.view_layer.objects.active = root
	bpy.ops.object.mode_set(mode='POSE')

	for pose_bone in root.pose.bones:
		pose_bone.rotation_mode = 'QUATERNION'

	if not root.animation_data:
		root.animation_data_create()

	action = bpy.data.actions.new(name=anim_name)
	root.animation_data.action = action

	bone_map = [root.pose.bones.get(name) for name in anim.skeleton.names]

	bro_source_matrix = [rna.to_list() for rna in root.data[ARMATURE_DATA_KEY]]
	bro_source_matrix = [Matrix([matrix[i:i + 4] for i in range(0, 16, 4)]) for matrix in bro_source_matrix]

	global_bind_pose = []
	for m in bro_source_matrix:
		# noinspection PyTypeChecker
		global_bind_pose.append(C @ m @ C)

	previous_quats = {}

	for frame_index in range(anim.header.frame_count):
		bpy.context.scene.frame_set(frame_index)

		global_anim_pose = []
		for index, track in enumerate(anim.bones):
			pos = track.position[frame_index] if not track.position_is_const else track.position[0]
			rot = track.rotation[frame_index] if not track.rotation_is_const else track.rotation[0]
			scale = track.scale[frame_index] if not track.scale_is_const else track.scale[0]

			# noinspection PyTypeChecker
			anim_matrix = C @ Matrix.LocRotScale(Vector(pos), Quaternion(rot), Vector((scale, scale, scale))) @ C

			parent_index = anim.skeleton.hierarchy[index]
			if parent_index != 0xffff:
				global_anim_pose.append(global_anim_pose[parent_index] @ anim_matrix)
			else:
				global_anim_pose.append(anim_matrix)

		target_pose = {}
		for index, track in enumerate(anim.bones):
			pose_bone = bone_map[index]
			if not pose_bone:
				continue

			delta_global = global_anim_pose[index] @ global_bind_pose[index].inverted()
			target_pose[pose_bone.name] = delta_global @ pose_bone.bone.matrix_local

		for index, track in enumerate(anim.bones):
			pose_bone = bone_map[index]
			if not pose_bone:
				continue

			pose_bone_mesh = target_pose[pose_bone.name]
			mesh_rest = pose_bone.bone.matrix_local

			if pose_bone.parent:
				parent_mesh_rest = pose_bone.parent.bone.matrix_local

				if pose_bone.parent.name in target_pose:
					parent_pose_bone = target_pose[pose_bone.parent.name]
				else:
					parent_pose_bone = parent_mesh_rest

				basis = mesh_rest.inverted() @ parent_mesh_rest @ parent_pose_bone.inverted() @ pose_bone_mesh
			else:
				basis = mesh_rest.inverted() @ pose_bone_mesh

			loc, rot, scale = basis.decompose()

			if pose_bone.name in previous_quats:
				if rot.dot(previous_quats[pose_bone.name]) < 0:
					rot.negate()
			previous_quats[pose_bone.name] = rot.copy()

			pose_bone.location = loc
			pose_bone.rotation_quaternion = rot
			pose_bone.scale = scale

			if not track.position_is_const or frame_index == 0:
				pose_bone.keyframe_insert(data_path='location', frame=frame_index)
			if not track.rotation_is_const or frame_index == 0:
				pose_bone.keyframe_insert(data_path='rotation_quaternion', frame=frame_index)
			if not track.scale_is_const or frame_index == 0:
				pose_bone.keyframe_insert(data_path='scale', frame=frame_index)

	bpy.context.scene.frame_set(0)
	bpy.ops.object.mode_set(mode='OBJECT')


if __name__ == '__main__':
	import sys
	import os.path
	from ..format.anim import AnimFile
	from .import_skel import create_skeleton

	with open(sys.argv[-1], 'rb') as f:
		clip_name = os.path.splitext(os.path.basename(sys.argv[-1]))[0]
		skel_obj = bpy.data.objects.new(clip_name, None)
		anim_file = AnimFile(f)
		armature_obj = create_skeleton(anim_file.skeleton, skel_obj)
		create_animation(anim_file, clip_name, armature_obj)
