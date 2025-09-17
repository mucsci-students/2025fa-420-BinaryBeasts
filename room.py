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
		"""Return the list of rooms."""
		return self.config['config'].get('rooms', [])

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
