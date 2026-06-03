# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

# noinspection PyUnresolvedReferences
from bpy.types import Operator, Context, OperatorFileListElement
from bpy_extras.io_utils import ImportHelper


class _ImportTemplate(Operator, ImportHelper):
	files: list[OperatorFileListElement]
	directory: str

	def load(self, path: str): pass


class _VirtualImportTemplate(_ImportTemplate): pass


class _SpecOperator(Operator):
	@classmethod
	def get_spec_path(cls) -> str: pass

	@classmethod
	def get_spec_name(cls, name: str) -> str | None: pass

	@classmethod
	def get_spec(cls) -> list[tuple[str, str, str, str, int]]: pass

	def draw_extended(self, context: Context): pass

	def execute_core(self, context: Context): pass
