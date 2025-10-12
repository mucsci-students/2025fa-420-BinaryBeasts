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



    def load_config(self):
        path = main_view.load_config()
        self.model.config = load_config_from_file(CombinedConfig, path)



    def save_config(self, path: str):

        config = self.model.config
        courses = []
        mon = []
        tue = []
        wed = []
        thu = []
        fri = []
        classes = []
        faculty = []

        # Extract time slots per day with spacing where available
        for monday in config.time_slot_config.times.get("MON", []):
            mon.append({"start": monday.start, "spacing": getattr(monday, "spacing", None), "end": monday.end})
        for tuesday in config.time_slot_config.times.get("TUE", []):
            tue.append({"start": tuesday.start, "spacing": getattr(tuesday, "spacing", None), "end": tuesday.end})
        for wednesday in config.time_slot_config.times.get("WED", []):
            wed.append({"start": wednesday.start, "spacing": getattr(wednesday, "spacing", None), "end": wednesday.end})
        for thursday in config.time_slot_config.times.get("THU", []):
            thu.append({"start": thursday.start, "spacing": getattr(thursday, "spacing", None), "end": thursday.end})
        for friday in config.time_slot_config.times.get("FRI", []):
            fri.append({"start": friday.start, "spacing": getattr(friday, "spacing", None), "end": friday.end})

        # Extract classes info
        for clas in config.time_slot_config.classes:
            diction = {"credits": clas.credits, "meetings": self.get_met(clas)}
            if hasattr(clas, "disabled"):
                diction["disabled"] = clas.disabled
            classes.append(diction)

        #Extract faculty info with serialized times per day
        for member in config.config.faculty:
            faculty.append({
            "name": member.name,
            "maximum_credits": member.maximum_credits,
            "minimum_credits": member.minimum_credits,
            "unique_course_limit": member.unique_course_limit,
            "times": {
                "MON": self.serialize_time_ranges(member.times.get("MON", [])),
                "TUE": self.serialize_time_ranges(member.times.get("TUE", [])),
                "WED": self.serialize_time_ranges(member.times.get("WED", [])),
                "THU": self.serialize_time_ranges(member.times.get("THU", [])),
                "FRI": self.serialize_time_ranges(member.times.get("FRI", [])),
            }
        })

# Extract courses info
        for course in config.config.courses:
            courses.append({
        "course_id": course.course_id,
        "credits": course.credits,
        "room": course.room,
        "lab": course.lab,
        "conflicts": course.conflicts,
        "faculty": course.faculty
    })

# Final combined config dictionary
        final_config = {
    "config": {
        "rooms": config.config.rooms,
        "labs": config.config.labs,
        "courses": courses,
        "faculty": faculty
    },
    "time_slot_config": {
        "times": {
            "MON": mon,
            "TUE": tue,
            "WED": wed,
            "THU": thu,
            "FRI": fri,
        },
        "classes": classes
    },
    "limit": config.limit,
    "optimizer_flags": config.optimizer_flags
}
        with open("config.json", "w") as json_file:
            json.dump(final_config, json_file, indent=1)
# You can now json.dumps(final_config) safely without serialization errors



    def serialize_time_ranges(self, day_slots):
        result = []
        for slot in day_slots:
            item = {
                "start": slot.start,
                "end": slot.end,
            }
            # Only include spacing if the attribute exists
            if hasattr(slot, "spacing"):
                item["spacing"] = slot.spacing
            result.append(item)
        return result

    def get_met(self, met):
        meetings = []
        for meet in met.meetings:
            diction = {"day": meet.day, "duration": meet.duration}
            if hasattr(meet, "lab"):
                diction["lab"] = meet.lab
            meetings.append(diction)
        return meetings

    def load_config_gui(self, path):
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


