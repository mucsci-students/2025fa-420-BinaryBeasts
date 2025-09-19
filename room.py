# RoomManager: Add, delete, and edit rooms in a config dictionary
from typing import Dict, Any, List

class RoomManager:
	def __init__(self, config: Dict[str, Any]):
		"""
		Initialize with a config dictionary (should have a 'rooms' key under 'config').
		"""
		self.config = config
		if 'config' not in self.config:
			raise ValueError("Config dictionary must have a 'config' key.")
		if 'rooms' not in self.config['config']:
			self.config['config']['rooms'] = []

	def get_rooms(self) -> List[str]:
		"""Return a copy of the list of rooms."""
		return list(self.config['config'].get('rooms', []))

	def add_room(self, room_name: str) -> bool:
		"""Add a room if it does not already exist. Returns True if added, False if already present."""
		rooms = self.config['config'].setdefault('rooms', [])
		if room_name in rooms:
			return False
		rooms.append(room_name)
		return True

	def delete_room(self, room_name: str) -> bool:
		"""Delete a room if it exists. Returns True if deleted, False if not found."""
		rooms = self.config['config'].get('rooms', [])
		if room_name in rooms:
			rooms.remove(room_name)
			return True
		return False

	def edit_room(self, old_name: str, new_name: str) -> bool:
		"""Rename a room. Returns True if successful, False if old_name not found or new_name exists."""
		rooms = self.config['config'].get('rooms', [])
		if old_name not in rooms or new_name in rooms:   
			return False
		idx = rooms.index(old_name)
		rooms[idx] = new_name
		#update room references in courses and faculty preferences
		self._update_room_references(old_name, new_name)
		return True

	def set_rooms(self, new_rooms: List[str]) -> dict:
		"""
		Replace the rooms list with `new_rooms`.
		Returns a report dict: {'added': [...], 'removed': [...]}.
		Raises TypeError/ValueError for invalid input.
		"""

		"""
		Checks that new_rooms is a proper list of strings by checking if new_rooms is a list, and that all values in new_rooms are strings.
		"""
		# Validate type
		if not isinstance(new_rooms, list) or not all(isinstance(r, str) for r in new_rooms):
			raise TypeError("new_rooms must be a list of strings")

		"""
		Checks the length of new_rooms and then turns it to a set and checks that length to make sure all values are unique.
		"""
		# Validate uniqueness
		if len(new_rooms) != len(set(new_rooms)):
			raise ValueError("room names must be unique")

		old_rooms = set(self.config['config'].get('rooms', []))
		new_set = set(new_rooms)

		# Replace rooms list
		self.config['config']['rooms'] = list(new_rooms)

		# Remove references in courses that point to removed rooms
		for course in self.config['config'].get('courses', []):
			if 'room' in course and isinstance(course['room'], list):
				course['room'] = [r for r in course['room'] if r in new_set]

		# Remove room preferences for removed rooms in faculty
		removed = old_rooms - new_set
		for faculty in self.config['config'].get('faculty', []):
			prefs = faculty.get('room_preferences')
			if isinstance(prefs, dict):
				for rm in list(removed):
					prefs.pop(rm, None)

		return {
			'added': sorted(list(new_set - old_rooms)),
			'removed': sorted(list(removed)),
		}

	def _update_room_references(self, old_name: str, new_name: str):
		# Update room references in courses
		for course in self.config['config'].get('courses', []):
			if 'room' in course and isinstance(course['room'], list):
				course['room'] = [new_name if r == old_name else r for r in course['room']]  
		# Update room preferences in faculty
		for faculty in self.config['config'].get('faculty', []):
			if 'room_preferences' in faculty and isinstance(faculty['room_preferences'], dict):
				if old_name in faculty['room_preferences']:
					faculty['room_preferences'][new_name] = faculty['room_preferences'].pop(old_name)
