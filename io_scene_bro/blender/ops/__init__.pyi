# SPDX-FileCopyrightText: 2026 Neptuwunium
#
# SPDX-License-Identifier: EUPL-1.2

from bpy.types import ImagePreviewCollection

_bro_image_collection: ImagePreviewCollection | None


def _load_preview_image(name: str, asset_path: str) -> str: pass


def _init_preview_image(): pass


def _deinit_preview_image(): pass


def _reset_preview_image(_: str): pass
