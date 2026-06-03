# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

import logging
import os
import time

from bpy.props import StringProperty, CollectionProperty
# noinspection PyUnresolvedReferences
from bpy.types import Operator, Context, Property, OperatorFileListElement
from bpy_extras.io_utils import ImportHelper

from .addon_preferences import AddonPreferences


# noinspection PyTypeHints
class _ImportTemplate(Operator, ImportHelper):
	bl_options = {'REGISTER', 'UNDO'}

	files: CollectionProperty(
		type=OperatorFileListElement,
		options={'HIDDEN'},
	)

	directory: StringProperty(get=lambda self: AddonPreferences.instance().game_data_path or '', options={'HIDDEN'})

	def load(self, path: str): pass

	@classmethod
	def poll(cls, _): return True

	def draw(self, _): pass

	def execute(self, context: Context):
		dirname = os.path.dirname(self.filepath)
		context.preferences.edit.use_global_undo = False
		start_time = time.perf_counter()
		for file in self.files:
			# noinspection PyTypeChecker
			self.load(os.path.join(dirname, file.name))
		context.view_layer.update()
		end_time = time.perf_counter()
		logging.info('took %.6f seconds', end_time - start_time)
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}


# noinspection PyTypeHints
class _VirtualImportTemplate(_ImportTemplate):
	@classmethod
	def poll(cls, _):
		game_path = AddonPreferences.instance().game_data_path
		return game_path and os.path.exists(game_path)


class _SpecOperator(Operator):
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def get_spec_path(cls): return ''

	@classmethod
	def get_spec_name(cls, name: str) -> str | None: return name

	@classmethod
	def get_spec(cls) -> list[tuple[str, str, str, str, int]]: return []

	def invoke(self, context: Context, _): return context.window_manager.invoke_props_dialog(self, width=200)

	def draw_extended(self, _): pass

	def draw(self, context: Context):
		self.layout.label(text=self.bl_header)
		self.layout.template_icon_view(self, 'spec_selector', show_labels=True)
		self.layout.label(text=self.get_spec_name(self.spec_selector))
		self.draw_extended(context)

	@classmethod
	def poll(cls, _):
		game_path = AddonPreferences.instance().game_data_path
		if not game_path:
			return False
		spec_path = os.path.join(game_path, cls.get_spec_path())
		return os.path.exists(spec_path)

	def execute_core(self, context: Context): pass

	def execute(self, context: Context):
		context.preferences.edit.use_global_undo = False
		start_time = time.perf_counter()
		self.execute_core(context)
		end_time = time.perf_counter()
		context.view_layer.update()
		logging.info('took %.6f seconds', end_time - start_time)
		context.preferences.edit.use_global_undo = True
		return {'FINISHED'}
