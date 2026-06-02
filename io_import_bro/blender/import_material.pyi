# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Optional

import bpy

from ..prefab.material import RTTRMaterial

def load_image(texture_path: str, root_path: str) -> Optional[bpy.types.Image]: pass
def create_material(material: RTTRMaterial, name: str, root_path: str) -> bpy.types.Material: pass
