import src.models.main_model as main_model
import src.views.cli.main_view as main_view
#from src.controllers.course_controller import course_controller
from src.views.cli.course_view import course_view
#from src.controllers.lab_controller import lab_controller
from src.views.cli.lab_view import lab_view
#from src.controllers.faculty_controller import faculty_controller
from src.views.cli.faculty_view import faculty_view
#from src.controllers.room_controller import room_controller
from src.views.cli.room_view import room_view
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
        for schedule in scheduler.get_models():
            print("Schedule:")
            for course in schedule:
                print(f"{course.as_csv()}")
        """"
        lst = []
        for schedule in scheduler.get_models():
            lst.append(schedule)
            self.model.schedules.append(schedule)
        return lst
        """

    def save_config(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.config.__dict__, f, indent=4)

    def load_config(self):
        path = main_view.load_config()
        self.model.config = load_config_from_file(CombinedConfig, path)


    
    def load_schedules(self, path: str):
        pass

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
        #save configuration has been selected
        elif input_data == "5":
            num = main_view.generate_schedules()
            scheds = self.generate_schedules(num)
            controller = schedules_controller.generate_controller(scheds)
            controller.entry()
        #generate schedule has been selected
        elif input_data == "6":
            self.save_config("config.json")
        elif input_data == "7":
            print("Exiting program.")
            exit(0)