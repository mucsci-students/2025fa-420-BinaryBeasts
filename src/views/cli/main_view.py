

def get_user_input():
        print("Main Menu:")
        print("1. Edit Course")
        print("2. Edit Lab")
        print("3. Edit Faculty")
        print("4. Edit Room")
        print("5. Generate Schedules")
        print("6. Save Configuration file")
        print("7. Import Schedules")
        print("8. Exit")
        return input("Enter your choice (1-8): ").strip()

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