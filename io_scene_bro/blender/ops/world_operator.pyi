# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ._import_template import _SpecOperator


class WorldRegistryOperator(_SpecOperator):
	spec_selector: str

	_worlds: list[tuple[str, str, str, str, int]] | None
	_world_cache: str | None
	_world_names: dict[str, tuple[str, str]] | None
