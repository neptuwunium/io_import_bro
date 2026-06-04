# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from bpy.types import Operator, Panel

from ._import_template import _VirtualImportTemplate


class MaterialOperator(_VirtualImportTemplate):
	filter_glob: str


class MaterialPanelOperator(Panel): pass


class BindMaterialOperator(Operator): pass


class BindMaterialsOperator(Operator): pass


class BindAllMaterialsOperator(Operator): pass
