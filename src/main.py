#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig
from courses import CourseManager
from room import RoomManager
from lab_manager import LabManager
from BinaryBeastsProjects.src.faculty import FacultyManager
from src.views.cli import schedules_view, main_view
# from views.gui.main_gui import MainGUI
from PyQt5.QtWidgets import (
    QApplication
)


def load_config(config_file: str) -> dict:
    """
    Load configuration from the specified config file.
    Args: config_file: Path to the configuration file
    Returns: Dictionary containing configuration data
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)

        if 'config' in data:
            return data['config']
        else:
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_file}")
    except Exception as e:
        raise Exception(f"Error loading config file {config_file}: {e}")

def load_time_slot_config(time_slot_config: str) -> dict:
    """
    Load time slot configuration from the specified file.
    Args: time_slot_config: Path to the time slot configuration file
    Returns: Dictionary containing time slot configuration
    """
    try:
        with open(time_slot_config, 'r') as f:
            data = json.load(f)

        if 'time_slot_config' in data:
            return data['time_slot_config']
        else:
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Time slot config file not found: {time_slot_config}")
    except Exception as e:
        raise Exception(f"Error loading time slot config file {time_slot_config}: {e}")
# this is more a quality of life thing its convenient
def print_config_summary(config: dict, time_slots: dict) -> None:
    """
    Print a readable summary of the configuration.
    Args: config: Configuration dictionary
          time_slots: Time slot configuration dictionary
    """
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    # Rooms
    rooms = config.get('rooms', [])
    print(f"\n📍 ROOMS ({len(rooms)} available):")
    for room in rooms:
        print(f"   • {room}")
    # Labs
    labs = config.get('labs', [])
    print(f"\n🔬 LABS ({len(labs)} available):")
    for lab in labs:
        print(f"   • {lab}")
    # Courses
    courses = config.get('courses', [])
    print(f"\n📚 COURSES ({len(courses)} total):")
    course_by_id = {}
    for course in courses:
        course_id = course.get('course_id', 'Unknown')
        if course_id not in course_by_id:
            course_by_id[course_id] = []
        course_by_id[course_id].append(course)

    for course_id, instances in course_by_id.items():
        print(f"   📖 {course_id} ({len(instances)} instance(s))")
        first_instance = instances[0]
        print(f"      Credits: {first_instance.get('credits', 'N/A')}")
        print(f"      Rooms: {', '.join(first_instance.get('room', [])) or 'None'}")
        print(f"      Labs: {', '.join(first_instance.get('lab', [])) or 'None'}")
        print(f"      Faculty: {', '.join(first_instance.get('faculty', [])) or 'Unassigned'}")
        conflicts = first_instance.get('conflicts', [])
        print(f"      Conflicts: {', '.join(conflicts) or 'None'}")
        if len(instances) > 1:
            print(f"      (Note: {len(instances)} different instances of this course)")
    
    # Faculty
    faculty = config.get('faculty', [])
    print(f"\n👥 FACULTY ({len(faculty)} members):")
    for member in faculty:
        name = member.get('name', 'Unknown')
        min_credits = member.get('minimum_credits', 0)
        max_credits = member.get('maximum_credits', 0)
        unique_limit = member.get('unique_course_limit', 'N/A')
        print(f"   👤 {name}")
        print(f"      Credit range: {min_credits}-{max_credits}")
        print(f"      Max unique courses: {unique_limit}")
        
        # Show availability
        times = member.get('times', {})
        available_days = [day for day, slots in times.items() if slots]
        print(f"      Available days: {', '.join(available_days) or 'None'}")
        
        # Show preferences
        course_prefs = member.get('course_preferences', {})
        if course_prefs:
            top_courses = sorted(course_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      Preferred courses: {', '.join([f'{c}({p})' for c, p in top_courses])}")
        
        room_prefs = member.get('room_preferences', {})
        if room_prefs:
            top_rooms = sorted(room_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      Preferred rooms: {', '.join([f'{r}({p})' for r, p in top_rooms])}")
        
        lab_prefs = member.get('lab_preferences', {})
        if lab_prefs:
            top_labs = sorted(lab_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      Preferred labs: {', '.join([f'{l}({p})' for l, p in top_labs])}")
    
    # Time slots summary
    print(f"\n🕒 TIME SLOT CONFIGURATION:")
    times = time_slots.get('times', {})
    for day, slots in times.items():
        if slots:
            print(f"   {day}: {len(slots)} time slot(s)")
            for slot in slots:
                start = slot.get('start', 'N/A')
                end = slot.get('end', 'N/A')
                spacing = slot.get('spacing', 'N/A')
                print(f"      {start}-{end} (spacing: {spacing}min)")
    
    # Class patterns
    classes = time_slots.get('classes', [])
    print(f"\n📅 CLASS PATTERNS ({len(classes)} patterns):")
    for i, pattern in enumerate(classes):
        credits = pattern.get('credits', 'N/A')
        meetings = pattern.get('meetings', [])
        disabled = pattern.get('disabled', False)
        status = " (DISABLED)" if disabled else ""
        print(f"   Pattern {i+1}: {credits} credits{status}")
        for meeting in meetings:
            day = meeting.get('day', 'N/A')
            duration = meeting.get('duration', 'N/A')
            lab = " (LAB)" if meeting.get('lab', False) else ""
            print(f"      {day}: {duration}min{lab}")
    
    print("="*60)

def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """
    Validate that a file path is accessible.
    Args:
        file_path: Path to validate
        must_exist: Whether the file must already exist
    Returns:
        Validated Path object
    Raises:
        FileNotFoundError: If file must exist but doesn't
        PermissionError: If file is not accessible
    """
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    path = Path(file_path)
    
    if must_exist:
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        if not path.stat().st_mode & 0o444:  # Check read permission
            raise PermissionError(f"No read permission for file: {file_path}")
    else:
        # For output files, check if parent directory exists and is writable
        parent = path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise PermissionError(f"Cannot create directory {parent}: {e}")
        if not parent.stat().st_mode & 0o222:  # Check write permission
            raise PermissionError(f"No write permission for directory: {parent}")
    
    return path

def save_config_to_file(config: dict, time_slots: dict, config_file: str) -> None:
    """
    Save the modified configuration back to the JSON file.
    Args:
        config: Configuration dictionary
        time_slots: Time slot configuration dictionary
        config_file: Path to save the configuration
    """
    try:
        # Remake the full configuration structure
        full_config = {
            "config": config,
            "time_slot_config": time_slots
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration saved successfully to {config_file}")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")

def show_interface_selection() -> str:
    """Display interface selection menu and get user choice."""
    print("\n" + "="*50)
    print("SCHEDULER APPLICATION")
    print("="*50)
    print("Choose your interface:")
    print("1. 💻 CLI (Command Line Interface)")
    print("2. 🖥️ GUI (Graphical User Interface)")
    print("3. 🚪 Exit")
    print("="*50)
    
    return input("Select an option (1-3): ").strip()

def show_main_menu() -> str:
    """Display main menu and get user choice."""
    print("\n" + "="*50)
    print("SCHEDULER CLI - MAIN MENU")
    print("="*50)
    print("1. 🗂️ Course Management")
    print("2. 🏢 Room Management")
    print("3. 🔬 Lab Management")
    print("4. 👥 Faculty Management")
    print("5. 📅 Schedule Management (Generate/Import/Export)")
    print("6. 🚪 Exit")
    print("="*50)

    return input("Select an option (1-6): ").strip()

def get_user_input():
    """
    Get user input for all required parameters.
    Returns:
        Dictionary containing user inputs
    """
    print("Scheduler CLI Application")
    print("Generate and optimize schedules based on configuration files.")
    print()
    # Get required inputs
    print("📁 CONFIGURATION FILE:")
    print("   Example: example.json")
    print("   Example: /path/to/config.json")
    print("   Example: ./configs/schedule_config.json")
    config_file = input("Enter path to configuration file (JSON): ").strip()
    # Check if user wants to use the same file for time slots
    print("\n🕒 TIME SLOT CONFIGURATION:")
    print("   If your JSON file contains both 'config' and 'time_slot_config' sections,")
    print("   you can use the same file for both.")
    use_same_file = input("Use the same file for time slot configuration? (y/n, default: y): ").strip().lower()
    if not use_same_file or use_same_file in ['y', 'yes', 'true', '1']:
        time_slots_file = config_file
    else:
        print("   Example: timeslots.json")
        print("   Example: /path/to/time_config.json")
        time_slots_file = input("Enter path to time slot configuration file (JSON): ").strip()
    
    print("\n💾 OUTPUT FILE:")
    print("   Example: schedules.json")
    print("   Example: output/generated_schedules.json")
    print("   Example: ./results/schedule_output.json")
    output_file = input("Enter path to output file: ").strip()
    
    # Get optional inputs
    print("\n📊 SCHEDULE GENERATION LIMIT:")
    print("   Example: 10 (default)")
    print("   Example: 25")
    print("   Example: 100")
    print("   Valid range: 1-1000")
    while True:
        limit_input = input("Enter number of schedules to generate (default: 10): ").strip()
        if not limit_input:
            limit = 10
            break
        try:
            limit = int(limit_input)
            if limit <= 0:
                print("Error: Please enter a number greater than 0.")
                continue
            if limit > 1000:
                print("Error: Please enter a number less than 1000.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number.")
    
    print("\n📄 OUTPUT FORMAT:")
    print("   Example: json (default)")
    print("   Example: csv")
    print("   Accepted values: json, csv")
    format_input = input("Choose output format (json/csv, default: json): ").strip().lower()
    output_format = 'csv' if format_input in ['csv', 'c'] else 'json'
    # might get rid of this I don't know if it is necessary really
    print("\n📋 CONFIGURATION PREVIEW:")
    print("   Example: y (show config summary before generating schedules)")
    print("   Example: n (skip config preview - default)")
    print("   Accepted values: y/yes/true/1 for yes, n/no/false/0 for no")
    show_config_input = input("Show configuration summary? (y/n, default: n): ").strip().lower()
    show_config = show_config_input in ['y', 'yes', 'true', '1']
    
    print("\n🚀 SCHEDULE OPTIMIZATION:")
    print("   Example: y (enable optimization)")
    print("   Example: n (disable optimization - default)")
    print("   Accepted values: y/yes/true/1 for yes, n/no/false/0 for no")
    optimize_input = input("Enable schedule optimization? (y/n, default: n): ").strip().lower()
    optimize = optimize_input in ['y', 'yes', 'true', '1']
    
    return {
        'config': config_file,
        'time_slots': time_slots_file,
        'output': output_file,
        'limit': limit,
        'optimize': optimize,
        'format': output_format,
        'show_config': show_config
    }

def generate_schedules_interactive(config_file: str, full_config: dict, time_slots: dict) -> None:
    """
    Schedule generation using the scheduler API.
    """
    print("\n" + "="*60)
    print("SCHEDULE GENERATION")
    print("="*60)
    
    # Show configuration preview option
    show_preview = input("📋 Show configuration summary? (y/n, default: n): ").strip().lower()
    if show_preview in ['y', 'yes', 'true', '1']:
        print_config_summary(full_config.get('config', {}), time_slots)
    
    # Get scheduler parameters
    print("\n📊 SCHEDULE GENERATION PARAMETERS:")
    
    # Get limit
    while True:
        limit_input = input("Number of schedules to generate (1-1000, default: 10): ").strip()
        if not limit_input:
            limit = 10
            break
        try:
            limit = int(limit_input)
            if limit <= 0 or limit > 1000:
                print("Error: Please enter a number between 1 and 1000")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number")
    
    # Get format
    format_input = input("Output format (json/csv, default: json): ").strip().lower()
    output_format = 'csv' if format_input in ['csv', 'c'] else 'json'
    
    # Get output file
    output_file = input("What would like to name the output file (default: generated_schedules): ").strip()
    if not output_file:
        output_file = "generated_schedules"
    
    # Add extension if not provided
    if not output_file.endswith(f'.{output_format}'):
        output_file = f"{output_file}.{output_format}"
    
    # Confirm generation
    print(f"\n🚀 READY TO GENERATE SCHEDULES:")
    print(f"   Config file: {config_file}")
    print(f"   Schedules: {limit}")
    print(f"   Format: {output_format}")
    print(f"   Output: {output_file}")
    
    confirm = input("\nProceed with schedule generation? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Schedule generation cancelled.")
        return
    
    # Use the scheduler API
    try:
        print("\n🔄 Loading configuration for scheduler...")
        scheduler_config = load_config_from_file(CombinedConfig, config_file)
        
        print("🔄 Initializing scheduler...")
        scheduler = Scheduler(scheduler_config)
        
        print(f"🔄 Generating schedule(s)...")
        schedules = []
        count = 0
        for schedule in scheduler.get_models():
            if count >= limit:
                break
            schedules.append(schedule)
            count += 1
            print(f"   Generated schedule {count}")
            
        if not schedules:
            print("❌ No valid schedules could be generated.")
            print("   The scheduler couldn't find solutions with the current configuration.")
            return
        
        print(f"\n✅ Successfully generated {len(schedules)} schedule(s)!")

        # Save schedules
        save_schedules_to_file(schedules, output_file, output_format)

        print(f"\n💾 Schedules saved to: {output_file}")

        # Navigate through schedules
        if schedules:
            navigate_schedules(schedules)
        
    except Exception as e:
        print(f"❌ Error generating schedules: {e}")
        print("   The scheduler encountered an issue with the configuration.")
    
    input("\nPress Enter to continue...")

def navigate_schedules(schedules: list) -> None:
    """
    Interactive navigation through generated schedules.
    Args: schedules: List of generated schedules to navigate through
    """
    if not schedules:
        print("No schedules to display.")
        return

    current_index = 0
    total_schedules = len(schedules)

    while True:
        # Clear display and show current schedule
        print("\n" + "="*95)
        print(f"SCHEDULE VIEWER - Schedule {current_index + 1} of {total_schedules}")
        print("="*95)

        # Display current schedule in tabular format
        current_schedule = [course.as_csv() for course in schedules[current_index]]
        display_schedule_basic(current_schedule)

        print("-" * 95)

        # Navigation menu
        print("\n📋 NAVIGATION OPTIONS:")
        print("   [d] Next schedule")
        print("   [a] Previous schedule")
        print("   [w] Go to specific schedule")
        print("   [s] Return to main menu")
        print("-" * 60)

        choice = input("Select an option: ").strip().lower()

        if choice == 'd':
            if current_index < total_schedules - 1:
                current_index += 1
            else:
                print("Already at the last schedule.")
                input("Press Enter to continue...")
        elif choice == 'a':
            if current_index > 0:
                current_index -= 1
            else:
                print("Already at the first schedule.")
                input("Press Enter to continue...")
        elif choice == 'w':
            try:
                schedule_num = int(input(f"Enter schedule number (1-{total_schedules}): ").strip())
                if 1 <= schedule_num <= total_schedules:
                    current_index = schedule_num - 1
                else:
                    print(f"Invalid schedule number. Please enter a number between 1 and {total_schedules}.")
                    input("Press Enter to continue...")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                input("Press Enter to continue...")
        elif choice == 's':
            break
        else:
            print("Invalid option. Please select w, a, s, or d.")
            input("Press Enter to continue...")

def load_schedules_from_json(file_path: str) -> list:
    """
    Load schedules from a JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        schedules = []
        for schedule_data in data:
            if isinstance(schedule_data, dict) and 'courses' in schedule_data:
                schedules.append(schedule_data['courses'])
            else:
                # Handle simple list format
                schedules.append(schedule_data)

        return schedules
    except FileNotFoundError:
        raise FileNotFoundError(f"Schedule file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading schedule file {file_path}: {e}")

def parse_course_string(course_str: str) -> dict:
    """
    Parse a course CSV string into a dictionary.
    Format: CMSC 140.01,Hardy,Roddy 147,Mac,MON 14:00-14:50,TUE 13:10-15:00
    Returns: Dictionary with course_id, faculty, room, lab, and time_slots
    """
    parts = course_str.split(',')
    if len(parts) < 4:
        return None

    course_id = parts[0].strip()
    faculty = parts[1].strip()
    room = parts[2].strip()
    lab = parts[3].strip()
    time_slots = [slot.strip() for slot in parts[4:]]

    return {
        'course_id': course_id,
        'faculty': faculty,
        'room': room,
        'lab': lab,
        'time_slots': time_slots
    }

def display_schedule_basic(schedule: list) -> None:
    """
    Display a schedule in tabular format showing all courses.
    """
    if not schedule:
        print("No schedule data to display.")
        return

    # Parse all courses
    courses = []
    for course_str in schedule:
        course = parse_course_string(course_str)
        if course:
            courses.append(course)

    if not courses:
        print("No valid course data to display.")
        return

    # Display all courses in a table
    print("\n" + "="*95)
    print("SCHEDULE")
    print("="*95)

    # Create table header
    print(f"| {'Course':<12} | {'Faculty':<8} | {'MON':<11} | {'TUE':<11} | {'WED':<11} | {'THU':<11} | {'FRI':<11} |")
    print("="*95)

    # Create rows for each course
    for course in courses:
        # Parse time slots by day
        day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}

        for slot in course['time_slots']:
            # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
            slot_clean = slot.replace('^', '')  # Remove lab indicator
            parts = slot_clean.split(' ', 1)
            if len(parts) == 2:
                day = parts[0].strip()
                time = parts[1].strip()
                if day in day_times:
                    if day_times[day]:
                        day_times[day] += '\n' + time
                    else:
                        day_times[day] = time

        # Print course row
        print(f"| {course['course_id']:<12} | {course['faculty']:<8} | {day_times['MON']:<11} | {day_times['TUE']:<11} | {day_times['WED']:<11} | {day_times['THU']:<11} | {day_times['FRI']:<11} |")

def display_schedule_by_room(schedule: list) -> None:

    if not schedule:
        print("No schedule data to display.")
        return

    # Parse all courses and group by room and lab
    room_schedule = {}  # room -> list of course data
    lab_schedule = {}   # lab -> list of course data

    for course_str in schedule:
        course = parse_course_string(course_str)
        if not course:
            continue

        # Group by room
        room = course['room']
        if room not in room_schedule:
            room_schedule[room] = []
        room_schedule[room].append(course)

        # Group by lab (if not None)
        lab = course['lab']
        if lab and lab.lower() != 'none':
            if lab not in lab_schedule:
                lab_schedule[lab] = []
            lab_schedule[lab].append(course)

    # Display room schedules
    print("\n" + "="*80)
    print("SCHEDULE BY ROOM")
    print("="*80)

    for room, courses in sorted(room_schedule.items()):
        print(f"\n{room}")
        print("-" * 80)

        # Create table header
        print(f"{'Course':<15} | {'Faculty':<10} | {'MON':<15} | {'TUE':<15} | {'WED':<15} | {'THU':<15} | {'FRI':<15}")
        print("-" * 80)

        # Create rows for each course
        for course in courses:
            # Parse time slots by day
            day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}

            for slot in course['time_slots']:
                # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
                slot = slot.replace('^', '')  # Remove lab indicator
                parts = slot.split(' ', 1)
                if len(parts) == 2:
                    day = parts[0].strip()
                    time = parts[1].strip()
                    if day in day_times:
                        if day_times[day]:
                            day_times[day] += '\n' + time
                        else:
                            day_times[day] = time

            # Print course row
            print(f"{course['course_id']:<15} | {course['faculty']:<10} | {day_times['MON']:<15} | {day_times['TUE']:<15} | {day_times['WED']:<15} | {day_times['THU']:<15} | {day_times['FRI']:<15}")

    # Display lab schedules
    if lab_schedule:
        print("\n" + "="*80)
        print("LAB SCHEDULES")
        print("="*80)

        for lab, courses in sorted(lab_schedule.items()):
            print(f"\n{lab} Lab")
            print("-" * 80)

            # Create table header
            print(f"{'Course':<15} | {'Faculty':<10} | {'MON':<15} | {'TUE':<15} | {'WED':<15} | {'THU':<15} | {'FRI':<15}")
            print("-" * 80)

            # Create rows for each course
            for course in courses:
                # Parse time slots by day (only show lab sessions marked with ^)
                day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}

                for slot in course['time_slots']:
                    # Only include lab sessions (marked with ^)
                    if '^' in slot:
                        slot = slot.replace('^', '')
                        parts = slot.split(' ', 1)
                        if len(parts) == 2:
                            day = parts[0].strip()
                            time = parts[1].strip()
                            if day in day_times:
                                if day_times[day]:
                                    day_times[day] += '\n' + time
                                else:
                                    day_times[day] = time

                # Print course row
                print(f"{course['course_id']:<15} | {course['faculty']:<10} | {day_times['MON']:<15} | {day_times['TUE']:<15} | {day_times['WED']:<15} | {day_times['THU']:<15} | {day_times['FRI']:<15}")

def display_schedule_by_faculty(schedule: list) -> None:

    if not schedule:
        print("No schedule data to display.")
        return

    # Parse all courses and group by faculty
    faculty_schedule = {}  # faculty -> list of course data

    for course_str in schedule:
        course = parse_course_string(course_str)
        if not course:
            continue

        faculty = course['faculty']
        if faculty not in faculty_schedule:
            faculty_schedule[faculty] = []
        faculty_schedule[faculty].append(course)

    # Display faculty schedules
    print("\n" + "="*80)
    print("SCHEDULE BY FACULTY")
    print("="*80)

    for faculty, courses in sorted(faculty_schedule.items()):
        print(f"\n{faculty}")
        print("-" * 80)

        # Create table header
        print(f"{'Course':<15} | {'Room':<12} | {'Lab':<8} | {'MON':<15} | {'TUE':<15} | {'WED':<15} | {'THU':<15} | {'FRI':<15}")
        print("-" * 80)

        # Create rows for each course
        for course in courses:
            # Parse time slots by day
            day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}

            for slot in course['time_slots']:
                # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
                slot_clean = slot.replace('^', '')  # Remove lab indicator for parsing
                parts = slot_clean.split(' ', 1)
                if len(parts) == 2:
                    day = parts[0].strip()
                    time = parts[1].strip()
                    if day in day_times:
                        if day_times[day]:
                            day_times[day] += '\n' + time
                        else:
                            day_times[day] = time

            # Print course row
            lab_display = course['lab'] if course['lab'].lower() != 'none' else '-'
            print(f"{course['course_id']:<15} | {course['room']:<12} | {lab_display:<8} | {day_times['MON']:<15} | {day_times['TUE']:<15} | {day_times['WED']:<15} | {day_times['THU']:<15} | {day_times['FRI']:<15}")

def navigate_raw_schedules(schedules: list) -> None:
    """
    Interactive navigation through schedules loaded from JSON (raw strings).
    Args: schedules: List of schedules (each schedule is a list of course strings)
    """
    if not schedules:
        print("No schedules to display.")
        return

    current_index = 0
    total_schedules = len(schedules)

    while True:
        # Clear display and show current schedule
        print("\n" + "="*95)
        print(f"SCHEDULE VIEWER - Schedule {current_index + 1} of {total_schedules}")
        print("="*95)

        # Display current schedule in tabular format
        current_schedule = schedules[current_index]
        if isinstance(current_schedule, list):
            display_schedule_basic(current_schedule)
        else:
            print(f"   {current_schedule}")

        print("-" * 95)

        # Navigation menu
        print("\n📋 NAVIGATION OPTIONS:")
        print("   [d] Next schedule")
        print("   [a] Previous schedule")
        print("   [w] Go to specific schedule")
        print("   [r] View by room/lab")
        print("   [f] View by faculty")
        print("   [s] Return to main menu")
        print("-" * 60)

        choice = input("Select an option: ").strip().lower()

        if choice == 'd':
            if current_index < total_schedules - 1:
                current_index += 1
            else:
                print("Already at the last schedule.")
                input("Press Enter to continue...")
        elif choice == 'a':
            if current_index > 0:
                current_index -= 1
            else:
                print("Already at the first schedule.")
                input("Press Enter to continue...")
        elif choice == 'w':
            try:
                schedule_num = int(input(f"Enter schedule number (1-{total_schedules}): ").strip())
                if 1 <= schedule_num <= total_schedules:
                    current_index = schedule_num - 1
                else:
                    print(f"Invalid schedule number. Please enter a number between 1 and {total_schedules}.")
                    input("Press Enter to continue...")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                input("Press Enter to continue...")
        elif choice == 'r':
            # Display by room
            display_schedule_by_room(current_schedule)
            input("\nPress Enter to continue...")
        elif choice == 'f':
            # Display by faculty
            display_schedule_by_faculty(current_schedule)
            input("\nPress Enter to continue...")
        elif choice == 's':
            break
        else:
            print("Invalid option. Please select w, a, s, d, r, or f.")
            input("Press Enter to continue...")

def show_schedule_management_menu() -> str:
    """Display schedule management submenu and get user choice."""
    print("\n" + "="*60)
    print("SCHEDULE IMPORT/EXPORT MANAGEMENT")
    print("="*60)
    print("1. 📝 Generate New Schedules")
    print("2. 📥 Import Schedules from JSON")
    print("3. 🔙 Return to Main Menu")
    print("="*60)

    return input("Select an option (1-3): ").strip()

def import_schedules_interactive() -> None:
    """
    Import and view schedules from a JSON file.
    """
    print("\n" + "="*60)
    print("IMPORT SCHEDULES")
    print("="*60)

    # Get file path
    print("\n📂 SELECT JSON FILE TO IMPORT:")
    print("   Example: generated_schedules.json")
    print("   Example: /path/to/schedules.json")
    file_path = input("Enter path to schedule JSON file: ").strip()

    if not file_path:
        print("No file path provided. Import cancelled.")
        input("\nPress Enter to continue...")
        return

    try:
        # Load schedules from JSON
        print(f"\n🔄 Loading schedules from {file_path}...")
        schedules = load_schedules_from_json(file_path)

        if not schedules:
            print("❌ No schedules found in the file.")
            input("\nPress Enter to continue...")
            return

        print(f"✅ Successfully loaded {len(schedules)} schedule(s)!")

        # Navigate through imported schedules
        schedules_view.navigate_raw_schedules(schedules)

    except FileNotFoundError as e:
        print(f"❌ {e}")
        input("\nPress Enter to continue...")
    except ValueError as e:
        print(f"❌ {e}")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"❌ Error importing schedules: {e}")
        input("\nPress Enter to continue...")

def schedule_management_menu(config_file: str, full_config: dict, time_slots: dict) -> None:
    """
    Schedule management menu with import/export options.
    """
    while True:
        choice = show_schedule_management_menu()

        if choice == '1':
            # Generate new schedules
            generate_schedules_interactive(config_file, full_config, time_slots)

        elif choice == '2':
            # Import existing schedules
            import_schedules_interactive()

        elif choice == '3':
            # Return to main menu
            break

        else:
            print("Invalid choice. Please select 1, 2, or 3.")
            input("\nPress Enter to continue...")

def save_schedules_to_file(schedules: list, output_file: str, format_type: str) -> None:
    """Save generated schedules to file."""
    try:
        if format_type == 'csv':
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Schedule,Course,Day,Time,Duration,Room,Lab,Faculty\n")
                for i, schedule in enumerate(schedules, 1):
                    for course in schedule:
                        csv_line = course.as_csv()
                        f.write(f"{i},{csv_line}\n")
        else:
            # JSON format
            json_schedules = []
            for i, schedule in enumerate(schedules, 1):
                schedule_data = {
                    'schedule_id': i,
                    'courses': [course.as_csv() for course in schedule]
                }
                json_schedules.append(schedule_data)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_schedules, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Error saving schedules: {e}")

def run_cli():
    """
    Run the CLI version of the scheduler application.
    """
    print("Welcome to the Scheduler CLI!")
    print("Loading initial configuration...")
    
    # Get configuration file
    print("\n📁 CONFIGURATION FILE:")
    print("   Example: example.json")
    print("   Example: /path/to/config.json")
    config_file = input("Enter path to configuration file (JSON): ").strip()
    
    # Validate and load configurations
    config_path = validate_file_path(config_file, must_exist=True)
    print(f"Loading configuration from: {config_path}")
    config = load_config(str(config_path))
    
    # Load time slots from same file (assuming nested structure like example.json)
    print(f"Loading time slot configuration from: {config_path}")
    time_slots = load_time_slot_config(str(config_path))
    
    # Load full config for room manager (needs both config and time_slot_config)
    with open(str(config_path), 'r') as f:
        full_config = json.load(f)

    while True:
        choice = show_main_menu()
        if choice == '1':
            course_manager = CourseManager() # Course Management
            config = course_manager.course_management_menu(config, str(config_path), time_slots)
            
        elif choice == '2':
            room_manager = RoomManager(full_config) # Room Management
            config = room_manager.room_management_menu(str(config_path), time_slots)
            full_config['config'] = config
            
        elif choice == '3':
            lab_manager = LabManager() # Lab Management
            config = lab_manager.lab_management_menu(str(config_path), config, time_slots)
            full_config['config'] = config
            
        elif choice == '4':
            faculty_manager = FacultyManager(full_config) # Faculty Management
            config = faculty_manager.faculty_management_menu(str(config_path), time_slots)
            # Update full_config with the new config
            full_config['config'] = config
            
        elif choice == '5':
            # Schedule Management (Generate/Import/Export)
            schedule_management_menu(str(config_path), full_config, time_slots)
            
        elif choice == '6':
            # Exit
            print("Thank you for using Scheduler CLI!")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, 5, or 6.")

def run_gui():

    app = None
    try:
        print("Starting GUI Application...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        gui = MainGUI()
        gui.run_gui_interactive()
    except ImportError:
        print("❌ GUI module not found. Please ensure main_gui.py is available.")
        input("Press Enter to return to interface selection...")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        input("Press Enter to return to interface selection...")

def main():

    try:
        print("Welcome to the Scheduler Application!")
        while True:
            choice = show_interface_selection()
            
            if choice == '1':
                run_cli()
                break
            elif choice == '2':
                run_gui()
            elif choice == '3':    # Exit
                print("Thank you for using the Scheduler Application!")
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    main()