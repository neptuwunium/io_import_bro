# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2
from typing import Optional

import bpy

from ..prefab.rttr import RTTRObject

LOCAL_TRANSFORM_COMPONENT = 'engine::LocalTransformComponent'
WORLD_TRANSFORM_COMPONENT = 'engine::WorldTransformComponent'
DEVICE_SLOTS_COMPONENT = 'cw::VehicleSlotMarkerComponent'
DEVICE_COMPONENT = 'cw::DeviceComponent'
MODEL_COMPONENT = 'ModelComponent'
SKELETON_COMPONENT = 'SkeletonComponent'
SUN_LIGHT_COMPONENT = 'SunAndPlanetsComponent'
DIRECTIONAL_LIGHT_COMPONENT = 'DirectionalLightComponent'
SPOT_LIGHT_COMPONENT = 'SpotLightComponent'
POINT_LIGHT_COMPONENT = 'PointLightComponent'
TERRAIN_COMPONENT = 'TerrainComponent'


def create_light(component: RTTRObject, data: bpy.types.Light) -> bool: pass


def create_prefab(prefab: Optional[RTTRObject], game_path: str,
                  slots: Optional[dict[str, bpy.types.Object]] = None,
                  parent: Optional[bpy.types.Object] = None,
                  cache: Optional[dict[str, bpy.types.Mesh]] = None) -> \
		Optional[bpy.types.Object]: pass
