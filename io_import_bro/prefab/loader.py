# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import copy
import json
import os.path

from .rttr import RTTRObject


def unflatten_dict(flat_dict, delimiter='/'):
	unflattened = RTTRObject()
	for key, value in flat_dict.items():
		parts = key.split(delimiter)
		current = unflattened
		for part in parts[:-1]:
			if part not in current:
				current[part] = RTTRObject()
			current = current[part]
		current[parts[-1]] = value
	return unflattened


def deep_merge(target, source):
	for key, value in source.items():
		if isinstance(value, RTTRObject) and isinstance(target.get(key), RTTRObject):
			deep_merge(target[key], value)
		else:
			target[key] = copy.deepcopy(value)
	return target


def load_prefab_vfs(base_path, prefab_path):
	prefab_path = os.path.join(base_path, prefab_path[1:])
	if not os.path.exists(prefab_path):
		return RTTRObject()

	with open(prefab_path, 'r') as vfs_file:
		return json.load(vfs_file)


def load_prefab(entity_path, base_path, inherited_overrides=None, is_root=False):
	if not os.path.exists(entity_path):
		return RTTRObject()

	with open(entity_path, 'r') as entity_file:
		return resolve_prefab(json.load(entity_file, object_hook=lambda d: RTTRObject(d)).get('entities', RTTRObject()),
		                      base_path, inherited_overrides, is_root)


def resolve_prefab(entity, base_path, inherited_overrides=None, is_root=False):
	if inherited_overrides is None:
		inherited_overrides = RTTRObject()

	resolved_entity = RTTRObject()

	base_prefab = entity.get('prefab')
	if base_prefab and isinstance(base_prefab, str):
		base_prefab_path = os.path.join(base_path, base_prefab[1:])
		resolved_entity = load_prefab(base_prefab_path, base_path, inherited_overrides)

	active_overrides = copy.deepcopy(inherited_overrides)
	if 'overrides' in entity:
		for target_uuid, override_data in entity['overrides'].items():
			if target_uuid not in active_overrides:
				active_overrides[target_uuid] = copy.deepcopy(override_data)
			else:
				merged_override = copy.deepcopy(override_data)
				deep_merge(merged_override, active_overrides[target_uuid])
				active_overrides[target_uuid] = merged_override

	if 'comps' in entity:
		unpacked_comps = unflatten_dict(entity['comps'])
		resolved_entity.setdefault('comps', RTTRObject())
		deep_merge(resolved_entity['comps'], unpacked_comps)

	entity_uuid = entity.get('uuid')
	if entity_uuid and entity_uuid in active_overrides:
		override_data = active_overrides[entity_uuid]
		if 'comps' in override_data:
			unpacked_overrides = unflatten_dict(override_data['comps'])
			resolved_entity.setdefault('comps', RTTRObject())
			deep_merge(resolved_entity['comps'], unpacked_overrides)

	resolved_children = []
	for child in resolved_entity.get('children', []):
		resolved_children.append(resolve_prefab(child, base_path, active_overrides))

	for child in entity.get('children', []):
		resolved_children.append(resolve_prefab(child, base_path, active_overrides))

	if resolved_children:
		resolved_entity['children'] = resolved_children

	if is_root and active_overrides:
		resolved_entity['overrides'] = active_overrides

	for key, value in entity.items():
		if key not in ['comps', 'children', 'overrides', 'prefab']:
			resolved_entity[key] = copy.deepcopy(value)

	return resolved_entity
