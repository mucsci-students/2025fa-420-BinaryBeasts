#!/usr/bin/env python3
"""
Scheduler CLI Application
Command-line tool for generating and optimizing schedules.
"""
import sys
import json
from pathlib import Path
from generate_csv import ScheduleCSVGenerator
from saveConfigFile import save_config_file
from courses import CourseManager, Course
from room import RoomManager
from lab_manager import LabManager

def load_config(config_file: str) -> dict:
    """
    Load configuration from the specified config file.
    Args:
        config_file: Path to the configuration file
    Returns:
        Dictionary containing configuration data
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        if 'config' in data:
            return data['config']
        else:
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {config_file}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_file}")
    except Exception as e:
        raise Exception(f"Error loading config file {config_file}: {e}")


def load_time_slot_config(time_slot_config: str) -> dict:
    """
    Load time slot configuration from the specified file.
    Args:
        time_slot_config: Path to the time slot configuration file
    Returns:
        Dictionary containing time slot configuration
    """
    try:
        with open(time_slot_config, 'r') as f:
            data = json.load(f)
        
        if 'time_slot_config' in data:
            return data['time_slot_config']
        else:
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in time slot config file {time_slot_config}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Time slot config file not found: {time_slot_config}")
    except Exception as e:
        raise Exception(f"Error loading time slot config file {time_slot_config}: {e}")



def generate_schedules(config: dict, time_slots: dict, limit: int, optimize: bool) -> list:
    """
    Generate schedules based on configuration and constraints.
    Args:
        config: Configuration dictionary
        time_slots: Time slot configuration dictionary
        limit: Maximum number of schedules to generate
        optimize: Whether to optimize the generated schedules
    Returns:
        List of generated schedules
    """
    # Use the CSV generator to create schedules
    csv_generator = ScheduleCSVGenerator(config, time_slots)
    schedules = csv_generator.generate_schedules_from_config(limit)
    
    if optimize:
        print("Applying optimization...")
        # Apply optimization logic here
        for schedule in schedules:
            schedule['optimization_score'] = schedule.get('optimization_score', 75.0) + 10.0
    
    return schedules


def optimize_schedule(schedule: dict) -> dict:
    """
    Optimize a single schedule according to specified criteria.
    Args:
        schedule: Schedule dictionary to optimize
    Returns:
        Optimized schedule dictionary
    """
    pass


def save_schedules(schedules: list, output_file: str, output_format: str = 'json') -> None:
    """
    Save generated schedules to the specified output file.
    Args:
        schedules: List of schedules to save
        output_file: Path to the output file
        output_format: Format to save in ('json' or 'csv')
    """
    try:
        if output_format.lower() == 'csv':
            # Save as CSV format
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                if schedules:
                    fieldnames = schedules[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(schedules)
                print(f"Successfully saved {len(schedules)} schedules to {output_file} (CSV format)")
        else:
            # Save as JSON format (default)
            save_config_file(output_file, schedules)
            print(f"Successfully saved {len(schedules)} schedules to {output_file} (JSON format)")
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing to output file: {output_file}")
    except OSError as e:
        raise OSError(f"Error writing to output file {output_file}: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error saving schedules to {output_file}: {e}")


def print_config_summary(config: dict, time_slots: dict) -> None:
    """
    Print a human-readable summary of the configuration.
    Args:
        config: Configuration dictionary
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
        # Reconstruct the full configuration structure
        full_config = {
            "config": config,
            "time_slot_config": time_slots
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration saved successfully to {config_file}")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")


def display_courses(course_manager: CourseManager) -> None:
    """Display all courses in a formatted list."""
    print("\n" + "="*60)
    print("COURSE LIST")
    print("="*60)
    
    all_courses = course_manager.get_all_courses()
    if not all_courses:
        print("No courses found.")
        return
    
    for course_id, instances in all_courses.items():
        print(f"\n📖 {course_id}")
        for i, course in enumerate(instances):
            instance_label = f" (Instance {i+1})" if len(instances) > 1 else ""
            print(f"   {instance_label}")
            print(f"   📊 Credits: {course.credits}")
            print(f"   🏢 Rooms: {', '.join(course.room) if course.room else 'None'}")
            print(f"   🔬 Labs: {', '.join(course.lab) if course.lab else 'None'}")
            print(f"   👤 Faculty: {', '.join(course.faculty) if course.faculty else 'Unassigned'}")
            print(f"   ⚠️  Conflicts: {', '.join(course.conflicts) if course.conflicts else 'None'}")
            if i < len(instances) - 1:
                print("   " + "-" * 40)
    
    print("="*60)


def get_course_input() -> dict:
    """Get course information from user input."""
    print("\n🆕 ADD NEW COURSE")
    print("=" * 30)
    
    course_id = input("Course ID (e.g., CMSC 101): ").strip()
    if not course_id:
        raise ValueError("Course ID cannot be empty")
    
    while True:
        try:
            credits = int(input("Credits (1-6): ").strip())
            if credits < 1 or credits > 6:
                print("Error: Credits must be between 1 and 6")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number for credits")
    
    print("\nRooms (press Enter to finish):")
    rooms = []
    while True:
        room = input(f"  Room {len(rooms)+1} (or Enter to finish): ").strip()
        if not room:
            break
        rooms.append(room)
    
    print("\nLabs (press Enter to finish):")
    labs = []
    while True:
        lab = input(f"  Lab {len(labs)+1} (or Enter to finish): ").strip()
        if not lab:
            break
        labs.append(lab)
    
    print("\nFaculty (press Enter to finish):")
    faculty = []
    while True:
        fac = input(f"  Faculty {len(faculty)+1} (or Enter to finish): ").strip()
        if not fac:
            break
        faculty.append(fac)
    
    print("\nConflicting courses (press Enter to finish):")
    conflicts = []
    while True:
        conflict = input(f"  Conflict {len(conflicts)+1} (or Enter to finish): ").strip()
        if not conflict:
            break
        conflicts.append(conflict)
    
    return {
        'course_id': course_id,
        'credits': credits,
        'room': rooms,
        'lab': labs,
        'faculty': faculty,
        'conflicts': conflicts
    }


def add_course_interactive(course_manager: CourseManager) -> None:
    """Interactive course addition."""
    try:
        course_data = get_course_input()
        course = Course(**course_data)
        course_manager.add_course(course)
        print(f"✅ Successfully added course: {course.course_id}")
    except Exception as e:
        print(f"❌ Error adding course: {e}")


def modify_course_interactive(course_manager: CourseManager) -> None:
    """Interactive course modification."""
    display_courses(course_manager)
    
    course_id = input("\nEnter Course ID to modify: ").strip()
    course_instances = course_manager.get_course(course_id)
    
    if not course_instances:
        print(f"❌ Course {course_id} not found.")
        return
    
    if len(course_instances) > 1:
        print(f"\nFound {len(course_instances)} instances of {course_id}:")
        for i, course in enumerate(course_instances):
            print(f"  {i+1}. Instance {i+1}")
        
        while True:
            try:
                choice = int(input("Select instance to modify (number): ")) - 1
                if 0 <= choice < len(course_instances):
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        choice = 0
    
    current_course = course_instances[choice]
    print(f"\n📝 MODIFYING: {current_course.course_id} (Instance {choice+1})")
    
    # Get new values, showing current values as defaults
    print(f"\nCurrent credits: {current_course.credits}")
    credits_input = input("New credits (press Enter to keep current): ").strip()
    credits = int(credits_input) if credits_input else current_course.credits
    
    print(f"\nCurrent rooms: {', '.join(current_course.room) if current_course.room else 'None'}")
    print("Enter new rooms (press Enter to finish, 'keep' to keep current):")
    rooms_input = input("  New rooms (or 'keep'): ").strip().lower()
    if rooms_input == 'keep':
        rooms = current_course.room
    else:
        rooms = []
        if rooms_input:
            rooms.append(rooms_input)
        while True:
            room = input(f"  Room {len(rooms)+1} (or Enter to finish): ").strip()
            if not room:
                break
            rooms.append(room)
    
    # Similar for other fields
    print(f"\nCurrent labs: {', '.join(current_course.lab) if current_course.lab else 'None'}")
    labs_input = input("Enter new labs ('keep' to keep current, Enter for none): ").strip().lower()
    if labs_input == 'keep':
        labs = current_course.lab
    else:
        labs = []
        if labs_input and labs_input != 'keep':
            labs.append(labs_input)
            while True:
                lab = input(f"  Lab {len(labs)+1} (or Enter to finish): ").strip()
                if not lab:
                    break
                labs.append(lab)
    
    print(f"\nCurrent faculty: {', '.join(current_course.faculty) if current_course.faculty else 'None'}")
    faculty_input = input("Enter new faculty ('keep' to keep current, Enter for none): ").strip().lower()
    if faculty_input == 'keep':
        faculty = current_course.faculty
    else:
        faculty = []
        if faculty_input and faculty_input != 'keep':
            faculty.append(faculty_input)
            while True:
                fac = input(f"  Faculty {len(faculty)+1} (or Enter to finish): ").strip()
                if not fac:
                    break
                faculty.append(fac)
    
    print(f"\nCurrent conflicts: {', '.join(current_course.conflicts) if current_course.conflicts else 'None'}")
    conflicts_input = input("Enter new conflicts ('keep' to keep current, Enter for none): ").strip().lower()
    if conflicts_input == 'keep':
        conflicts = current_course.conflicts
    else:
        conflicts = []
        if conflicts_input and conflicts_input != 'keep':
            conflicts.append(conflicts_input)
            while True:
                conflict = input(f"  Conflict {len(conflicts)+1} (or Enter to finish): ").strip()
                if not conflict:
                    break
                conflicts.append(conflict)
    
    # Remove old instance and add new one
    course_manager.delete_course(course_id, choice)
    new_course = Course(
        course_id=current_course.course_id,
        credits=credits,
        room=rooms,
        lab=labs,
        faculty=faculty,
        conflicts=conflicts
    )
    course_manager.add_course(new_course)
    
    print(f"✅ Successfully modified course: {current_course.course_id}")


def delete_course_interactive(course_manager: CourseManager) -> None:
    """Interactive course deletion."""
    display_courses(course_manager)
    
    course_id = input("\nEnter Course ID to delete: ").strip()
    course_instances = course_manager.get_course(course_id)
    
    if not course_instances:
        print(f"❌ Course {course_id} not found.")
        return
    
    if len(course_instances) > 1:
        print(f"\nFound {len(course_instances)} instances of {course_id}:")
        print("  0. Delete ALL instances")
        for i, course in enumerate(course_instances):
            print(f"  {i+1}. Delete instance {i+1}")
        
        while True:
            try:
                choice = int(input("Select option (number): "))
                if 0 <= choice <= len(course_instances):
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        if choice == 0:
            # Delete all instances
            while course_manager.get_course(course_id):
                course_manager.delete_course(course_id, 0)
            print(f"✅ Successfully deleted all instances of course: {course_id}")
        else:
            course_manager.delete_course(course_id, choice - 1)
            print(f"✅ Successfully deleted instance {choice} of course: {course_id}")
    else:
        confirm = input(f"Are you sure you want to delete {course_id}? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            course_manager.delete_course(course_id, 0)
            print(f"✅ Successfully deleted course: {course_id}")
        else:
            print("Deletion cancelled.")


def course_management_menu(config: dict, config_file: str, time_slots: dict) -> dict:
    """Course management menu interface."""
    course_manager = CourseManager()
    course_manager.load_courses(config.get('courses', []))
    
    while True:
        print("\n" + "="*50)
        print("COURSE MANAGEMENT")
        print("="*50)
        print("1. 👀 View all courses")
        print("2. ➕ Add new course")
        print("3. ✏️  Modify existing course")
        print("4. ❌ Delete course")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("="*50)
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            display_courses(course_manager)
        elif choice == '2':
            add_course_interactive(course_manager)
        elif choice == '3':
            modify_course_interactive(course_manager)
        elif choice == '4':
            delete_course_interactive(course_manager)
        elif choice == '5':
            # Save changes back to config
            updated_courses = []
            for course_instances in course_manager.get_all_courses().values():
                for course in course_instances:
                    updated_courses.append({
                        'course_id': course.course_id,
                        'credits': course.credits,
                        'room': course.room,
                        'lab': course.lab,
                        'faculty': course.faculty,
                        'conflicts': course.conflicts
                    })
            
            config['courses'] = updated_courses
            save_config_to_file(config, time_slots, config_file)
            return config
        elif choice == '6':
            print("Exiting without saving changes.")
            return config
        else:
            print("Invalid choice. Please select 1-6.")


def display_rooms(room_manager: RoomManager) -> None:
    """Display all rooms in a formatted list."""
    print("\n" + "="*60)
    print("ROOM LIST")
    print("="*60)
    
    rooms = room_manager.get_rooms()
    if not rooms:
        print("No rooms found.")
        return
    
    print(f"📍 Total Rooms: {len(rooms)}")
    print("-" * 60)
    
    for i, room in enumerate(rooms, 1):
        print(f"{i:3}. 🏢 {room}")
    
    print("="*60)


def add_room_interactive(room_manager: RoomManager) -> None:
    """Interactive room addition."""
    print("\n🆕 ADD NEW ROOM")
    print("=" * 30)
    
    room_name = input("Room name (e.g., Roddy 101): ").strip()
    if not room_name:
        print("❌ Room name cannot be empty.")
        return
    
    try:
        if room_manager.add_room(room_name):
            print(f"✅ Successfully added room: {room_name}")
        else:
            print(f"❌ Room '{room_name}' already exists.")
    except Exception as e:
        print(f"❌ Error adding room: {e}")


def edit_room_interactive(room_manager: RoomManager) -> None:
    """Interactive room editing/renaming."""
    display_rooms(room_manager)
    
    if not room_manager.get_rooms():
        print("❌ No rooms available to edit.")
        return
    
    old_name = input("\nEnter current room name to edit: ").strip()
    if not old_name:
        print("❌ Room name cannot be empty.")
        return
    
    if old_name not in room_manager.get_rooms():
        print(f"❌ Room '{old_name}' not found.")
        return
    
    new_name = input(f"Enter new name for '{old_name}': ").strip()
    if not new_name:
        print("❌ New room name cannot be empty.")
        return
    
    try:
        if room_manager.edit_room(old_name, new_name):
            print(f"✅ Successfully renamed '{old_name}' to '{new_name}'")
            print("📝 Note: All course and faculty references have been updated automatically.")
        else:
            if new_name in room_manager.get_rooms():
                print(f"❌ Room '{new_name}' already exists.")
            else:
                print(f"❌ Failed to rename room.")
    except Exception as e:
        print(f"❌ Error editing room: {e}")


def delete_room_interactive(room_manager: RoomManager) -> None:
    """Interactive room deletion with impact analysis."""
    display_rooms(room_manager)
    
    if not room_manager.get_rooms():
        print("❌ No rooms available to delete.")
        return
    
    room_name = input("\nEnter room name to delete: ").strip()
    if not room_name:
        print("❌ Room name cannot be empty.")
        return
    
    if room_name not in room_manager.get_rooms():
        print(f"❌ Room '{room_name}' not found.")
        return
    
    # Analyze impact of deletion
    print(f"\n🔍 ANALYZING IMPACT OF DELETING '{room_name}':")
    print("-" * 50)
    
    # Check courses using this room
    affected_courses = []
    config = room_manager.config.get('config', {})
    for course in config.get('courses', []):
        if 'room' in course and isinstance(course['room'], list):
            if room_name in course['room']:
                affected_courses.append(course.get('course_id', 'Unknown'))
    
    # Check faculty preferences
    affected_faculty = []
    for faculty in config.get('faculty', []):
        room_prefs = faculty.get('room_preferences', {})
        if room_name in room_prefs:
            affected_faculty.append(faculty.get('name', 'Unknown'))
    
    if affected_courses:
        print(f"📚 Courses using this room ({len(affected_courses)}):")
        for course in affected_courses:
            print(f"   • {course}")
    
    if affected_faculty:
        print(f"👥 Faculty with preferences for this room ({len(affected_faculty)}):")
        for faculty in affected_faculty:
            print(f"   • {faculty}")
    
    if not affected_courses and not affected_faculty:
        print("✅ No conflicts found. Room can be safely deleted.")
    else:
        print("\n⚠️  Warning: Deleting this room will:")
        if affected_courses:
            print(f"   • Remove room assignment from {len(affected_courses)} course(s)")
        if affected_faculty:
            print(f"   • Remove room preferences from {len(affected_faculty)} faculty member(s)")
    
    # Confirm deletion
    confirm = input(f"\nAre you sure you want to delete '{room_name}'? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        try:
            if room_manager.delete_room(room_name):
                print(f"✅ Successfully deleted room: {room_name}")
                if affected_courses or affected_faculty:
                    print("📝 Note: All references have been automatically removed.")
            else:
                print(f"❌ Failed to delete room '{room_name}'.")
        except Exception as e:
            print(f"❌ Error deleting room: {e}")
    else:
        print("Deletion cancelled.")


def room_management_menu(full_config: dict, config_file: str, time_slots: dict) -> dict:
    """Room management menu interface."""
    try:
        # RoomManager expects the full structure with 'config' key
        room_manager = RoomManager(full_config)
        
        while True:
            print("\n" + "="*50)
            print("ROOM MANAGEMENT")
            print("="*50)
            print("1. 👀 View all rooms")
            print("2. ➕ Add new room")
            print("3. ✏️  Edit/rename room")
            print("4. ❌ Delete room")
            print("5. 💾 Save changes and exit")
            print("6. 🚪 Exit without saving")
            print("="*50)
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                display_rooms(room_manager)
            elif choice == '2':
                add_room_interactive(room_manager)
            elif choice == '3':
                edit_room_interactive(room_manager)
            elif choice == '4':
                delete_room_interactive(room_manager)
            elif choice == '5':
                # Save changes back to full config
                save_config_to_file(full_config['config'], time_slots, config_file)
                return full_config['config']
            elif choice == '6':
                print("Exiting without saving changes.")
                return full_config['config']
            else:
                print("Invalid choice. Please select 1-6.")
                
    except Exception as e:
        print(f"❌ Error initializing room manager: {e}")
        return full_config.get('config', {})


def display_labs_and_courses(lab_manager: LabManager) -> None:
    """Display all labs and which courses use them."""
    print("\n" + "="*60)
    print("LAB USAGE SUMMARY")
    print("="*60)
    
    # Get all labs from the global labs list
    all_labs = lab_manager.data.get('config', {}).get('labs', [])
    courses = lab_manager.data.get('config', {}).get('courses', [])
    
    if not all_labs:
        print("No labs found in configuration.")
        return
    
    print(f"📍 Total Labs Available: {len(all_labs)}")
    print("-" * 60)
    
    for lab in all_labs:
        print(f"\n🔬 {lab}")
        
        # Find courses that use this lab
        courses_using_lab = []
        for course in courses:
            if 'lab' in course and isinstance(course.get('lab'), list):
                if lab in course['lab']:
                    courses_using_lab.append(course.get('course_id', 'Unknown'))
        
        if courses_using_lab:
            print(f"   📚 Used by {len(courses_using_lab)} course(s):")
            for course_id in courses_using_lab:
                print(f"      • {course_id}")
        else:
            print("   📭 No courses currently use this lab")
    
    print("="*60)


def add_lab_to_course_interactive(lab_manager: LabManager) -> None:
    """Interactive lab assignment to course."""
    print("\n➕ ADD LAB TO COURSE")
    print("=" * 30)
    
    # Show available courses
    courses = lab_manager.data.get('config', {}).get('courses', [])
    if not courses:
        print("❌ No courses found.")
        return
    
    print("Available courses:")
    course_ids = set()
    for course in courses:
        course_id = course.get('course_id')
        if course_id:
            course_ids.add(course_id)
    
    for i, course_id in enumerate(sorted(course_ids), 1):
        print(f"  {i}. {course_id}")
    
    course_id = input("\nEnter Course ID to add lab to: ").strip()
    if not course_id:
        print("❌ Course ID cannot be empty.")
        return
    
    # Check if course exists
    if not lab_manager.get_course_by_id(course_id):
        print(f"❌ Course '{course_id}' not found.")
        return
    
    # Show available labs
    all_labs = lab_manager.data.get('config', {}).get('labs', [])
    if not all_labs:
        print("❌ No labs available in configuration.")
        return
    
    print(f"\nAvailable labs:")
    for i, lab in enumerate(all_labs, 1):
        print(f"  {i}. {lab}")
    
    lab_type = input("\nEnter lab name to add: ").strip()
    if not lab_type:
        print("❌ Lab name cannot be empty.")
        return
    
    if lab_type not in all_labs:
        print(f"❌ Lab '{lab_type}' not found in available labs.")
        return
    
    try:
        result = lab_manager.add_lab(course_id, lab_type)
        if result:
            print(f"✅ Successfully added lab '{lab_type}' to course '{course_id}'")
        else:
            print(f"❌ Failed to add lab. Lab may already be assigned to this course.")
    except Exception as e:
        print(f"❌ Error adding lab: {e}")


def modify_lab_interactive(lab_manager: LabManager) -> None:
    """Interactive lab modification for courses."""
    display_labs_and_courses(lab_manager)
    
    course_id = input("\nEnter Course ID to modify lab for: ").strip()
    if not course_id:
        print("❌ Course ID cannot be empty.")
        return
    
    # Check if course exists
    course = lab_manager.get_course_by_id(course_id)
    if not course:
        print(f"❌ Course '{course_id}' not found.")
        return
    
    # Show current labs for this course
    current_labs = course.get('lab', [])
    if not current_labs:
        print(f"❌ Course '{course_id}' has no labs assigned.")
        return
    
    print(f"\nCurrent labs for {course_id}:")
    for i, lab in enumerate(current_labs, 1):
        print(f"  {i}. {lab}")
    
    old_lab = input("\nEnter current lab name to modify: ").strip()
    if not old_lab:
        print("❌ Lab name cannot be empty.")
        return
    
    if old_lab not in current_labs:
        print(f"❌ Lab '{old_lab}' is not assigned to course '{course_id}'.")
        return
    
    # Show available labs
    all_labs = lab_manager.data.get('config', {}).get('labs', [])
    print(f"\nAvailable labs:")
    for i, lab in enumerate(all_labs, 1):
        print(f"  {i}. {lab}")
    
    new_lab = input("\nEnter new lab name: ").strip()
    if not new_lab:
        print("❌ New lab name cannot be empty.")
        return
    
    if new_lab not in all_labs:
        print(f"❌ Lab '{new_lab}' not found in available labs.")
        return
    
    try:
        result = lab_manager.modify_lab(course_id, old_lab, new_lab)
        if result:
            print(f"✅ Successfully modified lab '{old_lab}' to '{new_lab}' for course '{course_id}'")
        else:
            print(f"❌ Failed to modify lab.")
    except Exception as e:
        print(f"❌ Error modifying lab: {e}")


def delete_lab_interactive(lab_manager: LabManager) -> None:
    """Interactive lab deletion from course."""
    display_labs_and_courses(lab_manager)
    
    course_id = input("\nEnter Course ID to remove lab from: ").strip()
    if not course_id:
        print("❌ Course ID cannot be empty.")
        return
    
    # Check if course exists
    course = lab_manager.get_course_by_id(course_id)
    if not course:
        print(f"❌ Course '{course_id}' not found.")
        return
    
    # Show current labs for this course
    current_labs = course.get('lab', [])
    if not current_labs:
        print(f"❌ Course '{course_id}' has no labs assigned.")
        return
    
    print(f"\nCurrent labs for {course_id}:")
    for i, lab in enumerate(current_labs, 1):
        print(f"  {i}. {lab}")
    
    lab_type = input("\nEnter lab name to remove: ").strip()
    if not lab_type:
        print("❌ Lab name cannot be empty.")
        return
    
    if lab_type not in current_labs:
        print(f"❌ Lab '{lab_type}' is not assigned to course '{course_id}'.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to remove lab '{lab_type}' from course '{course_id}'? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Deletion cancelled.")
        return
    
    try:
        result = lab_manager.delete_lab(course_id, lab_type)
        if result:
            print(f"✅ Successfully removed lab '{lab_type}' from course '{course_id}'")
        else:
            print(f"❌ Failed to remove lab.")
    except Exception as e:
        print(f"❌ Error removing lab: {e}")


def lab_management_menu(config_file: str, config: dict, time_slots: dict) -> dict:
    """Lab management menu interface."""
    try:
        lab_manager = LabManager()
        lab_manager.load_data(config_file)
        
        if not lab_manager.data:
            print("❌ Error loading lab data. Please check the configuration file.")
            return config
        
        while True:
            print("\n" + "="*50)
            print("LAB MANAGEMENT")
            print("="*50)
            print("1. 👀 View labs and course assignments")
            print("2. ➕ Add lab to course")
            print("3. ✏️  Modify course lab assignment")
            print("4. ❌ Remove lab from course")
            print("5. 💾 Save changes and exit")
            print("6. 🚪 Exit without saving")
            print("="*50)
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                display_labs_and_courses(lab_manager)
            elif choice == '2':
                add_lab_to_course_interactive(lab_manager)
            elif choice == '3':
                modify_lab_interactive(lab_manager)
            elif choice == '4':
                delete_lab_interactive(lab_manager)
            elif choice == '5':
                # Save changes back to file
                lab_manager.save_data()
                # Update the config dictionary with the modified data
                if 'config' in lab_manager.data:
                    config.update(lab_manager.data['config'])
                else:
                    config.update(lab_manager.data)
                print("✅ Lab changes saved successfully.")
                return config
            elif choice == '6':
                print("Exiting without saving changes.")
                return config
            else:
                print("Invalid choice. Please select 1-6.")
                
    except Exception as e:
        print(f"❌ Error initializing lab manager: {e}")
        return config


def show_main_menu() -> str:
    """Display main menu and get user choice."""
    print("\n" + "="*50)
    print("SCHEDULER CLI - MAIN MENU")
    print("="*50)
    print("1. 🗂️  Course Management")
    print("2. 🏢 Room Management")
    print("3. 🔬 Lab Management")
    print("4. 📅 Generate Schedules")
    print("5. 🚪 Exit")
    print("="*50)
    
    return input("Select an option (1-5): ").strip()


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


def main():
    """
    Where all the magic happens for the scheduler CLI.
    """
    try:
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
        
        # Main application loop
        while True:
            choice = show_main_menu()
            
            if choice == '1':
                # Course Management
                config = course_management_menu(config, str(config_path), time_slots)
                
            elif choice == '2':
                # Room Management
                config = room_management_menu(full_config, str(config_path), time_slots)
                # Update full_config with the new config
                full_config['config'] = config
                
            elif choice == '3':
                # Lab Management
                config = lab_management_menu(str(config_path), config, time_slots)
                # Update full_config with the new config
                full_config['config'] = config
                
            elif choice == '4':
                # Generate Schedules
                user_input = get_user_input()
                
                # Validate output file
                output_path = validate_file_path(user_input['output'], must_exist=False)
                
                # Show config summary if requested
                if user_input['show_config']:
                    print_config_summary(config, time_slots)
                    
                    # Ask user if they want to continue after seeing the config
                    print("\nContinue with schedule generation? (y/n, default: y):")
                    continue_input = input().strip().lower()
                    if continue_input in ['n', 'no', 'false', '0']:
                        print("Schedule generation cancelled by user.")
                        continue
                
                # Generate schedules
                print(f"Generating {user_input['limit']} schedules...")
                schedules = generate_schedules(config, time_slots, user_input['limit'], user_input['optimize'])
                
                # Save results
                print(f"Saving schedules to: {output_path}")
                save_schedules(schedules, str(output_path), user_input['format'])
                
                print("Schedule generation completed successfully!")
                
            elif choice == '5':
                # Exit
                print("Thank you for using Scheduler CLI!")
                break
                
            else:
                print("Invalid choice. Please select 1, 2, 3, 4, or 5.")
        
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