"""
Shim module to provide RoomGUI at src.views.gui.roomGui.

main_gui imports this module as `import src.views.gui.roomGui as roomGui`
and then calls `roomGui.RoomGUI(self.config)`.

The actual RoomGUI implementation lives in `src/roomGUI.py` alongside
RoomManager. This shim re-exports a RoomGUI class that ensures the config
is a plain dict before delegating to the real implementation.
"""

from typing import Optional, Any

# Import the real RoomGUI implementation
try:
	from src.roomGUI import RoomGUI as _BaseRoomGUI  # type: ignore
except Exception as _e:
	# As a fallback when running from the src directory directly
	from roomGUI import RoomGUI as _BaseRoomGUI  # type: ignore


class RoomGUI(_BaseRoomGUI):
	"""Compatibility wrapper for RoomGUI.

	Accepts either a Pydantic CombinedConfig model or a dict. If a model is
	provided, it will be converted to a dict via `model_dump()` before passing
	it to the base implementation, which expects a plain dict with a top-level
	'config' key.
	"""

	def __init__(self, config: Any, loaded_path: Optional[str] = None, parent=None) -> None:
		# Convert Pydantic model to dict if needed (CombinedConfig has model_dump)
		try:
			if hasattr(config, "model_dump"):
				config = config.model_dump()
		except Exception:
			# Best-effort: pass through if conversion fails
			pass

		super().__init__(config, loaded_path=loaded_path, parent=parent)


__all__ = ["RoomGUI"]

