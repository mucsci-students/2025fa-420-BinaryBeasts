from typing import Dict, Any, List

class FacultyController:
    """Mediator between Faculty GUI and scheduler.FacultyManager.

    This file mirrors the controller implementation the project expects;
    it's created as a proper Python module so it can be imported.
    """

    def __init__(self, config: Dict[str, Any]):
        # lazy import to avoid package import issues during module load
        from src.faculty import FacultyManager  
        self._manager = FacultyManager(config)

    @property
    def config(self) -> Dict[str, Any]:
        return self._manager.config

    def list_faculty(self) -> List[Dict[str, Any]]:
        return self._manager.get_faculty()

    def add_faculty(self, entry: Dict[str, Any]) -> bool:
        return self._manager.add_faculty(entry)

    def edit_faculty(self, old_name: str, entry: Dict[str, Any]) -> bool:
        return self._manager.edit_faculty(old_name, entry)

    def delete_faculty(self, name: str) -> None:
        return self._manager.delete_faculty(name)

    def build_faculty_entry(self, **kwargs) -> Dict[str, Any]:
        return self._manager.build_faculty_entry(**kwargs)

    def save_config(self, path: str) -> None:
        # keep save logic here: convert to CombinedConfig if available, write JSON
        import json
        from pathlib import Path
        try:
            from scheduler.config import CombinedConfig  # type: ignore
            combined = CombinedConfig.model_validate(self._manager.config)
            data = combined.model_dump()
        except Exception:
            data = self._manager.config
        p = Path(path)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
