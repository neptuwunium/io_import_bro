# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from typing import Optional

from .rttr import RTTRObject


def _unflatten_dict(flat_dict: RTTRObject, delimiter='/') -> RTTRObject: pass


def _deep_merge(target: RTTRObject, source: RTTRObject) -> RTTRObject: pass


def load_prefab(prefab_path: str, base_path: str,
                inherited_overrides: Optional[RTTRObject] = None,
                prefab_cache: Optional[dict[str, RTTRObject]] = None) -> RTTRObject: pass


def resolve_prefab(prefab: Optional[RTTRObject], base_path: str,
                   inherited_overrides: Optional[RTTRObject] = None,
                   prefab_cache: dict[str, RTTRObject] = None) -> RTTRObject: pass
