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

	def display_rooms(self) -> None:
		"""Display all rooms in a formatted list."""
		print("\n" + "="*60)
		print("ROOM LIST")
		print("="*60)
		
		rooms = self.get_rooms()
		if not rooms:
			print("No rooms found.")
			return
		
		print(f"📍 Total Rooms: {len(rooms)}")
		print("-" * 60)
		
		for i, room in enumerate(rooms, 1):
			print(f"{i:3}. 🏢 {room}")
		
		print("="*60)

	def add_room_interactive(self) -> None:
		"""Interactive room addition."""
		print("\n🆕 ADD NEW ROOM")
		print("=" * 30)
		
		room_name = input("Room name (e.g., Roddy 101): ").strip()
		if not room_name:
			print("❌ Room name cannot be empty.")
			return
		
		try:
			if self.add_room(room_name):
				print(f"✅ Successfully added room: {room_name}")
			else:
				print(f"❌ Room '{room_name}' already exists.")
		except Exception as e:
			print(f"❌ Error adding room: {e}")

	def edit_room_interactive(self) -> None:
		"""Interactive room editing/renaming."""
		self.display_rooms()
		
		if not self.get_rooms():
			print("❌ No rooms available to edit.")
			return
		
		old_name = input("\nEnter current room name to edit: ").strip()
		if not old_name:
			print("❌ Room name cannot be empty.")
			return
		
		if old_name not in self.get_rooms():
			print(f"❌ Room '{old_name}' not found.")
			return
		
		new_name = input(f"Enter new name for '{old_name}': ").strip()
		if not new_name:
			print("❌ New room name cannot be empty.")
			return
		
		try:
			if self.edit_room(old_name, new_name):
				print(f"✅ Successfully renamed '{old_name}' to '{new_name}'")
				print("📝 Note: All course and faculty references have been updated automatically.")
			else:
				if new_name in self.get_rooms():
					print(f"❌ Room '{new_name}' already exists.")
				else:
					print(f"❌ Failed to rename room.")
		except Exception as e:
			print(f"❌ Error editing room: {e}")

	def delete_room_interactive(self) -> None:
		"""Interactive room deletion with impact analysis."""
		self.display_rooms()
		
		if not self.get_rooms():
			print("❌ No rooms available to delete.")
			return
		
		room_name = input("\nEnter room name to delete: ").strip()
		if not room_name:
			print("❌ Room name cannot be empty.")
			return
		
		if room_name not in self.get_rooms():
			print(f"❌ Room '{room_name}' not found.")
			return
		
		# Analyze impact of deletion
		print(f"\n🔍 ANALYZING IMPACT OF DELETING '{room_name}':")
		print("-" * 50)
		
		# Check courses using this room
		affected_courses = []
		config = self.config.get('config', {})
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
		confirm = input(f"\nAre you sure you want to delete '{room_name}'? (y/n): ").strip().lower()
		if confirm in ['y', 'yes']:
			try:
				if self.delete_room(room_name):
					print(f"✅ Successfully deleted room: {room_name}")
					if affected_courses or affected_faculty:
						print("📝 Note: All references have been automatically removed.")
				else:
					print(f"❌ Failed to delete room '{room_name}'.")
			except Exception as e:
				print(f"❌ Error deleting room: {e}")
		else:
			print("Deletion cancelled.")

	def room_management_menu(self, config_file: str, time_slots: dict) -> dict:
		"""Room management menu interface."""
		while True:
			print("\n" + "="*50)
			print("ROOM MANAGEMENT")
			print("="*50)
			print("1. 👀 View all rooms")
			print("2. ➕ Add new room")
			print("3. ✏️ Edit/rename room")
			print("4. ❌ Delete room")
			print("5. 💾 Save changes and exit")
			print("6. 🚪 Exit without saving")
			print("="*50)
			
			choice = input("Select an option (1-6): ").strip()
			
			if choice == '1':
				self.display_rooms()
			elif choice == '2':
				self.add_room_interactive()
			elif choice == '3':
				self.edit_room_interactive()
			elif choice == '4':
				self.delete_room_interactive()
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