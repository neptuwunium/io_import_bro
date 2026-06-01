# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import copy

from .rttr import RTTRObject, load_rttr


def _unflatten_dict(flat_dict, delimiter='/'):
	unflattened = RTTRObject()
	for key, value in flat_dict.items():
		parts = key.split(delimiter)
		current = unflattened
		for part in parts[:-1]:
			if part not in current:
				current[part] = RTTRObject()
			current = current[part]
		if isinstance(value, RTTRObject):
			current[parts[-1]] = _unflatten_dict(value)
		elif isinstance(value, list):
			current[parts[-1]] = [_unflatten_dict(v) if isinstance(value, RTTRObject) else v for v in value]
		else:
			current[parts[-1]] = value
	return unflattened


def _deep_merge(target, source):
	for key, value in source.items():
		if isinstance(value, RTTRObject) and isinstance(target.get(key), RTTRObject):
			_deep_merge(target[key], value)
		if isinstance(value, list) and isinstance(target.get(key), list):
			target[key] += value
		else:
			target[key] = copy.deepcopy(value)
	return target


def load_prefab(prefab_path, base_path, inherited_overrides=None, prefab_cache=None):
	if not prefab_path:
		return RTTRObject()

	if prefab_path.endswith('.prefab'):
		if not prefab_path.endswith(".client.prefab"):
			prefab_path = prefab_path[:-len(".prefab")] + ".client.prefab"
	elif prefab_path.endswith('.world'):
		if not prefab_path.endswith(".client.world"):
			prefab_path = prefab_path[:-len(".world")] + ".client.world"
	else:
		return RTTRObject()

	if prefab_cache is None:
		prefab_cache = {}

	if prefab_path in prefab_cache:
		return copy.deepcopy(prefab_cache[prefab_path])

	print("loading", prefab_path)
	entities = load_rttr(prefab_path, base_path).entities
	if not isinstance(entities, RTTRObject):
		return RTTRObject()

	prefab = resolve_prefab(entities, base_path, inherited_overrides, prefab_cache)
	prefab_cache[prefab_path] = prefab
	return prefab


def resolve_prefab(entity, base_path, inherited_overrides=None, prefab_cache=None):
	if not entity:
		return RTTRObject()

	if inherited_overrides is None:
		inherited_overrides = RTTRObject()

	resolved_entity = RTTRObject()

	base_prefab = entity.get('prefab')
	if base_prefab and isinstance(base_prefab, str):
		resolved_entity = load_prefab(base_prefab, base_path, inherited_overrides, prefab_cache)

	active_overrides = copy.deepcopy(inherited_overrides)
	if 'overrides' in entity:
		for target_uuid, override_data in entity['overrides'].items():
			if target_uuid not in active_overrides:
				active_overrides[target_uuid] = copy.deepcopy(override_data)
			else:
				merged_override = copy.deepcopy(override_data)
				_deep_merge(merged_override, active_overrides[target_uuid])
				active_overrides[target_uuid] = merged_override

	if 'comps' in entity:
		unpacked_comps = _unflatten_dict(entity['comps'])
		resolved_entity.setdefault('comps', RTTRObject())
		_deep_merge(resolved_entity['comps'], unpacked_comps)

	entity_uuid = entity.get('uuid')
	resolved_children = []
	override_data = {}
	if entity_uuid and entity_uuid in active_overrides:
		override_data = active_overrides[entity_uuid]
		if 'comps' in override_data:
			unpacked_overrides = _unflatten_dict(override_data['comps'])
			resolved_entity.setdefault('comps', RTTRObject())
			_deep_merge(resolved_entity['comps'], unpacked_overrides)

	for child in resolved_entity.get('children', []):
		resolved_children.append(resolve_prefab(child, base_path, active_overrides, prefab_cache))

	for child in entity.get('children', []):
		resolved_children.append(resolve_prefab(child, base_path, active_overrides, prefab_cache))

	for child in override_data.get('children', []):
		resolved_children.append(resolve_prefab(child, base_path, active_overrides, prefab_cache))

	if resolved_children:
		resolved_entity['children'] = resolved_children

	for key, value in entity.items():
		if key not in ['comps', 'children', 'overrides', 'prefab']:
			resolved_entity[key] = copy.deepcopy(value)

	for key, value in override_data.items():
		if key not in ['comps', 'children', 'overrides', 'prefab']:
			resolved_entity[key] = copy.deepcopy(value)

	return resolved_entity


__all__ = ['load_prefab', 'resolve_prefab']
