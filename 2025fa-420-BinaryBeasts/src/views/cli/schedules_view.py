from src.controllers import schedules_controller

def generate_schedules_view():
    input_str = input("Enter the number of schedules to generate: ")
    return input_str

def schedule_navigation_view():
    print("Schedule Navigation Menu:")
    print("1. Next Schedule")
    print("2. Previous Schedule")
    print("3. Save Schedule")
    print("4. Exit to Main Menu")
    return input("Enter your choice (1-3): ").strip()

def save_schedules_view():
    path = input("Enter the path to save schedules (default 'schedules.txt'): ").strip()
    if not path:
        path = "schedules.txt"
    return path

def display_schedule(schedule):
    for course in schedule:
        if course == None:
            break
        else:
            print(f"{course.as_csv()}")







    
    