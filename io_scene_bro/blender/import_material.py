# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import logging
import os.path

import bpy

from .. import __package__ as __base_package__
from ..prefab.rttr import get_vfs_path

LOG = logging.getLogger(__name__)
SPACING = 25

MATERIAL_DATA_KEY = f'{__base_package__}.material_id'
NODE_DATA_KEY = f'{__base_package__}.property_target'


def load_image(texture_path, root_path):
	path = get_vfs_path(texture_path, root_path)
	if not os.path.exists(path):
		path = path + '.dds'
	if not os.path.exists(path):
		return None

	image = bpy.data.images.load(path, check_existing=True)
	image.colorspace_settings.name = 'Non-Color'
	image.alpha_mode = 'CHANNEL_PACKED'

	return image


# noinspection PyUnresolvedReferences
def bind_material(material):
	if not material:
		return

	group_name = material.get(MATERIAL_DATA_KEY)
	if not group_name:
		return

	group_node = None
	out_node = None
	node_tree = material.node_tree

	for node in material.node_tree.nodes:
		if node.bl_idname == 'ShaderNodeGroup' and node.name == group_name:
			group_node = node
		elif node.bl_idname == 'ShaderNodeOutputMaterial':
			out_node = node
			break

		if group_node and out_node:
			break

	if group_node is None or out_node is None:
		return

	if group_node.outputs:
		node_tree.links.new(group_node.outputs[0], out_node.inputs[0])

	if not group_node.inputs:
		return

	for node in material.node_tree.nodes:
		property_name = node.get(NODE_DATA_KEY)
		if not property_name:
			continue

		if property_name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[property_name])

		if node.bl_idname == 'ShaderNodeTexImage':
			property_name = property_name + ' Alpha'
			if property_name in group_node.inputs:
				node_tree.links.new(node.outputs[1], group_node.inputs[property_name])


def bind_materials(objs=None):
	if objs is None:
		for material in bpy.data.materials:
			bind_material(material)
		return

	for obj in objs:
		if not obj.material_slots:
			continue

		for material in obj.material_slots:
			bind_material(material.material)


def _create_default_tree(node_tree: bpy.types.ShaderNodeTree):
	node_tree.interface.new_socket(name="Surface", in_out='OUTPUT', socket_type='NodeSocketShader')

	group_input = node_tree.nodes.new(type='NodeGroupInput')
	group_input.location = (-200, 0)

	group_output = node_tree.nodes.new(type='NodeGroupOutput')
	group_output.location = (400, 0)

	principled_bsdf = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
	principled_bsdf.location = (100, 0)

	node_tree.links.new(principled_bsdf.outputs['BSDF'], group_output.inputs['Surface'])


def create_material(material, name, root_path):
	name = f'{name}::{hex(material.hash_id)[2:]}'

	if name in bpy.data.materials:
		return bpy.data.materials[name]

	LOG.info('creating material "%s"', name)
	blend_material = bpy.data.materials.new(name=name)
	if bpy.app.version < (5, 0):
		blend_material.use_nodes = True

	node_tree = blend_material.node_tree

	group_name = os.path.splitext(os.path.basename(material.effect))[0]
	blend_material[MATERIAL_DATA_KEY] = group_name

	while node_tree.nodes:
		node_tree.nodes.remove(node_tree.nodes[0])

	group_node = node_tree.nodes.new('ShaderNodeGroup')
	group_node.label = group_node.name = group_name

	out_node = node_tree.nodes.new('ShaderNodeOutputMaterial')
	group_node.location = 0, 0
	out_node.location = group_node.width + SPACING, 0

	if group_name in bpy.data.node_groups:
		group_node.node_tree = bpy.data.node_groups[group_name]
	else:
		LOG.warning('unknown shader "%s" on material "%s", creating default', group_name, name)
		group_node.node_tree = bpy.data.node_groups.new(group_name, type='ShaderNodeTree')
		_create_default_tree(group_node.node_tree)

	if group_node.outputs:
		node_tree.links.new(group_node.outputs[0], out_node.inputs[0])

	x = -int(group_node.width + SPACING)
	y = 0

	width = 0

	for name, texture in material.properties.textures.items():
		alpha_node_name = name + ' Alpha'
		node = node_tree.nodes.new('ShaderNodeTexImage')
		node[NODE_DATA_KEY] = name
		node.image = load_image(texture, root_path)
		node.location = x - 100, y
		node.label = node.name = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		if alpha_node_name in group_node.inputs:
			node_tree.links.new(node.outputs[1], group_node.inputs[alpha_node_name])
		y -= int(node.height + SPACING + 175)
		if node.width > width:
			width = node.width

	if width > 0:
		x -= int(width + SPACING)
	width = 0
	y = 0

	for name, value in material.properties.floats.items():
		node = node_tree.nodes.new('ShaderNodeValue')
		node[NODE_DATA_KEY] = name
		node.location = x, y
		node.outputs[0].default_value = value
		node.label = node.name = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height / 2 + SPACING)
		if node.width > width:
			width = node.width

	for name, value in material.properties.integers.items():
		node = node_tree.nodes.new('ShaderNodeValue')
		node[NODE_DATA_KEY] = name
		node.location = x, y
		node.outputs[0].default_value = float(value)
		node.label = node.name = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height / 2 + SPACING)
		if node.width > width:
			width = node.width

	for name, value in material.properties.bools.items():
		node = node_tree.nodes.new('ShaderNodeValue')
		node[NODE_DATA_KEY] = name
		node.location = x, y
		node.outputs[0].default_value = 1.0 if value else 0
		node.label = node.name = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height / 2 + SPACING)
		if node.width > width:
			width = node.width

	if width > 0:
		x -= int(width + SPACING)
	y = 0

	for name, value in material.properties.colors.items():
		alpha_node_name = name + ' Alpha'
		node = node_tree.nodes.new('FunctionNodeInputVector')
		node[NODE_DATA_KEY] = name
		node.location = x, y
		node.vector = value.xyz
		node.label = node.name = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height - 10 + SPACING)

		node = node_tree.nodes.new('ShaderNodeValue')
		node[NODE_DATA_KEY] = alpha_node_name
		node.location = x, y
		node.outputs[0].default_value = value.w
		node.label = node.name = alpha_node_name
		if alpha_node_name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[alpha_node_name])
		y -= int(node.height / 2 + SPACING)

	return blend_material


if __name__ == '__main__':
	import sys
	from ..prefab.material import load_material

	root_entity = load_material(sys.argv[-1], sys.argv[-2])
	create_material(root_entity, os.path.splitext(os.path.basename(sys.argv[-1]))[0], sys.argv[-2])
