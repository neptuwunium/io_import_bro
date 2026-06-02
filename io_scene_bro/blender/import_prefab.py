# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import logging
import math
import os.path

import bpy
from mathutils import Vector

from .import_material import create_material
from .import_mesh import import_mesh
from ..format.mesh import MeshFile
from ..prefab.loader import load_prefab
from ..prefab.material import load_material
from ..prefab.rttr import RTTRObject, get_vfs_path

LOG = logging.getLogger(f'{__name__}.import_prefab')

LOCAL_TRANSFORM_COMPONENT = 'engine::LocalTransformComponent'
WORLD_TRANSFORM_COMPONENT = 'engine::WorldTransformComponent'
DEVICE_COMPONENT = 'cw::DeviceComponent'
DEVICE_SLOTS_COMPONENT = 'cw::VehicleSlotMarkerComponent'
MODEL_COMPONENT = 'ModelComponent'
SKELETON_COMPONENT = 'SkeletonComponent'
SUN_LIGHT_COMPONENT = 'SunAndPlanetsComponent'
DIRECTIONAL_LIGHT_COMPONENT = 'DirectionalLightComponent'
SPOT_LIGHT_COMPONENT = 'SpotLightComponent'
POINT_LIGHT_COMPONENT = 'PointLightComponent'
TERRAIN_COMPONENT = 'TerrainComponent'


def create_light(component, data):
	if data.type == 'SUN':
		if isinstance(component.color, RTTRObject):
			data.color = (component.color.get('r', 0.0), component.color.get('g', 0.0), component.color.get('b', 0.0))
		if isinstance(component.intensity, float):
			data.energy = component.intensity
		if isinstance(component.azimuth, float):
			data.angle = component.azimuth
		return

	if isinstance(component.commonSettings, RTTRObject):
		common = component.commonSettings

		if isinstance(common.color, RTTRObject):
			data.color = (common.color.get('r', 0.0), common.color.get('g', 0.0), common.color.get('b', 0.0))

		if isinstance(common.intensity, float):
			if isinstance(component.radius, float):
				radius = component.radius
			elif isinstance(component.lightSize, float):
				radius = component.lightSize
			else:
				radius = 5

			fpi2 = 4 * (math.pi * math.pi)
			r2 = radius * radius
			flux = fpi2 * r2 * common.intensity
			data.energy = flux

	if isinstance(component.radius, float):
		data.shadow_soft_size = component.radius
	if data.type == 'SPOT' and isinstance(component.coneAngleDegrees, float):
		data.spot_size = math.radians(component.coneAngleDegrees)
	if data.type == 'AREA' and isinstance(component.lightSize, float):
		data.shape = 'SQUARE'
		data.size = component.lightSize


def create_prefab(prefab, game_path, slots=None, parent=None, cache=None):
	if not prefab: return None

	LOG.info('creating prefab "%s"', prefab.name)
	prefab_obj = bpy.data.objects.new(prefab.name, None)
	prefab_obj.parent = parent
	bpy.context.view_layer.active_layer_collection.collection.objects.link(prefab_obj)

	if isinstance(prefab.comps, RTTRObject):
		local_transform = prefab.comps.get(LOCAL_TRANSFORM_COMPONENT)
		world_transform = prefab.comps.get(WORLD_TRANSFORM_COMPONENT)
		device = prefab.comps.get(DEVICE_COMPONENT)
		device_slots = prefab.comps.get(DEVICE_SLOTS_COMPONENT)
		model = prefab.comps.get(MODEL_COMPONENT)
		sun = prefab.comps.get(SUN_LIGHT_COMPONENT)
		directional_light = prefab.comps.get(DIRECTIONAL_LIGHT_COMPONENT)
		spot_light = prefab.comps.get(SPOT_LIGHT_COMPONENT)
		point_light = prefab.comps.get(POINT_LIGHT_COMPONENT)
		_terrain = prefab.comps.get(TERRAIN_COMPONENT)  # todo

		if slots is not None and isinstance(device_slots, RTTRObject) \
				and isinstance(device_slots.slot, RTTRObject) \
				and isinstance(device_slots.slot.handle, str):
			slots[device_slots.slot.handle] = prefab_obj

		for light_comp, light_type in [
			(sun, 'SUN'),
			(directional_light, 'AREA'),
			(spot_light, 'SPOT'),
			(point_light, 'POINT')]:
			if isinstance(light_comp, RTTRObject):
				light_name = f'{prefab.name}::Light'
				light_data = bpy.data.lights.new(light_name, type=light_type)
				light_obj = bpy.data.objects.new(light_name, light_data)
				light_obj.parent = prefab_obj
				bpy.context.view_layer.active_layer_collection.collection.objects.link(light_obj)
				create_light(light_comp, light_data)

		if isinstance(local_transform, RTTRObject):
			if isinstance(local_transform.pos, RTTRObject):
				prefab_obj.location = Vector(
					(local_transform.pos.get("x", 0),
					 local_transform.pos.get("z", 0),
					 local_transform.pos.get("y", 0)))
			if isinstance(local_transform.scale, RTTRObject):
				prefab_obj.scale = Vector(
					(local_transform.scale.get("x", 1),
					 local_transform.scale.get("z", 1),
					 local_transform.scale.get("y", 1)))
			if isinstance(local_transform.rotation, RTTRObject):
				prefab_obj.rotation_mode = 'XYZ'
				prefab_obj.rotation_euler = Vector(
					(math.radians(local_transform.rotation.get("x", 0)),
					 math.radians(local_transform.rotation.get("z", 0)),
					 math.radians(-local_transform.rotation.get("y", 0))))

		if isinstance(world_transform, RTTRObject) and len(world_transform) > 0:
			assert False

		if isinstance(device, RTTRObject) and isinstance(device.statePrefabs, RTTRObject):
			for state_name, state in device.statePrefabs.items():
				if not (isinstance(state, RTTRObject) and isinstance(state.handle, str)): continue

				state_prefab_obj = bpy.data.objects.new(f'{prefab.name}::DeviceState::{state_name}', None)
				state_prefab_obj.parent = prefab_obj
				bpy.context.view_layer.active_layer_collection.collection.objects.link(state_prefab_obj)
				create_prefab(load_prefab(state.handle, game_path), game_path, slots, state_prefab_obj, cache)

		if isinstance(model, RTTRObject) and isinstance(model.meshes, list) and model.meshes:
			clutter_density = float(model.get("clutterDensity", 0.000))  # todo: procedural clutter

			if abs(clutter_density) < 0.001:
				mesh = model.meshes[0]

				if isinstance(mesh, RTTRObject) and isinstance(mesh.mesh, str):
					mesh_path = get_vfs_path(mesh.mesh, game_path)

					if os.path.exists(mesh_path):
						mesh_name = mesh.labelText or os.path.splitext(os.path.basename(mesh_path))[0]

						materials = {}
						cache_id = mesh.mesh
						if isinstance(mesh.materials, RTTRObject):
							for material_name, material_path in mesh.materials.items():
								if not isinstance(material_path, str): continue

								material = load_material(material_path, game_path, cache)
								materials[material_name] = create_material(material, material_name, game_path)
								if cache is not None:
									cache_id += f"[{material_name}::{material.hash_id}]"

						mesh_name = f'{prefab.name}::{mesh_name}'
						if cache is not None and cache_id in cache:
							blend_obj = bpy.data.objects.new(mesh_name, cache[cache_id])
							blend_obj.parent = prefab_obj
							bpy.context.view_layer.active_layer_collection.collection.objects.link(blend_obj)
						else:
							LOG.info('loading mesh "%s"', mesh.mesh)
							with open(mesh_path, 'rb') as f:
								mesh_obj = import_mesh(MeshFile(f), mesh_name, prefab_obj, materials)
								if cache is not None:
									cache[cache_id] = mesh_obj.data

	if prefab.children and isinstance(prefab.children, RTTRObject):
		for child in prefab.children.values():
			if not isinstance(child, RTTRObject): continue

			create_prefab(child, game_path, slots, prefab_obj, cache)

	return prefab_obj


if __name__ == '__main__':
	import sys
	import os.path

	root_entity = load_prefab(sys.argv[-1], sys.argv[-2])
	create_prefab(root_entity, sys.argv[-2])
