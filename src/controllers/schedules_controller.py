import src.models.main_model as main_model
import src.views.cli.main_view as main_view
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig
from src.views.cli import schedules_view

class generate_controller():
    def __init__(self, schedules):
        self.schedules = schedules
        self.index = 0


    def next_schedule(self):
        self.index += 1
        if self.index >= len(self.schedules):
            self.index = 0

    def previous_schedule(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.schedules) - 1

    def save_schedules(self):
        pass

    def entry(self):
        total_schedules = len(self.schedules)

        # Display initial schedule
        if self.schedules:
            print("\n" + "="*25)
            print(f"Schedule {self.index + 1} of {total_schedules}")
            print("="*25)
            schedules_view.display_schedule(self.schedules[self.index])

        while True:
            user_input = schedules_view.schedule_navigation_view()

            if user_input == "1":
                # Next schedule
                if self.index < total_schedules - 1:
                    self.next_schedule()
                    print("\n" + "="*25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("="*25)
                    schedules_view.display_schedule(self.schedules[self.index])
                else:
                    print("Already at the last schedule.")
                    input("Press Enter to continue...")
            elif user_input == "2":
                # Previous schedule
                if self.index > 0:
                    self.previous_schedule()
                    print("\n" + "="*25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("="*25)
                    schedules_view.display_schedule(self.schedules[self.index])
                else:
                    print("Already at the first schedule.")
                    input("Press Enter to continue...")
            elif user_input == "3":
                # Go to specific schedule
                try:
                    schedule_num = int(input(f"Enter schedule number (1-{total_schedules}): ").strip())
                    if 1 <= schedule_num <= total_schedules:
                        self.index = schedule_num - 1
                        print("\n" + "="*25)
                        print(f"Schedule {self.index + 1} of {total_schedules}")
                        print("="*25)
                        schedules_view.display_schedule(self.schedules[self.index])
                    else:
                        print(f"Invalid schedule number. Please enter a number between 1 and {total_schedules}.")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    input("Press Enter to continue...")
            elif user_input == "4":
                # View by room/lab
                # Convert schedule objects to CSV strings
                current_schedule_strings = [course.as_csv() for course in self.schedules[self.index] if course is not None]
                schedules_view.display_schedule_by_room(current_schedule_strings)
                input("\nPress Enter to continue...")
            elif user_input == "5":
                # View by faculty
                # Convert schedule objects to CSV strings
                current_schedule_strings = [course.as_csv() for course in self.schedules[self.index] if course is not None]
                schedules_view.display_schedule_by_faculty(current_schedule_strings)
                input("\nPress Enter to continue...")
            elif user_input == "6":
                # Return to main menu
                break
            else:
                print("Invalid option. Please select 1-6.")
                input("Press Enter to continue...")


class raw_schedules_controller():
    """Controller for navigating imported/raw schedules (from JSON files)"""
    def __init__(self, schedules):
        self.schedules = schedules
        self.index = 0

    def next_schedule(self):
        self.index += 1
        if self.index >= len(self.schedules):
            self.index = 0

    def previous_schedule(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.schedules) - 1

    def entry(self):
        """Entry point for raw schedule navigation"""
        if not self.schedules:
            print("No schedules to display.")
            return

        total_schedules = len(self.schedules)

        # Display initial schedule
        if self.schedules:
            print("\n" + "="*25)
            print(f"Schedule {self.index + 1} of {total_schedules}")
            print("="*25)
            schedules_view.display_schedule_basic(self.schedules[self.index])

        while True:
            user_input = schedules_view.schedule_navigation_view()

            if user_input == "1":
                # Next schedule
                if self.index < total_schedules - 1:
                    self.next_schedule()
                    print("\n" + "="*25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("="*25)
                    schedules_view.display_schedule_basic(self.schedules[self.index])
                else:
                    print("Already at the last schedule.")
                    input("Press Enter to continue...")
            elif user_input == "2":
                # Previous schedule
                if self.index > 0:
                    self.previous_schedule()
                    print("\n" + "="*25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("="*25)
                    schedules_view.display_schedule_basic(self.schedules[self.index])
                else:
                    print("Already at the first schedule.")
                    input("Press Enter to continue...")
            elif user_input == "3":
                # Go to specific schedule
                try:
                    schedule_num = int(input(f"Enter schedule number (1-{total_schedules}): ").strip())
                    if 1 <= schedule_num <= total_schedules:
                        self.index = schedule_num - 1
                        print("\n" + "="*25)
                        print(f"Schedule {self.index + 1} of {total_schedules}")
                        print("="*25)
                        schedules_view.display_schedule_basic(self.schedules[self.index])
                    else:
                        print(f"Invalid schedule number. Please enter a number between 1 and {total_schedules}.")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    input("Press Enter to continue...")
            elif user_input == "4":
                # View by room/lab
                schedules_view.display_schedule_by_room(self.schedules[self.index])
                input("\nPress Enter to continue...")
            elif user_input == "5":
                # View by faculty
                schedules_view.display_schedule_by_faculty(self.schedules[self.index])
                input("\nPress Enter to continue...")
            elif user_input == "6":
                # Return to main menu
                break
            else:
                print("Invalid option. Please select 1-6.")
                input("Press Enter to continue...")
            