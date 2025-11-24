def parse_course_string(course_str: str) -> dict:
    """
    Parse a course CSV string into a dictionary.
    Format: CMSC 140.01,Hardy,Roddy 147,Mac,MON 14:00-14:50,TUE 13:10-15:00
    Returns: Dictionary with course_id, faculty, room, lab, and time_slots
    """
    parts = course_str.split(",")
    if len(parts) < 4:
        return {}

    course_id = parts[0].strip()
    faculty = parts[1].strip()
    room = parts[2].strip()
    lab = parts[3].strip()
    time_slots = [slot.strip() for slot in parts[4:]]

    return {
        "course_id": course_id,
        "faculty": faculty,
        "room": room,
        "lab": lab,
        "time_slots": time_slots,
    }


def display_schedule_basic(schedule: list) -> None:
    """
    Display a schedule in tabular format showing all courses.
    """
    if not schedule:
        print("No schedule data to display.")
        return

    # Parse all courses
    courses = []
    for course_str in schedule:
        course = parse_course_string(course_str)
        if course:
            courses.append(course)

    if not courses:
        print("No valid course data to display.")
        return

    # Sort courses by earliest time slot for better readability
    courses_sorted = sorted(courses, key=get_earliest_time)

    # Display all courses in a table
    print("\n" + "=" * 95)
    print("SCHEDULE VIEWER")
    print("=" * 95)

    # Create table header
    print(
        f"| {'Course':<12} | {'Faculty':<8} | {'MON':<11} | {'TUE':<11} | {'WED':<11} | {'THU':<11} | {'FRI':<11} |"
    )
    print("=" * 95)

    # Create rows for each course
    for course in courses_sorted:
        # Parse time slots by day
        day_times = {"MON": "", "TUE": "", "WED": "", "THU": "", "FRI": ""}

        for slot in course["time_slots"]:
            # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
            slot_clean = slot.replace("^", "")  # Remove lab indicator
            parts = slot_clean.split(" ", 1)
            if len(parts) == 2:
                day = parts[0].strip()
                time = parts[1].strip()
                if day in day_times:
                    if day_times[day]:
                        day_times[day] += "\n" + time
                    else:
                        day_times[day] = time

        # Print course row
        print(
            f"| {course['course_id']:<12} | {course['faculty']:<8} | {day_times['MON']:<11} | {day_times['TUE']:<11} | {day_times['WED']:<11} | {day_times['THU']:<11} | {day_times['FRI']:<11} |"
        )


def display_schedule_by_room(schedule: list) -> None:
    """
    Display a schedule organized by room and lab.
    Shows a table for each room/lab with courses and their time slots.
    """
    if not schedule:
        print("No schedule data to display.")
        return

    # Parse all courses and group by room and lab
    room_schedule = {}  # room -> list of course data
    lab_schedule = {}  # lab -> list of course data

    for course_str in schedule:
        course = parse_course_string(course_str)
        if not course:
            continue

        # Group by room
        room = course["room"]
        if room not in room_schedule:
            room_schedule[room] = []
        room_schedule[room].append(course)

        # Group by lab (if not None)
        lab = course["lab"]
        if lab and lab.lower() != "none":
            if lab not in lab_schedule:
                lab_schedule[lab] = []
            lab_schedule[lab].append(course)

    # Display room schedules
    print("\n" + "=" * 80)
    print("SCHEDULE BY ROOM")
    print("=" * 80)

    for room, courses in sorted(room_schedule.items()):
        # Sort courses by earliest time slot for better readability
        courses_sorted = sorted(courses, key=get_earliest_time)

        print(f"\n{room}")
        print("-" * 80)

        # Create table header
        print(
            f"{'Course':<15} | {'Faculty':<10} | {'MON':<15} | {'TUE':<15} | {'WED':<15} | {'THU':<15} | {'FRI':<15}"
        )
        print("-" * 80)

        # Create rows for each course
        for course in courses_sorted:
            # Parse time slots by day
            day_times = {"MON": "", "TUE": "", "WED": "", "THU": "", "FRI": ""}

            for slot in course["time_slots"]:
                # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
                slot = slot.replace("^", "")  # Remove lab indicator
                parts = slot.split(" ", 1)
                if len(parts) == 2:
                    day = parts[0].strip()
                    time = parts[1].strip()
                    if day in day_times:
                        if day_times[day]:
                            day_times[day] += "\n" + time
                        else:
                            day_times[day] = time

            # Print course row
            print(
                f"{course['course_id']:<15} | {course['faculty']:<10} | {day_times['MON']:<15} | {day_times['TUE']:<15} | {day_times['WED']:<15} | {day_times['THU']:<15} | {day_times['FRI']:<15}"
            )

    # Display lab schedules
    if lab_schedule:
        print("\n" + "=" * 80)
        print("LAB SCHEDULES")
        print("=" * 80)

        for lab, courses in sorted(lab_schedule.items()):
            # Sort courses by earliest time slot for better readability
            courses_sorted = sorted(courses, key=get_earliest_time)

            print(f"\n{lab} Lab")
            print("-" * 80)

            # Create table header
            print(
                f"{'Course':<15} | {'Faculty':<10} | {'MON':<15} | {'TUE':<15} | {'WED':<15} | {'THU':<15} | {'FRI':<15}"
            )
            print("-" * 80)

            # Create rows for each course
            for course in courses_sorted:
                # Parse time slots by day (only show lab sessions marked with ^)
                day_times = {"MON": "", "TUE": "", "WED": "", "THU": "", "FRI": ""}

                for slot in course["time_slots"]:
                    # Only include lab sessions (marked with ^)
                    if "^" in slot:
                        slot = slot.replace("^", "")
                        parts = slot.split(" ", 1)
                        if len(parts) == 2:
                            day = parts[0].strip()
                            time = parts[1].strip()
                            if day in day_times:
                                if day_times[day]:
                                    day_times[day] += "\n" + time
                                else:
                                    day_times[day] = time

                # Print course row
                print(
                    f"{course['course_id']:<15} | {course['faculty']:<10} | {day_times['MON']:<15} | {day_times['TUE']:<15} | {day_times['WED']:<15} | {day_times['THU']:<15} | {day_times['FRI']:<15}"
                )


def get_earliest_time(course: dict) -> tuple:
    """
    Extract the earliest time from a course's time slots.
    Returns: (day_order, hour, minute) for sorting purposes
    """
    day_order = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4}
    earliest = (5, 24, 0)  # Default to end of week if no valid time found

    for slot in course['time_slots']:
        # Remove lab indicator and parse
        slot_clean = slot.replace('^', '')
        parts = slot_clean.split(' ', 1)
        if len(parts) == 2:
            day = parts[0].strip()
            time_str = parts[1].strip().split('-')[0]  # Get start time
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
                day_num = day_order.get(day, 5)
                if (day_num, hour, minute) < earliest:
                    earliest = (day_num, hour, minute)

    return earliest


def display_schedule_by_faculty(schedule: list) -> None:
    """
    Display a schedule organized by faculty member.
    Shows a table for each faculty with their courses and time slots.
    Courses are sorted by their earliest time slot for better readability.
    """
    if not schedule:
        print("No schedule data to display.")
        return

    # Parse all courses and group by faculty
    faculty_schedule = {}  # faculty -> list of course data

    for course_str in schedule:
        course = parse_course_string(course_str)
        if not course:
            continue

        faculty = course["faculty"]
        if faculty not in faculty_schedule:
            faculty_schedule[faculty] = []
        faculty_schedule[faculty].append(course)

    # Display faculty schedules
    print("\n" + "=" * 80)
    print("SCHEDULE BY FACULTY")
    print("=" * 80)

    for faculty, courses in sorted(faculty_schedule.items()):
        # Sort courses by earliest time slot for better readability
        courses_sorted = sorted(courses, key=get_earliest_time)

        print(f"\n{faculty}")
        print("-" * 80)

        # Create table header
        print(
            f"{'Course':<15} | {'Room':<12} | {'Lab':<8} | {'MON':<15} | {'TUE':<15} | {'WED':<15} | {'THU':<15} | {'FRI':<15}"
        )
        print("-" * 80)

        # Create rows for each course
        for course in courses_sorted:
            # Parse time slots by day
            day_times = {"MON": "", "TUE": "", "WED": "", "THU": "", "FRI": ""}

            for slot in course["time_slots"]:
                # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
                slot_clean = slot.replace("^", "")  # Remove lab indicator for parsing
                parts = slot_clean.split(" ", 1)
                if len(parts) == 2:
                    day = parts[0].strip()
                    time = parts[1].strip()
                    if day in day_times:
                        if day_times[day]:
                            day_times[day] += "\n" + time
                        else:
                            day_times[day] = time

            # Print course row
            lab_display = course["lab"] if course["lab"].lower() != "none" else "-"
            print(
                f"{course['course_id']:<15} | {course['room']:<12} | {lab_display:<8} | {day_times['MON']:<15} | {day_times['TUE']:<15} | {day_times['WED']:<15} | {day_times['THU']:<15} | {day_times['FRI']:<15}"
            )


def generate_schedules_view():
    input_str = input("Enter the number of schedules to generate: ")
    return input_str


def schedule_navigation_view():
    print("\n📋 NAVIGATION OPTIONS:")
    print("   1. Next schedule")
    print("   2. Previous schedule")
    print("   3. Go to specific schedule")
    print("   4. View by room/lab")
    print("   5. View by faculty")
    print("   6. Export schedules to file")
    print("   7. Export current schedule by faculty (PDF)")
    print("   8. Export current schedule by room (PDF)")
    print("   9. Return to main menu")
    print("-" * 60)
    return input("Select an option (1-9): ").strip()


def save_schedules_view():
    """Get filename and format for saving schedules"""
    filename = input("Enter filename to save schedules (default 'schedules'): ").strip()
    if not filename:
        filename = "schedules"

    format_input = input("Output format (json/csv, default: json): ").strip().lower()
    format_type = "csv" if format_input in ["csv", "c"] else "json"

    # Add extension if not provided
    if not filename.endswith(f".{format_type}"):
        filename = f"{filename}.{format_type}"

    return filename, format_type


def save_faculty_pdf_view(default_name: str = "faculty_schedules.pdf") -> str:
    """Prompt for filename to save faculty PDF (returns filename)."""
    filename = input(f"Enter filename to save faculty PDF (default '{default_name}'): ").strip()
    if not filename:
        filename = default_name
    # ensure extension
    if not filename.lower().endswith('.pdf'):
        filename = filename + '.pdf'
    return filename


def display_schedule(schedule):
    """
    Display a schedule in tabular format.
    Args: schedule: List of course objects with as_csv() method
    """
    if not schedule:
        print("No schedule data to display.")
        return

    # Convert schedule objects to CSV strings
    schedule_strings = []
    for course in schedule:
        if course is not None:
            schedule_strings.append(course.as_csv())

    # Display using tabular format
    display_schedule_basic(schedule_strings)


def save_schedules_by_faculty_pdf(schedule: list, filename: str = "faculty_schedules.pdf") -> str:
    """
    Save schedules grouped by faculty into a simple PDF-like text file.
    This minimal exporter accepts schedule as a list of course objects (with as_csv())
    or raw CSV strings. It writes a readable text file saved with .pdf extension so
    users can print or preview it. It's intentionally lightweight to avoid adding
    heavy dependencies in this branch.
    """
    # Normalize to CSV strings
    schedule_strings = []
    for item in schedule:
        if item is None:
            continue
        if hasattr(item, "as_csv"):
            try:
                schedule_strings.append(item.as_csv())
            except Exception:
                schedule_strings.append(str(item))
        else:
            schedule_strings.append(str(item))

    # Build faculty mapping
    faculty_map = {}
    for csv in schedule_strings:
        c = parse_course_string(csv)
        if not c:
            continue
        fac = c.get("faculty", "Unknown")
        faculty_map.setdefault(fac, []).append(c)

    # Prepare pages as simple text lines per faculty
    pages = []
    for fac in sorted(faculty_map.keys()):
        lines = [fac, "=" * max(20, len(fac))]
        courses = sorted(faculty_map[fac], key=get_earliest_time)
        for course in courses:
            lab_display = course["lab"] if course["lab"].lower() != "none" else "-"
            lines.append(f"{course['course_id']} | Room: {course['room']} | Lab: {lab_display}")
            for slot in course["time_slots"]:
                lines.append(f"  - {slot}")
            lines.append("")
        pages.append(lines)

    if not pages:
        pages = [["No schedule data available."]]

    # Try to use reportlab for a proper PDF; otherwise fallback to a plain text file
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception:
        # reportlab not available — fall back to simple text-based output and inform user
        print("reportlab not installed; writing a readable text file with .pdf extension.\nTo get a proper PDF install: pip install reportlab")
        try:
            if not filename.lower().endswith('.pdf'):
                filename = filename + '.pdf'
            with open(filename, 'wb') as f:
                content = []
                for p in pages:
                    content.extend(p)
                    content.append('\f')
                text = '\n'.join(content)
                f.write(text.encode('utf-8'))
            return filename
        except Exception as e:
            print(f"Failed to write faculty PDF fallback: {e}")
            return ""

    # Build a proper PDF using reportlab with tables that mirror the GUI layout
    try:
        if not filename.lower().endswith('.pdf'):
            filename = filename + '.pdf'

        from reportlab.lib import colors as rl_colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        header = ['Course', 'Room', 'Lab', 'MON', 'TUE', 'WED', 'THU', 'FRI']

        for fac in sorted(faculty_map.keys()):
            courses = sorted(faculty_map[fac], key=get_earliest_time)
            # Title
            elements.append(Paragraph(fac, styles['Title']))
            elements.append(Spacer(1, 6))

            # Build table data
            data = [header]
            for course in courses:
                day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}
                for slot in course['time_slots']:
                    slot_clean = slot.replace('^', '')
                    parts = slot_clean.split(' ', 1)
                    if len(parts) == 2:
                        day = parts[0].strip()
                        time = parts[1].strip()
                        if day in day_times:
                            if day_times[day]:
                                day_times[day] += '\n' + time
                            else:
                                day_times[day] = time

                lab_display = course['lab'] if course['lab'].lower() != 'none' else '-'
                row = [course['course_id'], course['room'], lab_display, day_times['MON'], day_times['TUE'], day_times['WED'], day_times['THU'], day_times['FRI']]
                data.append(row)

            # Create styled table
            tbl = Table(data, repeatRows=1, hAlign='LEFT')
            tbl_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ])
            tbl.setStyle(tbl_style)

            elements.append(tbl)
            elements.append(Spacer(1, 12))
            elements.append(PageBreak())

        # Build document
        doc.build(elements)
        return filename
    except Exception as e:
        print(f"Failed to generate PDF with reportlab: {e}")
        return ""


def save_schedules_by_room_pdf(schedule: list, filename: str = "room_schedules.pdf") -> str:
    """
    Save schedules grouped by room into a PDF file.
    This exporter accepts schedule as a list of course objects (with as_csv())
    or raw CSV strings and creates a PDF with one section per room.
    """
    # Normalize to CSV strings
    schedule_strings = []
    for item in schedule:
        if item is None:
            continue
        if hasattr(item, "as_csv"):
            try:
                schedule_strings.append(item.as_csv())
            except Exception:
                schedule_strings.append(str(item))
        else:
            schedule_strings.append(str(item))

    # Build room mapping
    room_map = {}
    for csv in schedule_strings:
        c = parse_course_string(csv)
        if not c:
            continue
        room = c.get("room", "Unknown")
        room_map.setdefault(room, []).append(c)

    # Prepare pages as simple text lines per room
    pages = []
    for room in sorted(room_map.keys()):
        lines = [room, "=" * max(20, len(room))]
        courses = sorted(room_map[room], key=get_earliest_time)
        for course in courses:
            lab_display = course["lab"] if course["lab"].lower() != "none" else "-"
            lines.append(f"{course['course_id']} | Faculty: {course['faculty']} | Lab: {lab_display}")
            for slot in course["time_slots"]:
                lines.append(f"  - {slot}")
            lines.append("")
        pages.append(lines)

    if not pages:
        pages = [["No schedule data available."]]

    # Try to use reportlab for a proper PDF; otherwise fallback to a plain text file
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception:
        # reportlab not available — fall back to simple text-based output and inform user
        print("reportlab not installed; writing a readable text file with .pdf extension.\nTo get a proper PDF install: pip install reportlab")
        try:
            if not filename.lower().endswith('.pdf'):
                filename = filename + '.pdf'
            with open(filename, 'wb') as f:
                content = []
                for p in pages:
                    content.extend(p)
                    content.append('\f')
                text = '\n'.join(content)
                f.write(text.encode('utf-8'))
            return filename
        except Exception as e:
            print(f"Failed to write room PDF fallback: {e}")
            return ""

    # Build a proper PDF using reportlab with tables
    try:
        if not filename.lower().endswith('.pdf'):
            filename = filename + '.pdf'

        from reportlab.lib import colors as rl_colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        header = ['Course', 'Faculty', 'Lab', 'MON', 'TUE', 'WED', 'THU', 'FRI']

        for room in sorted(room_map.keys()):
            courses = sorted(room_map[room], key=get_earliest_time)
            # Title
            elements.append(Paragraph(room, styles['Title']))
            elements.append(Spacer(1, 6))

            # Build table data
            data = [header]
            for course in courses:
                day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}
                for slot in course['time_slots']:
                    slot_clean = slot.replace('^', '')
                    parts = slot_clean.split(' ', 1)
                    if len(parts) == 2:
                        day = parts[0].strip()
                        time = parts[1].strip()
                        if day in day_times:
                            if day_times[day]:
                                day_times[day] += '\n' + time
                            else:
                                day_times[day] = time

                lab_display = course['lab'] if course['lab'].lower() != 'none' else '-'
                row = [course['course_id'], course['faculty'], lab_display, day_times['MON'], day_times['TUE'], day_times['WED'], day_times['THU'], day_times['FRI']]
                data.append(row)

            # Create styled table
            tbl = Table(data, repeatRows=1, hAlign='LEFT')
            tbl_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ])
            tbl.setStyle(tbl_style)

            elements.append(tbl)
            elements.append(Spacer(1, 12))
            elements.append(PageBreak())

        # Build document
        doc.build(elements)
        return filename
    except Exception as e:
        print(f"Failed to generate PDF with reportlab: {e}")
        return ""


def save_room_pdf_view(default_name: str = "room_schedules.pdf") -> str:
    """Prompt for filename to save room PDF (returns filename)."""
    filename = input(f"Enter filename to save room PDF (default '{default_name}'): ").strip()
    if not filename:
        filename = default_name
    # ensure extension
    if not filename.lower().endswith('.pdf'):
        filename = filename + '.pdf'
    return filename
