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


