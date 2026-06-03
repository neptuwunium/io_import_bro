# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from .rttr import RTTRObject, load_rttr

_IGNORE_FIELDS = ['comps', 'children', 'overrides', 'prefab']


def _clone(obj):
	if isinstance(obj, RTTRObject):
		res = RTTRObject()
		for k, v in obj.items():
			res[k] = _clone(v)
		return res
	elif isinstance(obj, list):
		return [_clone(v) for v in obj]
	return obj


def _unflatten_dict(flat_dict, delimiter='/'):
	unflattened = RTTRObject()
	for key, value in flat_dict.items():
		parts = key.split(delimiter)
		current = unflattened
		last = parts.pop()
		for part in parts:
			if part not in current:
				current[part] = RTTRObject()
			current = current[part]
		if isinstance(value, RTTRObject):
			current[last] = _unflatten_dict(value, delimiter)
		elif isinstance(value, list) and value and isinstance(value[0], RTTRObject):
			current[last] = [_unflatten_dict(item, delimiter) for item in value]
		else:
			current[last] = value
	return unflattened


def _deep_merge(target, source):
	if isinstance(target, list) and isinstance(source, RTTRObject):
		for key, value in source.items():
			idx = int(key)
			if idx < 0:
				continue
			elif idx < len(target):
				if isinstance(value, RTTRObject) and isinstance(target[idx], (RTTRObject, list)):
					_deep_merge(target[idx], value)
				else:
					target[idx] = _clone(value)
			else:
				target.extend([RTTRObject() for _ in range(idx - len(target) + 1)])
				target[idx] = _clone(value)
	elif isinstance(target, RTTRObject) and isinstance(source, RTTRObject):
		for key, value in source.items():
			target_val = target.get(key)
			if isinstance(value, RTTRObject) and isinstance(target_val, (RTTRObject, list)):
				_deep_merge(target_val, value)
			else:
				target[key] = _clone(value)
	return target


def load_prefab(prefab_path, base_path, inherited_overrides=None, prefab_cache=None):
	if not prefab_path:
		return RTTRObject()

	if prefab_path.endswith('.prefab'):
		if not prefab_path.endswith('.client.prefab'):
			prefab_path = prefab_path[:-len('.prefab')] + '.client.prefab'
	elif prefab_path.endswith('.world'):
		if not prefab_path.endswith('.client.world'):
			prefab_path = prefab_path[:-len('.world')] + '.client.world'

	if prefab_cache is None:
		prefab_cache = {}

	if prefab_path not in prefab_cache:
		rttr = load_rttr(prefab_path, base_path)
		if '__type__' in rttr and rttr['__type__'] != 'engine::io::SceneResource::RawData':
			return RTTRObject()

		entities = rttr.entities
		if not isinstance(entities, RTTRObject):
			return RTTRObject()

		prefab_cache[prefab_path] = resolve_prefab(entities, base_path, inherited_overrides, prefab_cache)

	return _clone(prefab_cache[prefab_path])


def _map_children(children):
	if not isinstance(children, list):
		return children

	return RTTRObject({child.uuid: child for child in children})


def resolve_prefab(entity, base_path, inherited_overrides=None, prefab_cache=None):
	if not entity:
		return RTTRObject()

	active_overrides = RTTRObject()
	if inherited_overrides:
		for k, v in inherited_overrides.items():
			active_overrides[k] = v

	resolved_entity = RTTRObject()

	base_prefab = entity.get('prefab')
	if base_prefab and isinstance(base_prefab, str):
		resolved_entity = load_prefab(base_prefab, base_path, active_overrides, prefab_cache)

	if 'overrides' in entity:
		for target_uuid, override_data in entity['overrides'].items():
			if target_uuid not in active_overrides:
				active_overrides[target_uuid] = _clone(override_data)
			else:
				if active_overrides[target_uuid] is (inherited_overrides and inherited_overrides.get(target_uuid)):
					active_overrides[target_uuid] = _clone(active_overrides[target_uuid])
				_deep_merge(active_overrides[target_uuid], override_data)

	if 'comps' in entity:
		unpacked_comps = _unflatten_dict(entity['comps'])
		resolved_entity.setdefault('comps', RTTRObject())
		_deep_merge(resolved_entity['comps'], unpacked_comps)

	entity_uuid = entity.get('uuid')
	override_data = {}
	if entity_uuid and entity_uuid != '00000000-0000-0000-0000-000000000000' and entity_uuid in active_overrides:
		override_data = active_overrides[entity_uuid]
		if 'comps' in override_data:
			unpacked_overrides = _unflatten_dict(override_data['comps'])
			resolved_entity.setdefault('comps', RTTRObject())
			_deep_merge(resolved_entity['comps'], unpacked_overrides)

	raw_children = _map_children(resolved_entity.get('children', []))
	_deep_merge(raw_children, _map_children(entity.get('children', [])))
	_deep_merge(raw_children, _map_children(override_data.get('children', [])))

	resolved_children = RTTRObject()
	for key, child in raw_children.items():
		resolved_children[key] = resolve_prefab(child, base_path, active_overrides, prefab_cache)

	if resolved_children:
		resolved_entity['children'] = resolved_children

	for key, value in entity.items():
		if key not in _IGNORE_FIELDS:
			resolved_entity[key] = _clone(value)

	for key, value in override_data.items():
		if key not in _IGNORE_FIELDS:
			resolved_entity[key] = _clone(value)

	return resolved_entity


__all__ = ['load_prefab', 'resolve_prefab']

if __name__ == '__main__':
	import sys
	import json

	root_entity = load_prefab(sys.argv[-1], sys.argv[-2])
	print(json.dumps(root_entity, indent='\t'))
