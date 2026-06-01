# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from .rttr import RTTRObject


class RTTRMaterial:
	properties: dict[str, RTTRObject]
	textures: dict[str, str]
	effect: str

	def __init__(self, rttr: RTTRObject | None = None, base: RTTRMaterial | None = None): pass


def load_material(material_path: str, base_path: str) -> RTTRMaterial: pass


def resolve_material(material: RTTRObject, base_path: str) -> RTTRMaterial: pass
