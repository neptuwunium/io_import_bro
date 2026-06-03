# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import bpy

from .. import __package__ as __base_package__
from ..format.skel import SkelFile

ARMATURE_DATA_KEY = f'{__base_package__}.skeleton_matrix'
ICOSPHERE_DEFAULT_NAME = f"{__base_package__}.skeleton_shape"


def _create_icosphere(name: str) -> bpy.types.Mesh: pass


def create_skeleton(skel: SkelFile, root: bpy.types.Object) -> bpy.types.Object: pass
