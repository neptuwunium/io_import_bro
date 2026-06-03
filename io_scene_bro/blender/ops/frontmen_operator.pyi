# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ._import_template import _SpecOperator
from ...prefab.rttr import RTTRObject


class FrontmenRegistryOperator(_SpecOperator):
	spec_selector: str

	_frontmen: list[tuple[str, str, str, str, int]] | None
	_frontmen_cache: str | None
	_frontmen_data: dict[str, RTTRObject] | None
