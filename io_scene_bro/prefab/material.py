# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import copy
import struct
from zlib import crc32

from mathutils import Vector, Matrix

from .rttr import RTTRObject, load_rttr


class RTTRMaterialProperties:
	def __init__(self):
		self.colors = {}
		self.matrices = {}
		self.integers = {}
		self.floats = {}
		self.bools = {}
		self.textures = {}


class RTTRMaterial:
	def __init__(self, rttr=None, base_rttr=None):
		if base_rttr:
			self.properties = copy.deepcopy(base_rttr.properties)
			self.effect = base_rttr.effect
		else:
			self.properties = RTTRMaterialProperties()
			self.effect = ''

		self._hash_id = 0

		if rttr:
			if '__type__' in rttr and rttr['__type__'] != 'engine::render::Material::Snapshot':
				return

			self.effect = rttr.get('effect', '') or self.effect
			self._parse_properties(rttr.get('properties', []))

			for texture in rttr.get('textures', []):
				if not texture['texture'] or not texture['name']: continue
				self.properties.textures[texture['name']] = texture['texture']

	@property
	def hash_id(self):
		if self._hash_id:
			return self._hash_id

		if not self.effect or not self.properties:
			return 0

		h = crc32(self.effect.encode(), 42)

		for name, value in self.properties.matrices.items():
			# noinspection PyTypeChecker
			value_bytes = struct.pack('=16f', *(tuple(value[0]) + tuple(value[1]) + tuple(value[2]) + tuple(value[3])))
			h = crc32(f'{name}='.encode(), h)
			h = crc32(value_bytes, h)

		for name, value in self.properties.colors.items():
			# noinspection PyTypeChecker
			value_bytes = struct.pack('=4f', *tuple(value))
			h = crc32(f'{name}='.encode(), h)
			h = crc32(value_bytes, h)

		for name, value in self.properties.bools.items():
			value_bytes = struct.pack('=?', value)
			h = crc32(f'{name}='.encode(), h)
			h = crc32(value_bytes, h)

		for name, value in self.properties.integers.items():
			value_bytes = struct.pack('=i', value)
			h = crc32(f'{name}='.encode(), h)
			h = crc32(value_bytes, h)

		for name, value in self.properties.floats.items():
			value_bytes = struct.pack('=f', value)
			h = crc32(f'{name}='.encode(), h)
			h = crc32(value_bytes, h)

		for name, value in self.properties.textures.items():
			h = crc32(f'{name}={value}'.encode(), h)

		self._hash_id = h
		return h

	def _parse_properties(self, properties):
		for prop in properties:
			if not prop['value'] or not prop['name']: continue
			value = prop['value']
			match value.get('__type__'):
				case 'engine::render::Material::Snapshot::PropertyArray':
					array_properties = value.get('properties', [])
					self._parse_properties(array_properties)
				case 'eastl::vector32<engine::render::Material::Snapshot::Property,eastl::allocator>':
					internal_properties = value.get('__value__', [])
					self._parse_properties(internal_properties)
				case 'math::matrix':
					m = value.get('M', [])
					m1 = m.get(0, {})
					m2 = m.get(1, {})
					m3 = m.get(2, {})
					m4 = m.get(3, {})
					self.properties.matrices[prop['name']] = Matrix(
						((m1.get('x', 1),
						  m1.get('y', 0),
						  m1.get('z', 0),
						  m1.get('w', 0)),
						 (m2.get('x', 0),
						  m2.get('y', 1),
						  m2.get('z', 0),
						  m2.get('w', 0)),
						 (m3.get('x', 0),
						  m3.get('y', 0),
						  m3.get('z', 1),
						  m3.get('w', 0)),
						 (m4.get('x', 0),
						  m4.get('y', 0),
						  m4.get('z', 0),
						  m4.get('w', 1))),
					)
				case 'math::vec4':
					self.properties.colors[prop['name']] = Vector(
						(value.get('x', 0),
						 value.get('y', 0),
						 value.get('z', 0),
						 value.get('w', 1))
					)
				case 'math::vec3':
					self.properties.colors[prop['name']] = Vector(
						(value.get('x', 0),
						 value.get('y', 0),
						 value.get('z', 0),
						 1)
					)
				case 'math::vec2':
					self.properties.colors[prop['name']] = Vector(
						(value.get('x', 0),
						 value.get('y', 0),
						 0,
						 1)
					)
				case 'bool':
					self.properties.bools[prop['name']] = bool(value.get('__value__', False))
				case 'float':
					self.properties.floats[prop['name']] = float(value.get('__value__', 0.0))
				case 'int32':
					self.properties.integers[prop['name']] = int(value.get('__value__', 0))
				case 'engine::InternedString':
					self.properties.textures[prop['name']] = str(value.get('__value__', ''))


def load_material(material_path, base_path, cache=None):
	if not material_path:
		return RTTRMaterial()

	if cache is not None and material_path in cache:
		return cache[material_path]

	material = resolve_material(load_rttr(material_path, base_path), base_path)
	if cache is not None:
		cache[material_path] = material
	return material


def resolve_material(material, base_path, cache=None):
	base_material_path = material.get('base')
	if isinstance(base_material_path, str):
		base_material = load_material(base_material_path, base_path, cache)
	else:
		base_material = RTTRMaterial()
	return RTTRMaterial(RTTRObject(material), base_material)


if __name__ == '__main__':
	import sys
	import json

	root_material = load_material(sys.argv[-1], sys.argv[-2])
	print(json.dumps(root_material, indent='\t'))
