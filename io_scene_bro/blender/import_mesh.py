# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from collections import defaultdict

import bpy
import numpy as np

from .import_skel import create_skeleton


def create_material(name):
	if name in bpy.data.materials:
		return bpy.data.materials[name]
	return bpy.data.materials.new(name=name)


def import_mesh(mesh, name, parent=None, materials=None):
	mesh_data = bpy.data.meshes.new(name)
	blend_obj = bpy.data.objects.new(name, mesh_data)
	blend_obj.parent = parent
	bpy.context.view_layer.active_layer_collection.collection.objects.link(blend_obj)

	if not materials:
		materials = {}

	if mesh.skeleton:
		(armature_obj, bones) = create_skeleton(mesh.skeleton, blend_obj)
	else:
		armature_obj = None
		bones = None

	mesh_data.from_pydata(mesh.positions, [], mesh.indices, shade_flat=False)

	loop_vert_indices = np.empty(len(mesh_data.loops), dtype=np.int32)
	mesh_data.loops.foreach_get('vertex_index', loop_vert_indices)

	for uv_index, uv_list in enumerate(mesh.uv_layers):
		uv_list = uv_list.copy()
		uv_list[:, 1] = 1.0 - uv_list[:, 1]
		loop_uvs = uv_list[loop_vert_indices]
		layer = mesh_data.uv_layers.new(name=f'TEXCOORD_{uv_index}')
		layer.uv.foreach_set('vector', loop_uvs.flatten())

	if mesh.colors is not None:
		layer = mesh_data.color_attributes.new('Color', 'FLOAT_COLOR', 'POINT')
		layer.data.foreach_set('color', mesh.colors.flatten())

	if bones and armature_obj:
		armature = blend_obj.modifiers.new('Armature', 'ARMATURE')
		armature.object = armature_obj

		groups = []
		for bone in bones:
			groups.append(blend_obj.vertex_groups.new(name=bone))

		if mesh.blend_weights is not None and mesh.blend_indices is not None:  # todo
			for vertex_index, (weight_start, bone_count) in enumerate(mesh.blend_indices):
				for weight_index in range(bone_count):
					(weight, bone_index) = mesh.blend_weights[weight_start + weight_index]
					# noinspection PyUnresolvedReferences
					groups[bone_index].add([vertex_index], weight, 'REPLACE')
		elif mesh.skin_indices is not None:
			grouped: dict[int, list[int]] = defaultdict(list)

			for index, bone_index in np.ndenumerate(mesh.skin_indices):
				grouped[int(bone_index)].append(index[0])

			for bone_index, vertices in grouped.items():
				groups[bone_index].add(vertices, 1.0, 'REPLACE')

	material_lookup = {}
	material_indices = []
	for material_name, submesh in mesh.submeshes:
		if material_lookup.get(material_name) is None:
			material_lookup[material_name] = len(mesh_data.materials)
			mesh_data.materials.append(
				materials[material_name] if material_name in materials else create_material(material_name))
		material_indices.append(np.full(submesh.triangle_count, material_lookup[material_name], dtype=np.int32))
	material_indices_cat = np.concatenate(material_indices)
	mesh_data.polygons.foreach_set('material_index', material_indices_cat)

	mesh_data.update()

	mesh_data.validate(clean_customdata=False)
	mesh_data.update(calc_edges=True)
	mesh_data.normals_split_custom_set_from_vertices(mesh.normals.tolist())

	return blend_obj


if __name__ == '__main__':
	import sys
	import os.path
	from ..format.mesh import MeshFile

	with open(sys.argv[-1], 'rb') as f:
		import_mesh(MeshFile(f), os.path.splitext(os.path.basename(sys.argv[-1]))[0])
