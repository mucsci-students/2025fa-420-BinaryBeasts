import scheduler.config
from scheduler.config import CombinedConfig
import main_model

def add_faculty_room_preference(faculty: str, room: str, preference: int):
    # assume combined_config is of type scheduler.config.CombinedConfig
    with main_model.config.edit_mode() as editable_combined_config:
        for f in editable_combined_config.config.faculty:
            if f.name == faculty:
                if room not in f.room_preferences:
                    raise RuntimeError(f"Faculty {faculty} already has room preference for {room}")
                with f.edit_mode() as editable_faculty:
                    editable_faculty.room_preferences[room] = preference
                return
        else:
            raise RuntimeError(f"Faculty {faculty} does not exist")
        



