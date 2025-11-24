# src/undo_manager.py

from copy import deepcopy


class SnapshotUndoManager:
    """
    Simple snapshot-based undo/redo manager.

    It stores copies of the manager's state.
    Each time something changes, we record a new snapshot.
    Undo = go back to an older snapshot.
    Redo = go forward to a newer snapshot.
    """

    def __init__(self, get_state, set_state):
        """
        get_state: function that returns current state (e.g. manager.snapshot_state())
        set_state: function that restores state (e.g. manager.restore_state(state))
        """
        self._get_state = get_state
        self._set_state = set_state

        # Start with initial state
        first_state = deepcopy(self._get_state())
        self._snapshots = [first_state]
        self._index = 0

    def record_change(self):
        """Call this AFTER a successful change to save a new snapshot."""
        current_state = deepcopy(self._get_state())

        # If we undid some steps and then make a new change,
        # drop all "future" snapshots.
        if self._index < len(self._snapshots) - 1:
            self._snapshots = self._snapshots[: self._index + 1]

        self._snapshots.append(current_state)
        self._index += 1

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return self._index < len(self._snapshots) - 1

    def undo(self) -> bool:
        """Go one step back. Returns False if nothing to undo."""
        if not self.can_undo():
            return False

        self._index -= 1
        state = self._snapshots[self._index]
        self._set_state(deepcopy(state))
        return True

    def redo(self) -> bool:
        """Go one step forward. Returns False if nothing to redo."""
        if not self.can_redo():
            return False

        self._index += 1
        state = self._snapshots[self._index]
        self._set_state(deepcopy(state))
        return True
