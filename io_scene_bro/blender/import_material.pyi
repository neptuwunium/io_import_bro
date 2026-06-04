# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Optional

import bpy

from .. import __package__ as __base_package__
from ..prefab.material import RTTRMaterial

MATERIAL_DATA_KEY = f'{__base_package__}.material_id'
NODE_DATA_KEY = f'{__base_package__}.property_target'


def bind_material(material: bpy.types.Material): pass


def bind_materials(objs: Optional[list[bpy.types.Object]] = None): pass


def load_image(texture_path: str, root_path: str) -> Optional[bpy.types.Image]: pass


def create_material(material: RTTRMaterial, name: str, root_path: str) -> bpy.types.Material: pass
