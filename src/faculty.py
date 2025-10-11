"""Faculty manager for course scheduling system."""

from typing import Dict, Any, List


class FacultyManager:
	def __init__(self, config: Dict[str, Any]):
		"""
		Initialize with a config dictionary 
		"""
		self.config = config
		
		if 'config' not in self.config:
			raise ValueError("Config dictionary must have a 'config' key.")
		
		if 'faculty' not in self.config['config']:
			self.config['config']['faculty'] = []

	# ...existing code...

	def get_faculty(self) -> List[Dict[str, Any]]:
		"""Return a shallow copy of the faculty list."""
		return [dict(f) for f in self.config['config'].get('faculty', [])]

	def add_faculty(self, faculty: Dict[str, Any]) -> bool:
		"""
		Adds a faculty if valid
		"""
		
		entry = dict(faculty)
		self._apply_defaults(entry)
		
		self._validate_faculty_entry(entry)

		name = entry['name']
		faculty_list = self.config['config'].setdefault('faculty', [])
		if not isinstance(faculty_list, list):
			raise TypeError("'faculty' in config must be a list")

		if any(f.get('name') == name for f in faculty_list):
			return False

		faculty_list.append(entry)
		return True

	def delete_faculty(self, name: str) -> bool:
		"""
		Deletes faculty by name, removes references in courses
		"""
		faculty_list = self.config['config'].get('faculty', [])
		# find the faculty entry by name
		idx = next((i for i, f in enumerate(faculty_list) if f.get('name') == name), None)
		if idx is None:
			return False

		# remove faculty
		del faculty_list[idx]

		# remove name from any course['faculty'] lists
		self._remove_faculty_references(name)

		return True

	def edit_faculty(self, name: str, new_data: Dict[str, Any]) -> bool:
		"""
		Edit faculty identified by 'name'
		"""
		faculty_list = self.config['config'].get('faculty', [])
		idx = next((i for i, f in enumerate(faculty_list) if f.get('name') == name), None)
		if idx is None:
			return False

		# If renaming, ensure new name doesn't already exist (unless same)
		new_name = new_data.get('name')
		if new_name and new_name != name and any(f.get('name') == new_name for f in faculty_list):
			return False

		# Validate merged entry
		merged = dict(faculty_list[idx])
		merged.update(new_data)
		self._apply_defaults(merged)
		self._validate_faculty_entry(merged)

		# Save
		faculty_list[idx] = merged

		# If the name changed, update course references
		if new_name and new_name != name:
			self._rename_faculty_references(name, new_name)

		return True

	def set_faculty(self, new_faculty: List[Dict[str, Any]]) -> Dict[str, List[str]]:
		"""
		Replace the entire faculty list with `new_faculty`. Validates
		"""
		if not isinstance(new_faculty, list) or not all(isinstance(f, dict) for f in new_faculty):
			raise TypeError('new_faculty must be a list of dictionaries')

		names = [f.get('name') for f in new_faculty]
		if any(not isinstance(n, str) or not n for n in names):
			raise ValueError('each faculty entry must have a non-empty string "name"')
		if len(names) != len(set(names)):
			raise ValueError('faculty names must be unique')

		# Validate all entries
		for f in new_faculty:
			entry = dict(f)
			self._apply_defaults(entry)
			self._validate_faculty_entry(entry)

		old_names = {f.get('name') for f in self.config['config'].get('faculty', [])}
		new_names = set(names)

		# Replace; make copies and apply defaults
		self.config['config']['faculty'] = []
		for f in new_faculty:
			entry = dict(f)
			self._apply_defaults(entry)
			self.config['config']['faculty'].append(entry)

		# Remove instructor references for removed faculty
		removed = old_names - new_names
		# remove references from course faculty lists
		for name in removed:
			self._remove_faculty_references(name)

		return {
			'added': sorted(list(new_names - old_names)),
			'removed': sorted(list(removed)),
		}

	def _remove_faculty_references(self, name: str) -> int:
		"""Remove `name` from all course['faculty'] lists. Returns total removed count."""
		total_removed = 0
		for course in self.config['config'].get('courses', []):
			fac = course.get('faculty')
			if isinstance(fac, list):
				removed_count = sum(1 for f in fac if f == name)
				if removed_count:
					course['faculty'] = [f for f in fac if f != name]
					total_removed += removed_count
		return total_removed

	def _rename_faculty_references(self, old: str, new: str) -> int:
		"""Rename `old` to `new` in all course['faculty'] lists. Returns replacements count."""
		total_replaced = 0
		for course in self.config['config'].get('courses', []):
			fac = course.get('faculty')
			if isinstance(fac, list):
				replaced = [new if f == old else f for f in fac]
				count = sum(1 for a, b in zip(fac, replaced) if a != b)
				if count:
					course['faculty'] = replaced
					total_replaced += count
		return total_replaced

	def _validate_faculty_entry(self, faculty: Dict[str, Any]):
		"""Validates faculty, raises error if needed
		"""
		if not isinstance(faculty, dict):
			raise TypeError('faculty entry must be a dict')

		name = faculty.get('name')
		if not isinstance(name, str) or not name:
			raise ValueError('faculty entry must include a non-empty "name" string')

		# Required numeric fields
		for key in ('maximum_credits', 'minimum_credits', 'unique_course_limit'):
			if key not in faculty or not isinstance(faculty[key], int):
				raise TypeError(f'"{key}" is required and must be an int')

		# times: expect a dict mapping day abbreviations to list of strings
		times = faculty.get('times')
		if times is not None:
			if not isinstance(times, dict):
				raise TypeError('"times" must be a dict mapping day->list of time ranges')
			for day, ranges in times.items():
				if not isinstance(day, str):
					raise TypeError('day keys in "times" must be strings')
				if not isinstance(ranges, list) or not all(isinstance(r, str) for r in ranges):
					raise TypeError('each value in "times" must be a list of strings like "09:00-17:00"')

		# preference dictionaries (optional) must be dict[str,int]
		for pref_key in ('course_preferences', 'room_preferences', 'lab_preferences'):
			if pref_key in faculty:
				if not isinstance(faculty[pref_key], dict):
					raise TypeError(f'"{pref_key}" must be a dict mapping item->weight')
				for k, v in faculty[pref_key].items():
					if not isinstance(k, str) or not isinstance(v, int):
						raise TypeError(f'entries in "{pref_key}" must map string->int')

		# Ensure minimum_credits not greater than maximum_credits
		if faculty.get('minimum_credits') is not None and faculty.get('maximum_credits') is not None:
			if faculty['minimum_credits'] > faculty['maximum_credits']:
				raise ValueError('"minimum_credits" cannot be greater than "maximum_credits"')

		# Validate room and lab preferences reference existing rooms/labs in config
		existing_rooms = set(self.config['config'].get('rooms', []))
		existing_labs = set(self.config['config'].get('labs', []))
		invalid_rooms = [k for k in faculty.get('room_preferences', {}) if k not in existing_rooms]
		if invalid_rooms:
			raise ValueError(f'room_preferences reference unknown rooms: {invalid_rooms}')
		invalid_labs = [k for k in faculty.get('lab_preferences', {}) if k not in existing_labs]
		if invalid_labs:
			raise ValueError(f'lab_preferences reference unknown labs: {invalid_labs}')

	def _apply_defaults(self, faculty: Dict[str, Any]):
		#Applies Defaults 

		numeric_defaults = {
			'maximum_credits': 9,
			'minimum_credits': 0,
			'unique_course_limit': 1,
		}
		for k, v in numeric_defaults.items():
			if k not in faculty:
				faculty[k] = v

		# Ensure preference dicts exist
		for pref_key in ('course_preferences', 'room_preferences', 'lab_preferences'):
			faculty.setdefault(pref_key, {})

		# Default times to M-F 09:00-17:00 if missing or empty
		if not faculty.get('times'):
			default_times = {d: ['09:00-17:00'] for d in ('MON', 'TUE', 'WED', 'THU', 'FRI')}
			faculty['times'] = default_times

	def display_faculty(self) -> None:
		"""Display all faculty members in a formatted list."""
		print("\n" + "="*60)
		print("FACULTY LIST")
		print("="*60)
		
		faculty_list = self.get_faculty()
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
		for course in self.config['config'].get('courses', []):
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
		available_rooms = self.config['config'].get('rooms', [])
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
		available_labs = self.config['config'].get('labs', [])
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
		"""Interactive faculty addition."""
		try:
			faculty_data = self.get_faculty_input()
			if self.add_faculty(faculty_data):
				print(f"✅ Successfully added faculty: {faculty_data['name']}")
			else:
				print(f"❌ Faculty '{faculty_data['name']}' already exists.")
		except Exception as e:
			print(f"❌ Error adding faculty: {e}")

	def edit_faculty_interactive(self) -> None:
		"""Interactive faculty editing."""
		self.display_faculty()
		
		faculty_list = self.get_faculty()
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
			if self.edit_faculty(name, new_data):
				print(f"✅ Successfully updated faculty: {name}")
				if new_name != name:
					print(f"📝 Note: All course references have been updated to use new name '{new_name}'")
			else:
				print(f"❌ Failed to update faculty. Name may already exist.")
		except Exception as e:
			print(f"❌ Error editing faculty: {e}")

	def delete_faculty_interactive(self) -> None:
		"""Interactive faculty deletion with impact analysis."""
		self.display_faculty()
		
		faculty_list = self.get_faculty()
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
		config = self.config.get('config', {})
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
				if self.delete_faculty(name):
					print(f"✅ Successfully deleted faculty: {name}")
					if affected_courses:
						print("📝 Note: All course references have been automatically removed.")
				else:
					print(f"❌ Failed to delete faculty '{name}'.")
			except Exception as e:
				print(f"❌ Error deleting faculty: {e}")
		else:
			print("Deletion cancelled.")

	def faculty_management_menu(self, config_file: str, time_slots: dict) -> dict:
		"""Faculty management menu interface."""
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
					# Save changes back to full config
					from main import save_config_to_file
					save_config_to_file(self.config['config'], time_slots, config_file)
					return self.config['config']
				elif choice == '6':
					print("Exiting without saving changes.")
					return self.config['config']
				else:
					print("Invalid choice. Please select 1-6.")
					
		except Exception as e:
			print(f"❌ Error in faculty management: {e}")
			return self.config.get('config', {})


