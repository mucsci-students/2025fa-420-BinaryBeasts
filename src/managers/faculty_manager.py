"""Faculty manager for course scheduling system."""

from typing import Dict, Any, List

from scheduler.config import CombinedConfig, FacultyConfig

class FacultyManager:
	def __init__(self, combined_config: CombinedConfig):
		"""
		Initialize with a config dictionary 
		"""
		self.combined_config = combined_config
		self.config = combined_config.config
		self.faculty = self.config.faculty 
		self.courses = self.config.courses
		self.rooms = self.config.rooms
		self.labs = self.config.labs

	def get_faculty(self) -> List[Dict[str, Any]]:
		"""Return a shallow copy of the faculty list."""
		return [f.dict() for f in self.faculty]

	def get_courses(self) -> List[str]:
		"""Return a shallow copy of the courses list."""
		return [c.course_id for c in self.courses]

	def get_rooms(self) -> List[str]:
		"""Return a shallow copy of the rooms list."""
		return [r for r in self.rooms]

	def get_labs(self) -> List[str]:
		"""Return a shallow copy of the labs list."""
		return [l for l in self.labs]

	def add_faculty(self, faculty: Dict[str, Any]) -> bool:
		"""
		Adds a faculty if valid
		"""
		#** unpacks the dict into keyword args for FacultyConfig
		entry = FacultyConfig(**faculty)
		
		self._validate_faculty_entry(entry)

		self.faculty.append(entry)

		return True

	def delete_faculty(self, name: str) -> bool:
		"""
		Deletes faculty by name, removes references in courses
		"""
		for f in self.faculty:
			if f.name == name:
				self.faculty.remove(f)
				break

		# remove name from any course['faculty'] lists
		self._remove_faculty_references(name)

		return True

	def edit_faculty(self, name: str, new_data: Dict[str, Any]) -> bool:
		"""
		Edit faculty identified by 'name'
		"""
		for f in self.faculty:
			if f.name == name:
				old_name = f.name
				f = FacultyConfig(**new_data)
				self._validate_faculty_entry(f)
				if f.name != old_name:
					self._rename_faculty_references(old_name, f.name)
				return True

		return False

	def set_faculty(self, new_faculty: List[Dict[str, Any]]) -> Dict[str, List[str]]:
		"""
		Replace the entire faculty list with `new_faculty`. Validates
		"""
		faculty_list = List[FacultyConfig]()
		for dict in new_faculty:
			faculty_list.append(FacultyConfig(**dict))

		old_names = set()
		for f in self.faculty:
			old_names.add(f.name)

		#might cause issues later, implement edit mode here to roll back changes on validatiion error
		self.faculty = faculty_list

		new_names = set()
		for f in self.faculty:
			self._validate_faculty_entry(f)
			new_names.add(f.name)

		# Remove instructor references for removed faculty
		removed = old_names - new_names
		for name in removed:
			self._remove_faculty_references(name)

		return {
			'added': sorted(list(new_names - old_names)),
			'removed': sorted(list(removed)),
		}

	def _remove_faculty_references(self, name: str) -> int:
		"""Remove `name` from all course['faculty'] lists. Returns total removed count."""
		total_removed = 0
		for course in self.courses:
			fac = course.faculty
			for f in fac:
				if f == name:
					fac.remove(f)
					total_removed += 1
		return total_removed

	def _rename_faculty_references(self, old: str, new: str) -> int:
		"""Rename `old` to `new` in all course['faculty'] lists. Returns replacements count."""
		total_replaced = 0
		for course in self.courses:
			fac = course.faculty
			for f in fac:
				if f == old:
					f = new
					total_replaced += 1
		return total_replaced

	def _validate_faculty_entry(self, faculty: FacultyConfig):
		"""Extra Validation for faculty(FacultyConfig already automatically validates), raises error if needed
		"""
		if not isinstance(faculty, FacultyConfig):
			raise TypeError('faculty entry must be a FacultyConfig')

		name = faculty.name
		if not isinstance(name, str) or name == '':
			raise ValueError('faculty entry must include a non-empty "name" string')

		if any(f.name == name for f in self.faculty):
			raise ValueError(f'faculty with name "{name}" already exists')

		# Validate room and lab preferences reference existing rooms/labs in config
		existing_rooms = self.config.rooms
		existing_labs = self.config.labs
		room_prefs = faculty.room_preferences
		lab_prefs = faculty.lab_preferences

		invalid_rooms = [k for k in room_prefs if k not in existing_rooms]
		if invalid_rooms:
			raise ValueError(f'room_preferences reference unknown rooms: {invalid_rooms}')
		invalid_labs = [k for k in lab_prefs if k not in existing_labs]
		if invalid_labs:
			raise ValueError(f'lab_preferences reference unknown labs: {invalid_labs}')




