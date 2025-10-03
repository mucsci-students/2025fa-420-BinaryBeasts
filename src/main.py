#!/usr/bin/env python3
"""
Scheduler CLI Application
Command-line tool for generating and optimizing schedules.
"""
import sys
import json
from pathlib import Path
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig
from saveConfigFile import save_config_file
from courses import CourseManager
from room import RoomManager
from lab_manager import LabManager
from faculty import FacultyManager
from main_gui import MainGUI
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
"""
Can cut \/\/\/\/\/\/
"""
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


"""
Can cut \/\/\/\/\/\/
"""






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



"""
Andrews features can be moved to course class
"""
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

"""
Andrews features can be moved to course class
"""
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

"""
Andrews features can be moved to course class
"""
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

"""
Andrews features can be moved to course class
"""
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

"""
Andrews features can be moved to course class
"""
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

"""
Naomis features can be moved to course class
"""

"""
Patricks features can be moved to course class
"""
def display_faculty(faculty_manager: FacultyManager) -> None:
    """Display all faculty members in a formatted list."""
    print("\n" + "="*60)
    print("FACULTY LIST")
    print("="*60)
    
    faculty_list = faculty_manager.get_faculty()
    if not faculty_list:
        print("No faculty found.")
        return
    
    print(f"👥 Total Faculty: {len(faculty_list)}")
    print("-" * 60)
    
    for i, member in enumerate(faculty_list, 1):
        name = member.get('name', 'Unknown')
        min_credits = member.get('minimum_credits', 0)
        max_credits = member.get('maximum_credits', 0)
        unique_limit = member.get('unique_course_limit', 'N/A')
        
        print(f"\n{i:3}. 👤 {name}")
        print(f"      📊 Credit range: {min_credits}-{max_credits}")
        print(f"      📚 Max unique courses: {unique_limit}")
        
        # Show availability
        times = member.get('times', {})
        available_days = [day for day, slots in times.items() if slots]
        print(f"      📅 Available days: {', '.join(available_days) or 'None'}")
        
        # Show course preferences
        course_prefs = member.get('course_preferences', {})
        if course_prefs:
            top_courses = sorted(course_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      ⭐ Preferred courses: {', '.join([f'{c}({p})' for c, p in top_courses])}")
        else:
            print(f"      ⭐ Preferred courses: None")
        
        # Show room preferences
        room_prefs = member.get('room_preferences', {})
        if room_prefs:
            top_rooms = sorted(room_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      🏢 Preferred rooms: {', '.join([f'{r}({p})' for r, p in top_rooms])}")
        else:
            print(f"      🏢 Preferred rooms: None")
        
        # Show lab preferences
        lab_prefs = member.get('lab_preferences', {})
        if lab_prefs:
            top_labs = sorted(lab_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      🔬 Preferred labs: {', '.join([f'{l}({p})' for l, p in top_labs])}")
        else:
            print(f"      🔬 Preferred labs: None")
    
    print("="*60)

"""
Patricks features can be moved to course class
"""
def get_faculty_input(config: dict) -> dict:
    """Get faculty information from user input."""
    print("\n🆕 ADD NEW FACULTY")
    print("=" * 30)
    
    name = input("Faculty name (e.g., Dr. Smith): ").strip()
    if not name:
        raise ValueError("Faculty name cannot be empty")
    
    # Get credit limits
    while True:
        try:
            min_credits = int(input("Minimum credits (0-20): ").strip())
            if min_credits < 0 or min_credits > 20:
                print("Error: Minimum credits must be between 0 and 20")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number for minimum credits")
    
    while True:
        try:
            max_credits = int(input("Maximum credits (0-20): ").strip())
            if max_credits < min_credits or max_credits > 20:
                print(f"Error: Maximum credits must be between {min_credits} and 20")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number for maximum credits")
    
    while True:
        try:
            unique_limit = int(input("Unique course limit (1-10): ").strip())
            if unique_limit < 1 or unique_limit > 10:
                print("Error: Unique course limit must be between 1 and 10")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number for unique course limit")
    
    # Get availability times
    print("\nAvailability times (format: HH:MM-HH:MM, press Enter to skip day):")
    times = {}
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    for day in days:
        time_input = input(f"  {day} (e.g., 09:00-17:00): ").strip()
        if time_input:
            times[day] = [time_input]
        else:
            times[day] = []
    
    # Get course preferences
    available_courses = set()
    for course in config.get('courses', []):
        course_id = course.get('course_id')
        if course_id:
            available_courses.add(course_id)
    
    print(f"\nCourse preferences (available courses: {', '.join(sorted(available_courses))})")
    print("Format: CourseID:preference (1-5), press Enter to finish:")
    course_preferences = {}
    while True:
        pref_input = input(f"  Course preference {len(course_preferences)+1} (or Enter to finish): ").strip()
        if not pref_input:
            break
        try:
            course_id, pref_str = pref_input.split(':')
            course_id = course_id.strip()
            preference = int(pref_str.strip())
            if preference < 1 or preference > 5:
                print("Error: Preference must be between 1 and 5")
                continue
            if course_id in available_courses:
                course_preferences[course_id] = preference
            else:
                print(f"Warning: Course '{course_id}' not found in available courses")
        except ValueError:
            print("Error: Format should be CourseID:preference (e.g., CMSC140:5)")
    
    # Get room preferences
    available_rooms = config.get('rooms', [])
    print(f"\nRoom preferences (available rooms: {', '.join(available_rooms)})")
    print("Format: RoomName:preference (1-5), press Enter to finish:")
    room_preferences = {}
    while True:
        pref_input = input(f"  Room preference {len(room_preferences)+1} (or Enter to finish): ").strip()
        if not pref_input:
            break
        try:
            room_name, pref_str = pref_input.split(':')
            room_name = room_name.strip()
            preference = int(pref_str.strip())
            if preference < 1 or preference > 5:
                print("Error: Preference must be between 1 and 5")
                continue
            if room_name in available_rooms:
                room_preferences[room_name] = preference
            else:
                print(f"Warning: Room '{room_name}' not found in available rooms")
        except ValueError:
            print("Error: Format should be RoomName:preference (e.g., Roddy136:5)")
    
    # Get lab preferences
    available_labs = config.get('labs', [])
    print(f"\nLab preferences (available labs: {', '.join(available_labs)})")
    print("Format: LabName:preference (1-5), press Enter to finish:")
    lab_preferences = {}
    while True:
        pref_input = input(f"  Lab preference {len(lab_preferences)+1} (or Enter to finish): ").strip()
        if not pref_input:
            break
        try:
            lab_name, pref_str = pref_input.split(':')
            lab_name = lab_name.strip()
            preference = int(pref_str.strip())
            if preference < 1 or preference > 5:
                print("Error: Preference must be between 1 and 5")
                continue
            if lab_name in available_labs:
                lab_preferences[lab_name] = preference
            else:
                print(f"Warning: Lab '{lab_name}' not found in available labs")
        except ValueError:
            print("Error: Format should be LabName:preference (e.g., Linux:5)")
    
    return {
        'name': name,
        'minimum_credits': min_credits,
        'maximum_credits': max_credits,
        'unique_course_limit': unique_limit,
        'times': times,
        'course_preferences': course_preferences,
        'room_preferences': room_preferences,
        'lab_preferences': lab_preferences
    }

"""
Patricks features can be moved to course class
"""
def add_faculty_interactive(faculty_manager: FacultyManager, config: dict) -> None:
    """Interactive faculty addition."""
    try:
        faculty_data = get_faculty_input(config)
        if faculty_manager.add_faculty(faculty_data):
            print(f"✅ Successfully added faculty: {faculty_data['name']}")
        else:
            print(f"❌ Faculty '{faculty_data['name']}' already exists.")
    except Exception as e:
        print(f"❌ Error adding faculty: {e}")

"""
Patricks features can be moved to course class
"""
def edit_faculty_interactive(faculty_manager: FacultyManager, config: dict) -> None:
    """Interactive faculty editing."""
    display_faculty(faculty_manager)
    
    faculty_list = faculty_manager.get_faculty()
    if not faculty_list:
        print("❌ No faculty available to edit.")
        return
    
    name = input("\nEnter faculty name to edit: ").strip()
    if not name:
        print("❌ Faculty name cannot be empty.")
        return
    
    # Check if faculty exists
    if not any(f.get('name') == name for f in faculty_list):
        print(f"❌ Faculty '{name}' not found.")
        return
    
    print(f"\n📝 EDITING: {name}")
    print("Enter new values (press Enter to keep current value):")
    
    # Get current faculty data
    current_faculty = next(f for f in faculty_list if f.get('name') == name)
    
    # Get new name (optional)
    new_name = input(f"New name (current: {name}): ").strip()
    if not new_name:
        new_name = name
    
    # Get new credit limits (optional)
    min_credits_input = input(f"New minimum credits (current: {current_faculty.get('minimum_credits', 0)}): ").strip()
    min_credits = int(min_credits_input) if min_credits_input else current_faculty.get('minimum_credits', 0)
    
    max_credits_input = input(f"New maximum credits (current: {current_faculty.get('maximum_credits', 0)}): ").strip()
    max_credits = int(max_credits_input) if max_credits_input else current_faculty.get('maximum_credits', 0)
    
    unique_limit_input = input(f"New unique course limit (current: {current_faculty.get('unique_course_limit', 1)}): ").strip()
    unique_limit = int(unique_limit_input) if unique_limit_input else current_faculty.get('unique_course_limit', 1)
    
    new_data = {
        'name': new_name,
        'minimum_credits': min_credits,
        'maximum_credits': max_credits,
        'unique_course_limit': unique_limit
    }
    
    # Ask if they want to update preferences
    update_prefs = input("Update preferences? (y/n, default: n): ").strip().lower()
    if update_prefs in ['y', 'yes']:
        print("Note: Complete faculty preference update - enter all preferences you want to keep:")
        try:
            faculty_data = get_faculty_input(config)
            new_data.update({
                'times': faculty_data['times'],
                'course_preferences': faculty_data['course_preferences'],
                'room_preferences': faculty_data['room_preferences'],
                'lab_preferences': faculty_data['lab_preferences']
            })
        except Exception as e:
            print(f"❌ Error getting preferences: {e}")
            return
    
    try:
        if faculty_manager.edit_faculty(name, new_data):
            print(f"✅ Successfully updated faculty: {name}")
            if new_name != name:
                print(f"📝 Note: All course references have been updated to use new name '{new_name}'")
        else:
            print(f"❌ Failed to update faculty. Name may already exist.")
    except Exception as e:
        print(f"❌ Error editing faculty: {e}")

"""
Patricks features can be moved to course class
"""
def delete_faculty_interactive(faculty_manager: FacultyManager) -> None:
    """Interactive faculty deletion with impact analysis."""
    display_faculty(faculty_manager)
    
    faculty_list = faculty_manager.get_faculty()
    if not faculty_list:
        print("❌ No faculty available to delete.")
        return
    
    name = input("\nEnter faculty name to delete: ").strip()
    if not name:
        print("❌ Faculty name cannot be empty.")
        return
    
    # Check if faculty exists
    if not any(f.get('name') == name for f in faculty_list):
        print(f"❌ Faculty '{name}' not found.")
        return
    
    # Analyze impact of deletion
    print(f"\n🔍 ANALYZING IMPACT OF DELETING '{name}':")
    print("-" * 50)
    
    # Check courses assigned to this faculty
    affected_courses = []
    config = faculty_manager.config.get('config', {})
    for course in config.get('courses', []):
        if 'faculty' in course and isinstance(course['faculty'], list):
            if name in course['faculty']:
                affected_courses.append(course.get('course_id', 'Unknown'))
    
    if affected_courses:
        print(f"📚 Courses assigned to this faculty ({len(affected_courses)}):")
        for course in affected_courses:
            print(f"   • {course}")
    else:
        print("✅ No courses currently assigned to this faculty.")
    
    if affected_courses:
        print("\n⚠️  Warning: Deleting this faculty member will:")
        print(f"   • Remove faculty assignment from {len(affected_courses)} course(s)")
    
    # Confirm deletion
    confirm = input(f"\nAre you sure you want to delete faculty '{name}'? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        try:
            if faculty_manager.delete_faculty(name):
                print(f"✅ Successfully deleted faculty: {name}")
                if affected_courses:
                    print("📝 Note: All course references have been automatically removed.")
            else:
                print(f"❌ Failed to delete faculty '{name}'.")
        except Exception as e:
            print(f"❌ Error deleting faculty: {e}")
    else:
        print("Deletion cancelled.")

"""
Patricks features can be moved to course class
"""
def faculty_management_menu(full_config: dict, config_file: str, time_slots: dict) -> dict:
    """Faculty management menu interface."""
    try:
        # FacultyManager expects the full structure with 'config' key
        faculty_manager = FacultyManager(full_config)
        config = full_config.get('config', {})
        
        while True:
            print("\n" + "="*50)
            print("FACULTY MANAGEMENT")
            print("="*50)
            print("1. 👀 View all faculty")
            print("2. ➕ Add new faculty")
            print("3. ✏️ Edit faculty")
            print("4. ❌ Delete faculty")
            print("5. 💾 Save changes and exit")
            print("6. 🚪 Exit without saving")
            print("="*50)
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                display_faculty(faculty_manager)
            elif choice == '2':
                add_faculty_interactive(faculty_manager, config)
            elif choice == '3':
                edit_faculty_interactive(faculty_manager, config)
            elif choice == '4':
                delete_faculty_interactive(faculty_manager)
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
        print(f"❌ Error initializing faculty manager: {e}")
        return full_config.get('config', {})


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
    
    # Main application loop
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            # Course Management
            course_manager = CourseManager()
            config = course_manager.course_management_menu(config, str(config_path), time_slots)
            
        elif choice == '2':
            # Room Management
            config = room_management_menu(full_config, str(config_path), time_slots)
            # Update full_config with the new config
            full_config['config'] = config
            
        elif choice == '3':
            # Lab Management
            lab_manager = LabManager()
            config = lab_manager.lab_management_menu(str(config_path), config, time_slots)
            # Update full_config with the new config
            full_config['config'] = config
            
        elif choice == '4':
            # Faculty Management
            config = faculty_management_menu(full_config, str(config_path), time_slots)
            # Update full_config with the new config
            full_config['config'] = config
            
        elif choice == '5':
            # Exit
            print("Thank you for using Scheduler CLI!")
            break
            
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, or 5.")

def run_gui():
    """
    Run the GUI version of the scheduler application.
    """
    app = None
    try:
        print("🖥️ Starting GUI Application...")
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
        input("Press Enter to return to interface selection...")

def main():
    """
    Main entry point for the scheduler application.
    """
    try:
        print("Welcome to the Scheduler Application!")
        
        # Interface selection loop
        while True:
            choice = show_interface_selection()
            
            if choice == '1':
                # CLI Interface
                run_cli()
                break
            elif choice == '2':
                # GUI Interface
                run_gui()
                # Continue loop to allow interface selection again
            elif choice == '3':
                # Exit
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