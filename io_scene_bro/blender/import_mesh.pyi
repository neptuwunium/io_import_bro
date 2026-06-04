# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Optional

import bpy

from ..format.mesh import MeshFile


def create_mesh(mesh: MeshFile, name: str,
                parent: Optional[bpy.types.Object] = None,
                materials: Optional[dict[str, bpy.types.Material]] = None) -> \
		bpy.types.Object: pass
