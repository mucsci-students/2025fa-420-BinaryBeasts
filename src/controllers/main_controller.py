import src.models.main_model as main_model
import src.views.cli.main_view as main_view
#from src.controllers.course_controller import course_controller
#from src.views.cli.course_view import course_view
#from src.controllers.lab_controller import lab_controller
#from src.views.cli.lab_view import lab_view
#from src.controllers.faculty_controller import faculty_controller
#from src.views.cli.faculty_view import faculty_view
#from src.controllers.room_controller import room_controller
#from src.views.cli.room_view import room_view
from src.controllers import schedules_controller
from src.views.cli import schedules_view
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig
import json


class main_controller():
    def __init__(self, model):
        self.model = model

    def set_config(self, config):
        self.model.set_config(config)
    
    def set_num_schedules(self, num):
        self.model.set_num_schedules(num)

    def generate_schedules(self, limit: int):
        self.model.set_limit(limit)
        scheduler = Scheduler(self.model.config)
        lst = []
        for schedule in scheduler.get_models():
            lst.append(schedule)
            self.model.schedules.append(schedule)
        return lst

    def save_config(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.config.__dict__, f, indent=4)

    def load_config(self):
        path = main_view.load_config()
        self.model.config = load_config_from_file(CombinedConfig, path)


    
    def load_schedules(self):
        """Load schedules from JSON file and navigate them"""
        path = main_view.import_schedules()
        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Handle different JSON formats
            if isinstance(data, list):
                if data and isinstance(data[0], dict) and 'schedule_id' in data[0] and 'courses' in data[0]:
                    # New format: [{"schedule_id": 1, "courses": [...]}, ...]
                    schedules = [schedule_obj['courses'] for schedule_obj in data]
                elif data and isinstance(data[0], list):
                    # Multiple schedules (old format): [[schedule1], [schedule2], ...]
                    schedules = data
                else:
                    # Single schedule (old format): [course1, course2, ...]
                    schedules = [data]
            else:
                print("Invalid schedule format in JSON file.")
                return

            # Use raw_schedules_controller for navigation
            controller = schedules_controller.raw_schedules_controller(schedules)
            controller.entry()

        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{path}'.")
        except Exception as e:
            print(f"Error loading schedules: {e}")

    def save_schedules(self, path: str):
        with open(path, 'w') as f:
            f.write(str(self.schedules[self.current_schedule_index]))

    def process_input(self, input_data):
        #edit course has been selected
        if input_data == "1":
            course_controller(self.model.config)
            course_view()
        #edit lab has been selected
        elif input_data == "2":
            lab_controller(self.model.config)
            lab_view()
        #edit faculty has been selected
        elif input_data == "3":
            faculty_controller(self.model.config)
            faculty_view()
        #edit room has been selected
        elif input_data == "4":
            room_controller(self.model.config)
            room_view()
        #generate schedules has been selected
        elif input_data == "5":
            num = main_view.generate_schedules()
            scheds = self.generate_schedules(num)
            controller = schedules_controller.generate_controller(scheds)
            controller.entry()
        #import schedules has been selected
        elif input_data == "6":
            (self.load_schedules())
        #exit has been selected
        elif input_data == "7":
            print("Exiting program.")
            exit(0)


