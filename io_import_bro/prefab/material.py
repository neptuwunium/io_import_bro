# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import copy

from .rttr import RTTRObject, load_rttr


class RTTRMaterial:
	def __init__(self, rttr, base_rttr=None):
		if base_rttr:
			self.properties = copy.deepcopy(base_rttr.properties)
			self.textures = copy.deepcopy(base_rttr.textures)
			self.effect = base_rttr.effect
		else:
			self.properties = {}
			self.textures = {}
			self.effect = ''

		if rttr:
			self.effect = rttr.get('effect', '') or self.effect
			for prop in rttr.get('properties', []):
				if not prop["value"] or not prop["name"]: continue
				self.properties[prop["name"]] = prop["value"]

			for texture in rttr.get('textures', []):
				if not texture["texture"] or not texture["name"]: continue
				self.textures[texture["name"]] = texture["texture"]


def load_material(material_path, base_path):
	if not (material_path and material_path.endswith('.material')):
		return RTTRMaterial()

	return resolve_material(load_rttr(material_path, base_path), base_path)


def resolve_material(material, base_path):
	base_material_path = material.get('base')
	if isinstance(base_material_path, str):
		base_material = load_material(base_material_path, base_path)
	else:
		base_material = RTTRMaterial()
	return RTTRMaterial(RTTRObject(material), base_material)
