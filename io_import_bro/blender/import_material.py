# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import logging
import os.path

import bpy
from mathutils import Vector

from io_import_bro.prefab.rttr import get_vfs_path

LOG = logging.getLogger(f'{__name__}.material')
SPACING = 25


def load_image(texture_path, root_path):
	path = get_vfs_path(texture_path, root_path)
	if not os.path.exists(path):
		path = path + ".dds"
	if not os.path.exists(path):
		return None

	image = bpy.data.images.load(path, check_existing=True)
	image.colorspace_settings.name = 'Non-Color'
	image.alpha_mode = 'CHANNEL_PACKED'

	return image


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

	while node_tree.nodes:
		node_tree.nodes.remove(node_tree.nodes[0])

	group_node = node_tree.nodes.new('ShaderNodeGroup')
	group_node.label = group_name

	out_node = node_tree.nodes.new('ShaderNodeOutputMaterial')
	group_node.location = 0, 0
	out_node.location = group_node.width + SPACING, 0

	if group_name in bpy.data.node_groups:
		group_node.node_tree = bpy.data.node_groups[group_name]
		if group_node.outputs:
			node_tree.links.new(group_node.outputs[0], out_node.inputs[0])
	else:
		group_node.node_tree = bpy.data.node_groups.new(group_name, type='ShaderNodeTree')
		LOG.warning('unknown shader "%s" on material "%s"', group_name, name)

	x = -int(group_node.width + SPACING)
	y = 0

	width = 0

	for name, texture in material.properties.textures.items():
		alpha_node_name = name + ' Alpha'
		node = node_tree.nodes.new('ShaderNodeTexImage')
		node.image = load_image(texture, root_path)
		node.location = x - 100, y
		node.label = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		if alpha_node_name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[alpha_node_name])
		y -= int(node.height + SPACING + 175)
		if node.width > width:
			width = node.width

	if width > 0:
		x -= int(width + SPACING)
	width = 0
	y = 0

	for name, value in material.properties.floats.items():
		node = node_tree.nodes.new('ShaderNodeValue')
		node.location = x, y
		node.outputs[0].default_value = value
		node.label = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height / 2 + SPACING)
		if node.width > width:
			width = node.width

	for name, value in material.properties.integers.items():
		node = node_tree.nodes.new('ShaderNodeValue')
		node.location = x, y
		node.outputs[0].default_value = float(value)
		node.label = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height / 2 + SPACING)
		if node.width > width:
			width = node.width

	for name, value in material.properties.bools.items():
		node = node_tree.nodes.new('ShaderNodeValue')
		node.location = x, y
		node.outputs[0].default_value = 1.0 if value else 0
		node.label = name
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
		node = node_tree.nodes.new('ShaderNodeRGB')
		node.location = x, y
		node.outputs[0].default_value = Vector((value.x, value.y, value.z, 1.0))
		node.label = name
		if name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[name])
		y -= int(node.height + 50 + SPACING)

		node = node_tree.nodes.new('ShaderNodeValue')
		node.location = x, y
		node.outputs[0].default_value = value.w
		node.label = alpha_node_name
		if alpha_node_name in group_node.inputs:
			node_tree.links.new(node.outputs[0], group_node.inputs[alpha_node_name])
		y -= int(node.height / 2 + SPACING)

	return blend_material


if __name__ == '__main__':
	import sys
	from ..prefab.material import load_material

	root_entity = load_material(sys.argv[-1], sys.argv[-2])
	create_material(root_entity, os.path.splitext(os.path.basename(sys.argv[-1]))[0], sys.argv[-2])
