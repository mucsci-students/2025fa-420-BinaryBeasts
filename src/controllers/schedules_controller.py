from src.views.cli import schedules_view
from src.models.room_day_model import schedule_to_location_blocks
import json


class generate_controller:
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

    def get_current_schedule_strings(self):
        """Return the current schedule as a list of CSV strings."""
        if not self.schedules or self.index < 0 or self.index >= len(self.schedules):
            return []
        schedule = self.schedules[self.index]
        strings = []
        for course in schedule:
            if course is None:
                continue
            try:
                if hasattr(course, 'as_csv'):
                    strings.append(course.as_csv())
                elif isinstance(course, str):
                    strings.append(course)
            except Exception:
                continue
        return strings

    def get_room_day_blocks(self):
        """Return room->List[TimeBlock] for the current schedule combining labs under rooms."""
        csv_list = self.get_current_schedule_strings()
        return schedule_to_location_blocks(csv_list)

    def _save_schedules_to_file(self, output_file: str, format_type: str):
        """Save generated schedules to file"""
        try:
            if format_type == "csv":
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("Schedule,Course,Day,Time,Duration,Room,Lab,Faculty\n")
                    for i, schedule in enumerate(self.schedules, 1):
                        for course in schedule:
                            csv_line = course.as_csv()
                            f.write(f"{i},{csv_line}\n")
            else:
                # JSON format
                json_schedules = []
                for i, schedule in enumerate(self.schedules, 1):
                    schedule_data = {
                        "schedule_id": i,
                        "courses": [course.as_csv() for course in schedule],
                    }
                    json_schedules.append(schedule_data)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(json_schedules, f, indent=2, ensure_ascii=False)

            print(f"✅ Schedules saved successfully to {output_file}")
        except Exception as e:
            print(f"❌ Error saving schedules: {e}")

        input("\nPress Enter to continue...")

    def save_schedules(self, output_file: str, format_type: str):
        """Save generated schedules to file"""
        try:
            if format_type == "csv":
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("Schedule,Course,Day,Time,Duration,Room,Lab,Faculty\n")
                    for i, schedule in enumerate(self.schedules, 1):
                        for course in schedule:
                            csv_line = course.as_csv()
                            f.write(f"{i},{csv_line}\n")
            else:
                # JSON format
                json_schedules = []
                for i, schedule in enumerate(self.schedules, 1):
                    schedule_data = {
                        "schedule_id": i,
                        "courses": [course.as_csv() for course in schedule],
                    }
                    json_schedules.append(schedule_data)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(json_schedules, f, indent=2, ensure_ascii=False)

            print(f"✅ Schedules saved successfully to {output_file}")
        except Exception as e:
            print(f"❌ Error saving schedules: {e}")

    def entry(self):
        total_schedules = len(self.schedules)

        # Display initial schedule
        if self.schedules:
            print("\n" + "=" * 25)
            print(f"Schedule {self.index + 1} of {total_schedules}")
            print("=" * 25)
            schedules_view.display_schedule(self.schedules[self.index])

        while True:
            user_input = schedules_view.schedule_navigation_view()

            if user_input == "1":
                # Next schedule
                if self.index < total_schedules - 1:
                    self.next_schedule()
                    print("\n" + "=" * 25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("=" * 25)
                    schedules_view.display_schedule(self.schedules[self.index])
                else:
                    print("Already at the last schedule.")
                    input("Press Enter to continue...")
            elif user_input == "2":
                # Previous schedule
                if self.index > 0:
                    self.previous_schedule()
                    print("\n" + "=" * 25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("=" * 25)
                    schedules_view.display_schedule(self.schedules[self.index])
                else:
                    print("Already at the first schedule.")
                    input("Press Enter to continue...")
            elif user_input == "3":
                # Go to specific schedule
                try:
                    schedule_num = int(
                        input(f"Enter schedule number (1-{total_schedules}): ").strip()
                    )
                    if 1 <= schedule_num <= total_schedules:
                        self.index = schedule_num - 1
                        print("\n" + "=" * 25)
                        print(f"Schedule {self.index + 1} of {total_schedules}")
                        print("=" * 25)
                        schedules_view.display_schedule(self.schedules[self.index])
                    else:
                        print(
                            f"Invalid schedule number. Please enter a number between 1 and {total_schedules}."
                        )
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    input("Press Enter to continue...")
            elif user_input == "4":
                # View by room/lab
                # Convert schedule objects to CSV strings
                current_schedule_strings = [
                    course.as_csv()
                    for course in self.schedules[self.index]
                    if course is not None
                ]
                schedules_view.display_schedule_by_room(current_schedule_strings)
                input("\nPress Enter to continue...")
            elif user_input == "5":
                # View by faculty
                # Convert schedule objects to CSV strings
                current_schedule_strings = [
                    course.as_csv()
                    for course in self.schedules[self.index]
                    if course is not None
                ]
                schedules_view.display_schedule_by_faculty(current_schedule_strings)
                input("\nPress Enter to continue...")
            elif user_input == "6":
                # Save schedules to file
                filename, format_type = schedules_view.save_schedules_view()
                self._save_schedules_to_file(filename, format_type)
            elif user_input == "7":
                # Export current schedule grouped by faculty (PDF)
                filename = schedules_view.save_faculty_pdf_view()
                # Build current schedule objects list
                schedule_objs = [c for c in self.schedules[self.index] if c is not None]
                try:
                    written = schedules_view.save_schedules_by_faculty_pdf(schedule_objs, filename)
                    if written:
                        print(f"✅ Faculty PDF written to: {written}")
                    else:
                        print("❌ Failed to write faculty PDF.")
                except Exception as e:
                    print(f"❌ Error exporting faculty PDF: {e}")
                input("\nPress Enter to continue...")
            elif user_input == "8":
                # Return to main menu
                break
            else:
                print("Invalid option. Please select 1-7.")
                input("Press Enter to continue...")


class raw_schedules_controller:
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
            print("\n" + "=" * 25)
            print(f"Schedule {self.index + 1} of {total_schedules}")
            print("=" * 25)
            schedules_view.display_schedule_basic(self.schedules[self.index])

        while True:
            user_input = schedules_view.schedule_navigation_view()

            if user_input == "1":
                # Next schedule
                if self.index < total_schedules - 1:
                    self.next_schedule()
                    print("\n" + "=" * 25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("=" * 25)
                    schedules_view.display_schedule_basic(self.schedules[self.index])
                else:
                    print("Already at the last schedule.")
                    input("Press Enter to continue...")
            elif user_input == "2":
                # Previous schedule
                if self.index > 0:
                    self.previous_schedule()
                    print("\n" + "=" * 25)
                    print(f"Schedule {self.index + 1} of {total_schedules}")
                    print("=" * 25)
                    schedules_view.display_schedule_basic(self.schedules[self.index])
                else:
                    print("Already at the first schedule.")
                    input("Press Enter to continue...")
            elif user_input == "3":
                # Go to specific schedule
                try:
                    schedule_num = int(
                        input(f"Enter schedule number (1-{total_schedules}): ").strip()
                    )
                    if 1 <= schedule_num <= total_schedules:
                        self.index = schedule_num - 1
                        print("\n" + "=" * 25)
                        print(f"Schedule {self.index + 1} of {total_schedules}")
                        print("=" * 25)
                        schedules_view.display_schedule_basic(
                            self.schedules[self.index]
                        )
                    else:
                        print(
                            f"Invalid schedule number. Please enter a number between 1 and {total_schedules}."
                        )
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
                # Save schedules to file
                filename, format_type = schedules_view.save_schedules_view()
                self._save_schedules_to_file(filename, format_type)
            elif user_input == "7":
                # Export current schedule grouped by faculty (PDF)
                filename = schedules_view.save_faculty_pdf_view()
                schedule_objs = [c for c in self.schedules[self.index] if c is not None]
                try:
                    written = schedules_view.save_schedules_by_faculty_pdf(schedule_objs, filename)
                    if written:
                        print(f"✅ Faculty PDF written to: {written}")
                    else:
                        print("❌ Failed to write faculty PDF.")
                except Exception as e:
                    print(f"❌ Error exporting faculty PDF: {e}")
                input("\nPress Enter to continue...")
            elif user_input == "8":
                # Return to main menu
                break
            else:
                print("Invalid option. Please select 1-7.")
                input("Press Enter to continue...")

    def _save_schedules_to_file(self, output_file: str, format_type: str):
        """Save raw schedules (from imported JSON) to file"""
        try:
            if format_type == "csv":
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("Schedule,Course\n")
                    for i, schedule in enumerate(self.schedules, 1):
                        for course_str in schedule:
                            f.write(f"{i},{course_str}\n")
            else:
                # JSON format
                json_schedules = []
                for i, schedule in enumerate(self.schedules, 1):
                    schedule_data = {
                        "schedule_id": i,
                        "courses": schedule,  # Already CSV strings
                    }
                    json_schedules.append(schedule_data)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(json_schedules, f, indent=2, ensure_ascii=False)

            print(f"✅ Schedules saved successfully to {output_file}")
        except Exception as e:
            print(f"❌ Error saving schedules: {e}")

            input("\nPress Enter to continue...")
            print(f"✅ Schedules saved successfully to {output_file}")
        except Exception as e:
            print(f"❌ Error saving schedules: {e}")

        input("\nPress Enter to continue...")
