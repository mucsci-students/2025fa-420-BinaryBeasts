import src.models.main_model as main_model
import src.views.cli.main_view as main_view
from src.controllers.course_controller import CourseController
from src.models.course_model import CourseManager
from src.controllers.faculty_controller import FacultyController
from src.models.faculty_model import FacultyManager
#from src.controllers.lab_controller import lab_controller
#from src.views.cli.lab_view import lab_view
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

    def process_input(self, input_data):
        #edit course has been selected
        if input_data == "1":
            self.manage_courses()
        #edit lab has been selected
        elif input_data == "2":
            print("Lab management not yet implemented.")
            input("Press Enter to continue...")
        #edit faculty has been selected
        elif input_data == "3":
            self.manage_faculty()
        #edit room has been selected
        elif input_data == "4":
            print("Room management not yet implemented.")
            input("Press Enter to continue...")
        #generate schedules has been selected
        elif input_data == "5":
            num = main_view.generate_schedules()
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


