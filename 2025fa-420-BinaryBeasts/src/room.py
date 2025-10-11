from typing import Dict, Any, List, Optional, Union

# Required imports from scheduler project
from scheduler.config import CombinedConfig, SchedulerConfig


class RoomManager:
	"""Manage rooms using scheduler models only (CombinedConfig or SchedulerConfig)."""

	def __init__(self, config_like: Union[CombinedConfig, SchedulerConfig]):
		# Store scheduler models only
		self._combined: Optional[CombinedConfig] = None
		self._scheduler: SchedulerConfig

		if isinstance(config_like, CombinedConfig):
			self._combined = config_like
			self._scheduler = config_like.config
		elif isinstance(config_like, SchedulerConfig):
			self._scheduler = config_like
		else:
			raise TypeError("RoomManager expects CombinedConfig or SchedulerConfig from scheduler.config")

	def _edit_context(self):
		"""Yield an editable model context for atomic edits with validation."""
		if self._combined is not None:
			return self._combined.edit_mode()
		return self._scheduler.edit_mode()

	def _sync_scheduler(self) -> None:
		"""Ensure self._scheduler points to the current scheduler model.

		When editing a CombinedConfig, the inner .config may be replaced
		during validation. Keep our reference in sync so getters reflect changes.
		"""
		if self._combined is not None:
			self._scheduler = self._combined.config

	def get_rooms(self) -> List[str]:
		"""Return a copy of the list of rooms."""
		return list(self._scheduler.rooms)

	def add_room(self, room_name: str) -> bool:
		"""Add a room if it does not already exist. Returns True if added, False if already present."""
		if not isinstance(room_name, str) or not room_name:
			raise TypeError("room_name must be a non-empty string")

		rooms = self.get_rooms()
		if room_name in rooms:
			return False

		with self._edit_context() as editable:
			sched = editable.config if hasattr(editable, 'config') else editable
			sched.rooms.append(room_name)
		self._sync_scheduler()
		return True

	def delete_room(self, room_name: str) -> bool:
		"""Delete a room if it exists. Returns True if deleted, False if not found."""
		rooms = self.get_rooms()
		if room_name not in rooms:
			return False

		with self._edit_context() as editable:
			sched = editable.config if hasattr(editable, 'config') else editable
			# Clean references in courses and faculty FIRST
			for course in sched.courses:
				course.room = [r for r in course.room if r != room_name]
			for fac in sched.faculty:
				if room_name in fac.room_preferences:
					fac.room_preferences.pop(room_name, None)
			# Now remove from rooms to avoid validation on intermediate state
			sched.rooms = [r for r in sched.rooms if r != room_name]
		self._sync_scheduler()
		return True

	def edit_room(self, old_name: str, new_name: str) -> bool:
		"""Rename a room. Returns True if successful, False if old_name not found or new_name exists."""
		if not old_name or not new_name:
			raise TypeError("old_name and new_name must be non-empty strings")

		rooms = self.get_rooms()
		if old_name not in rooms or new_name in rooms:
			return False

		with self._edit_context() as editable:
			sched = editable.config if hasattr(editable, 'config') else editable
			# To avoid validation errors, temporarily ensure new_name exists in rooms
			if new_name not in sched.rooms:
				sched.rooms = list(sched.rooms) + [new_name]
			# Update room references in courses
			for course in sched.courses:
				course.room = [new_name if r == old_name else r for r in course.room]
			# Update room preference keys in faculty
			for fac in sched.faculty:
				if old_name in fac.room_preferences:
					val = fac.room_preferences.pop(old_name)
					fac.room_preferences[new_name] = val
			# Finally, remove the old name from rooms
			sched.rooms = [r for r in sched.rooms if r != old_name]
		self._sync_scheduler()
		return True

	def set_rooms(self, new_rooms: List[str]) -> dict:
		"""
		Replace the rooms list with `new_rooms`.
		Returns a report dict: {'added': [...], 'removed': [...]}.
		Raises TypeError/ValueError for invalid input.
		"""

		# Validate type
		if not isinstance(new_rooms, list) or not all(isinstance(r, str) for r in new_rooms):
			raise TypeError("new_rooms must be a list of strings")
		# Validate uniqueness
		if len(new_rooms) != len(set(new_rooms)):
			raise ValueError("room names must be unique")

		old_rooms = set(self.get_rooms())
		new_set = set(new_rooms)

		with self._edit_context() as editable:
			sched = editable.config if hasattr(editable, 'config') else editable
			# Compute removed before changes
			removed = old_rooms - new_set
			# First, clean references for rooms that will be removed
			for course in sched.courses:
				course.room = [r for r in course.room if r in new_set]
			for fac in sched.faculty:
				for rm in list(removed):
					fac.room_preferences.pop(rm, None)
			# Now replace rooms with the new list
			sched.rooms = list(new_rooms)
		self._sync_scheduler()

		return {
			'added': sorted(list(new_set - old_rooms)),
			'removed': sorted(list(removed)),
		}

	def _update_room_references(self, old_name: str, new_name: str):
		"""Utility kept for compatibility if needed; uses scheduler model."""
		with self._edit_context() as editable:
			sched = editable.config if hasattr(editable, 'config') else editable
			for course in sched.courses:
				course.room = [new_name if r == old_name else r for r in course.room]
			for fac in sched.faculty:
				if old_name in fac.room_preferences:
					val = fac.room_preferences.pop(old_name)
					fac.room_preferences[new_name] = val
		self._sync_scheduler()

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
		for course in self._scheduler.courses:
			if room_name in list(course.room):
				affected_courses.append(str(course.course_id))
		
		# Check faculty preferences
		affected_faculty = []
		for faculty in self._scheduler.faculty:
			if room_name in dict(faculty.room_preferences).keys():
				affected_faculty.append(str(faculty.name))
		
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
				# Save changes back to file as combined JSON
				config_dict = self._scheduler.model_dump()
				full_json = {"config": config_dict, "time_slot_config": time_slots}
				try:
					with open(config_file, 'w', encoding='utf-8') as f:
						import json as _json
						_json.dump(full_json, f, indent=2, ensure_ascii=False)
					print(f"✅ Configuration saved successfully to {config_file}")
				except Exception as e:
					print(f"❌ Error saving configuration: {e}")
				return config_dict
			elif choice == '6':
				print("Exiting without saving changes.")
				return self._scheduler.model_dump()
			else:
				print("Invalid choice. Please select 1-6.")

	# Serialization helpers
	def to_combined_dict(self) -> Dict[str, Any]:
		"""Return a serializable dict for saving.

		If CombinedConfig is available, dump the full combined dict; otherwise dump only the scheduler config under 'config'.
		"""
		if self._combined is not None:
			return self._combined.model_dump()
		return {"config": self._scheduler.model_dump()}