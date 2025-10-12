

def get_user_input():
        print("Main Menu:")
        print("1. Edit Course")
        print("2. Edit Lab")
        print("3. Edit Faculty")
        print("4. Edit Room")
        print("5. Generate Schedules")
        print("6. Import Schedules")
        print("7. Exit")
        return input("Enter your choice (1-7): ").strip()

def load_config():
        path = input("Enter path to configuration file (default 'config.json'): ").strip()
        if not path:
            path = "config.json"
            return path
        return path

def generate_schedules():
       num = input("How many schedules would you like? ")
       return int(num)

def import_schedules():
        path = input("Enter path to schedules JSON file (default 'schedules.json'): ").strip()
        if not path:
            path = "schedules.json"
        return path

def print_config_summary(config: dict, time_slots: dict) -> None:
    """
    Print a readable summary of the configuration.
    Args: config: Configuration dictionary
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

        room_prefs = member.get('room_preferences', {})
        if room_prefs:
            top_rooms = sorted(room_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      Preferred rooms: {', '.join([f'{r}({p})' for r, p in top_rooms])}")

        lab_prefs = member.get('lab_preferences', {})
        if lab_prefs:
            top_labs = sorted(lab_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"      Preferred labs: {', '.join([f'{l}({p})' for l, p in top_labs])}")

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