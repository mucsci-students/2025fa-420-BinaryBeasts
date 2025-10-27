import src.views.cli.main_view as main_view
from src.controllers.course_controller import CourseController
from src.models.course_model import CourseManager
from src.controllers.faculty_controller import FacultyController
from src.models.faculty_model import FacultyManager
from src.controllers.room_controller import RoomController
from src.models.room_model import RoomManager
from src.controllers.lab_controller import LabController
from src.models.lab_model import LabManager
from src.controllers import schedules_controller
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

    def manage_courses(self):
        """Manage courses using the course management system"""
        # Create CourseManager and load courses from CombinedConfig
        manager = CourseManager()

        # Extract courses from CombinedConfig
        courses_data = []
        for course in self.model.config.config.courses:
            courses_data.append({
                'course_id': course.course_id,
                'credits': course.credits,
                'room': course.room,
                'lab': course.lab,
                'faculty': course.faculty,
                'conflicts': course.conflicts
            })

        manager.load_courses(courses_data)

        # Create controller and run
        controller = CourseController(manager)
        from src.views.cli.course_view_cli import CourseView

        while True:
            CourseView.show_menu()
            choice = CourseView.get_menu_choice()

            if choice == '1':
                CourseView.display_courses(controller)
            elif choice == '2':
                CourseView.add_course_interactive(controller)
            elif choice == '3':
                CourseView.modify_course_interactive(controller)
            elif choice == '4':
                CourseView.delete_course_interactive(controller)
            elif choice == '5':
                # Save changes back to CombinedConfig
                if manager.save_with_combined_config(self.model.config):
                    print("✅ Configuration saved successfully")
                else:
                    print("❌ Failed to save configuration")
                return
            elif choice == '6':
                print("Exiting without saving changes.")
                return
            else:
                print("❌ Invalid choice. Please select 1-6.")

    def manage_faculty(self):
        """Manage faculty using the faculty management system"""
        # Create FacultyManager and load faculty from CombinedConfig
        manager = FacultyManager()

        # Extract faculty from CombinedConfig
        faculty_data = []
        for faculty in self.model.config.config.faculty:
            faculty_data.append({
                'name': faculty.name,
                'minimum_credits': faculty.minimum_credits,
                'maximum_credits': faculty.maximum_credits,
                'unique_course_limit': faculty.unique_course_limit,
                'times': faculty.times,
                'course_preferences': faculty.course_preferences,
                'room_preferences': faculty.room_preferences,
                'lab_preferences': faculty.lab_preferences
            })

        manager.load_faculty(faculty_data)

        # Create controller and run
        controller = FacultyController(manager)
        from src.views.cli.faculty_view import FacultyView

        # Get available resources for validation
        available_courses = set()
        for course in self.model.config.config.courses:
            available_courses.add(course.course_id)

        available_rooms = list(self.model.config.config.rooms)
        available_labs = list(self.model.config.config.labs)

        # Get course manager for impact analysis
        course_manager = CourseManager()
        courses_data = []
        for course in self.model.config.config.courses:
            courses_data.append({
                'course_id': course.course_id,
                'credits': course.credits,
                'room': course.room,
                'lab': course.lab,
                'faculty': course.faculty,
                'conflicts': course.conflicts
            })
        course_manager.load_courses(courses_data)
        courses_list = course_manager.get_all_courses()

        while True:
            FacultyView.show_menu()
            choice = FacultyView.get_menu_choice()

            if choice == '1':
                FacultyView.display_faculty(controller)
            elif choice == '2':
                FacultyView.add_faculty_interactive(controller, available_courses, available_rooms, available_labs)
            elif choice == '3':
                FacultyView.modify_faculty_interactive(controller, available_courses, available_rooms, available_labs)
            elif choice == '4':
                FacultyView.delete_faculty_interactive(controller, courses_list)
            elif choice == '5':
                # Save changes back to CombinedConfig
                if manager.save_with_combined_config(self.model.config):
                    print("✅ Configuration saved successfully")
                else:
                    print("❌ Failed to save configuration")
                return
            elif choice == '6':
                print("Exiting without saving changes.")
                return
            else:
                print("❌ Invalid choice. Please select 1-6.")

    def manage_rooms(self):
        """Manage rooms using the room management system"""
        # Create RoomManager and load rooms from CombinedConfig
        manager = RoomManager(self.model.config.config)

        # Create controller and run
        controller = RoomController(manager)
        from src.views.cli.room_view import RoomView

        # Get course and faculty data for impact analysis
        course_manager = CourseManager()
        courses_data = []
        for course in self.model.config.config.courses:
            courses_data.append({
                'course_id': course.course_id,
                'credits': course.credits,
                'room': course.room,
                'lab': course.lab,
                'faculty': course.faculty,
                'conflicts': course.conflicts
            })
        course_manager.load_courses(courses_data)
        courses_list = course_manager.get_all_courses()

        faculty_manager = FacultyManager()
        faculty_data = []
        for faculty in self.model.config.config.faculty:
            faculty_data.append({
                'name': faculty.name,
                'minimum_credits': faculty.minimum_credits,
                'maximum_credits': faculty.maximum_credits,
                'unique_course_limit': faculty.unique_course_limit,
                'times': faculty.times,
                'course_preferences': faculty.course_preferences,
                'room_preferences': faculty.room_preferences,
                'lab_preferences': faculty.lab_preferences
            })
        faculty_manager.load_faculty(faculty_data)
        faculty_list = faculty_manager.get_all_faculty()

        while True:
            RoomView.show_menu()
            choice = RoomView.get_menu_choice()

            if choice == '1':
                RoomView.display_rooms(controller)
            elif choice == '2':
                RoomView.add_room_interactive(controller)
            elif choice == '3':
                RoomView.modify_room_interactive(controller)
            elif choice == '4':
                RoomView.delete_room_interactive(controller, courses_list, faculty_list)
            elif choice == '5':
                # Save changes back to CombinedConfig
                self.model.config.config = manager.save_with_combined_config(self.model.config.config)
                print("✅ Configuration saved successfully")
                return
            elif choice == '6':
                print("Exiting without saving changes.")
                return
            else:
                print("❌ Invalid choice. Please select 1-6.")

    def manage_labs(self):
        """Manage labs using the lab management system"""
        # Create LabManager and load labs from CombinedConfig
        manager = LabManager(self.model.config)

        # Create controller and run
        controller = LabController(manager)
        from src.views.cli.lab_view_cli import LabView

        # Get course and faculty data for impact analysis
        course_manager = CourseManager()
        courses_data = []
        for course in self.model.config.config.courses:
            courses_data.append({
                'course_id': course.course_id,
                'credits': course.credits,
                'room': course.room,
                'lab': course.lab,
                'faculty': course.faculty,
                'conflicts': course.conflicts
            })
        course_manager.load_courses(courses_data)
        courses_list = course_manager.get_all_courses()

        faculty_manager = FacultyManager()
        faculty_data = []
        for faculty in self.model.config.config.faculty:
            faculty_data.append({
                'name': faculty.name,
                'minimum_credits': faculty.minimum_credits,
                'maximum_credits': faculty.maximum_credits,
                'unique_course_limit': faculty.unique_course_limit,
                'times': faculty.times,
                'course_preferences': faculty.course_preferences,
                'room_preferences': faculty.room_preferences,
                'lab_preferences': faculty.lab_preferences
            })
        faculty_manager.load_faculty(faculty_data)
        faculty_list = faculty_manager.get_all_faculty()

        while True:
            LabView.show_menu()
            choice = LabView.get_menu_choice()

            if choice == '1':
                LabView.display_labs(controller)
            elif choice == '2':
                LabView.add_lab_interactive(controller)
            elif choice == '3':
                LabView.modify_lab_interactive(controller)
            elif choice == '4':
                LabView.delete_lab_interactive(controller, courses_list, faculty_list)
            elif choice == '5':
                # Save changes back to CombinedConfig
                if controller.save_to_combined_config(self.model.config):
                    print("✅ Configuration saved successfully")
                else:
                    print("❌ Failed to save configuration")
                return
            elif choice == '6':
                print("Exiting without saving changes.")
                return
            else:
                print("❌ Invalid choice. Please select 1-6.")

    def process_input(self, input_data):
        #edit course has been selected
        if input_data == "1":
            self.manage_courses()
        #edit lab has been selected
        elif input_data == "2":
            self.manage_labs()
        #edit faculty has been selected
        elif input_data == "3":
            self.manage_faculty()
        #edit room has been selected
        elif input_data == "4":
            self.manage_rooms()
        #generate schedules has been selected
        elif input_data == "5":
            config_flags = main_view.generate_schedules()
            num = config_flags[0]
            self.model.config.optimizer_flags = config_flags[1]
            scheds = self.generate_schedules(num)
            controller = schedules_controller.generate_controller(scheds)
            controller.entry()
        #import schedules has been selected
        elif input_data == "6":
            self.load_schedules()
        #exit has been selected
        elif input_data == "7":
            print("Exiting program.")
            exit(0)
            
    def load_config_gui(self, path):
        self.model.config = load_config_from_file(CombinedConfig, path)




