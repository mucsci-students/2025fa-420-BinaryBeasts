import sys
from typing import Optional, Dict, Any

from scheduler.config import CombinedConfig, FacultyConfig
from src.controllers.faculty_controller import FacultyController

class FacultyView:
	def __init__(self, controller: FacultyController):
		self.controller = controller

	def display_faculty(self) -> None:
		"""Display all faculty members using the manager."""

		#call controller to retrieve faculty list
		faculty_list = self.controller.get_faculty()
		
		print("\n" + "="*60)
		print("FACULTY LIST")
		print("="*60)
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
			times = member.get('times', {})
			available_days = [day for day, slots in times.items() if slots]
			print(f"      📅 Available days: {', '.join(available_days) or 'None'}")
			course_prefs = member.get('course_preferences', {})
			if course_prefs:
				top_courses = sorted(course_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
				print(f"      ⭐ Preferred courses: {', '.join([f'{c}({p})' for c, p in top_courses])}")
			else:
				print(f"      ⭐ Preferred courses: None")
			room_prefs = member.get('room_preferences', {})
			if room_prefs:
				top_rooms = sorted(room_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
				print(f"      🏢 Preferred rooms: {', '.join([f'{r}({p})' for r, p in top_rooms])}")
			else:
				print(f"      🏢 Preferred rooms: None")
			lab_prefs = member.get('lab_preferences', {})
			if lab_prefs:
				top_labs = sorted(lab_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
				print(f"      🔬 Preferred labs: {', '.join([f'{l}({p})' for l, p in top_labs])}")
			else:
				print(f"      🔬 Preferred labs: None")
		print("="*60)

	def get_faculty_input(self) -> dict:
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
		# prefer controller-managed config if present
		cfg = getattr(self.controller, 'manager').config
		for course in cfg.get('config', {}).get('courses', []):
			course_id = course.get('course_id')
			if course_id:
				available_courses.add(course_id)

		print(f"\nCourse preferences (available courses: {', '.join(sorted(available_courses))})")
		print("Format: CourseID:preference (0-10), press Enter to finish:")
		course_preferences = {}
		while True:
			pref_input = input(f"  Course preference {len(course_preferences)+1} (or Enter to finish): ").strip()
			if not pref_input:
				break
			try:
				course_id, pref_str = pref_input.split(':')
				course_id = course_id.strip()
				preference = int(pref_str.strip())
				if preference < 0 or preference > 10:
					print("Error: Preference must be between 0 and 10")
					continue
				if course_id in available_courses:
					course_preferences[course_id] = preference
				else:
					print(f"Warning: Course '{course_id}' not found in available courses")
			except ValueError:
				print("Error: Format should be CourseID:preference (e.g., CMSC140:8)")

		# Get room preferences
		available_rooms = cfg.get('config', {}).get('rooms', [])
		print(f"\nRoom preferences (available rooms: {', '.join(available_rooms)})")
		print("Format: RoomName:preference (0-10), press Enter to finish:")
		room_preferences = {}
		while True:
			pref_input = input(f"  Room preference {len(room_preferences)+1} (or Enter to finish): ").strip()
			if not pref_input:
				break
			try:
				room_name, pref_str = pref_input.split(':')
				room_name = room_name.strip()
				preference = int(pref_str.strip())
				if preference < 0 or preference > 10:
					print("Error: Preference must be between 0 and 10")
					continue
				if room_name in available_rooms:
					room_preferences[room_name] = preference
				else:
					print(f"Warning: Room '{room_name}' not found in available rooms")
			except ValueError:
				print("Error: Format should be RoomName:preference (e.g., Roddy136:8)")

		# Get lab preferences
		available_labs = cfg.get('config', {}).get('labs', [])
		print(f"\nLab preferences (available labs: {', '.join(available_labs)})")
		print("Format: LabName:preference (0-10), press Enter to finish:")
		lab_preferences = {}
		while True:
			pref_input = input(f"  Lab preference {len(lab_preferences)+1} (or Enter to finish): ").strip()
			if not pref_input:
				break
			try:
				lab_name, pref_str = pref_input.split(':')
				lab_name = lab_name.strip()
				preference = int(pref_str.strip())
				if preference < 0 or preference > 10:
					print("Error: Preference must be between 0 and 10")
					continue
				if lab_name in available_labs:
					lab_preferences[lab_name] = preference
				else:
					print(f"Warning: Lab '{lab_name}' not found in available labs")
			except ValueError:
				print("Error: Format should be LabName:preference (e.g., Linux:8)")

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

	def add_faculty_interactive(self) -> None:
		try:
			faculty_data = self.get_faculty_input()
			res = None
			res = self.controller.add_faculty(faculty_data)
		except Exception as e:
			res = e
			if res is None:
				print(f"✅ Successfully added faculty: {faculty_data['name']}")
			else:
				print(f"❌ Error adding faculty: {res}")
		except Exception as e:
			print(f"❌ Error adding faculty: {e}")

	def edit_faculty_interactive(self) -> None:
		self.display_faculty()
		faculty_list = self.controller.get_faculty()
		if not faculty_list:
			print("❌ No faculty available to edit.")
			return
		name = input("\nEnter faculty name to edit: ").strip()
		if not name:
			print("❌ Faculty name cannot be empty.")
			return
		if not any(f.get('name') == name for f in faculty_list):
			print(f"❌ Faculty '{name}' not found.")
			return
		print(f"\n📝 EDITING: {name}")
		print("Enter new values (press Enter to keep current value):")
		current_faculty = next(f for f in faculty_list if f.get('name') == name)
		new_name = input(f"New name (current: {name}): ").strip() or name
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
		update_prefs = input("Update preferences? (y/n, default: n): ").strip().lower()
		if update_prefs in ['y', 'yes']:
			print("Note: Complete faculty preference update - enter all preferences you want to keep:")
			try:
				faculty_data = self.get_faculty_input()
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
			ok = False
			if self.controller and hasattr(self.controller, 'edit_faculty'):
				ok = self.controller.edit_faculty(name, new_data)
			else:
				ok = self._mgr.edit_faculty(name, new_data)
			if ok:
				print(f"✅ Successfully updated faculty: {name}")
				if new_name != name:
					print(f"📝 Note: All course references have been updated to use new name '{new_name}'")
			else:
				print(f"❌ Failed to update faculty. Name may already exist.")
		except Exception as e:
			print(f"❌ Error editing faculty: {e}")

	def delete_faculty_interactive(self) -> None:
		self.display_faculty()
		faculty_list = self.controller.get_faculty()
		if not faculty_list:
			print("❌ No faculty available to delete.")
			return
		name = input("\nEnter faculty name to delete: ").strip()
		if not name:
			print("❌ Faculty name cannot be empty.")
			return
		if not any(f.get('name') == name for f in faculty_list):
			print(f"❌ Faculty '{name}' not found.")
			return
		print(f"\n🔍 ANALYZING IMPACT OF DELETING '{name}':")
		print("-" * 50)
		affected_courses = []
		cfg = getattr(self._mgr, 'config', {})
		for course in cfg.get('config', {}).get('courses', []):
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
		confirm = input(f"\nAre you sure you want to delete faculty '{name}'? (y/N): ").strip().lower()
		if confirm in ['y', 'yes']:
			try:
				ok = False
				if self.controller and hasattr(self.controller, 'delete_faculty'):
					ok = self.controller.delete_faculty(name)
				else:
					ok = self._mgr.delete_faculty(name)
				if ok:
					print(f"✅ Successfully deleted faculty: {name}")
					if affected_courses:
						print("📝 Note: All course references have been automatically removed.")
				else:
					print(f"❌ Failed to delete faculty '{name}'.")
			except Exception as e:
				print(f"❌ Error deleting faculty: {e}")
		else:
			print("Deletion cancelled.")

	def faculty_management_menu(self, combined_config: CombinedConfig) -> dict:
		try:
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
					self.display_faculty()
				elif choice == '2':
					self.add_faculty_interactive()
				elif choice == '3':
					self.edit_faculty_interactive()
				elif choice == '4':
					self.delete_faculty_interactive()
				elif choice == '5':
					from main import save_config_to_file
					cfg = getattr(self.controller, 'manager').config
					save_config_to_file(cfg.get('config', {}), time_slots, config_file)
					return cfg.get('config', {})
				elif choice == '6':
					print("Exiting without saving changes.")
					cfg = getattr(self.controller, 'manager', getattr(self._mgr, 'config', {}))
					return cfg.get('config', {})
				else:
					print("Invalid choice. Please select 1-6.")
		except Exception as e:
			print(f"❌ Error in faculty management: {e}")
			return getattr(self._mgr, 'config', {}).get('config', {})

