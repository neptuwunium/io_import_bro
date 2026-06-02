# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from mathutils import Vector, Matrix

from .rttr import RTTRObject


class RTTRMaterialProperties:
	colors: dict[str, Vector]
	matrices: dict[str, Matrix]
	integers: dict[str, int]
	floats: dict[str, float]
	bools: dict[str, bool]
	textures: dict[str, str]


class RTTRMaterial:
	properties: RTTRMaterialProperties
	effect: str
	_hash_id: int

	def __init__(self, rttr: RTTRObject | None = None, base: RTTRMaterial | None = None): pass

	@property
	def hash_id(self) -> int: pass

	def _parse_properties(self, properties: list[RTTRObject]): pass


def load_material(material_path: str, base_path: str, cache: dict[str, RTTRMaterial] = None) -> RTTRMaterial: pass


def resolve_material(material: RTTRObject, base_path: str) -> RTTRMaterial: pass
