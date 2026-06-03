# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from ._import_template import _SpecOperator
from ...prefab.rttr import RTTRObject


class VehicleRegistryOperator(_SpecOperator):
	spec_selector: str

	_vehicles: list[tuple[str, str, str, str, int]] | None
	_vehicles_cache: str | None
	_vehicle_data: dict[str, RTTRObject] | None
