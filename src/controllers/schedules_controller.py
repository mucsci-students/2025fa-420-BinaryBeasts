import src.models.main_model as main_model
import src.views.cli.main_view as main_view
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig
from src.views.cli import schedules_view

class generate_controller():
    def __init__(self, schedules):
        self.schedules = schedules
        self.index = 0
        

    def next_schedule(self):
        self.index += 1
        if self.index >= len(self.schedules):
            self.index = 0
        schedules_view.display_schedule(self.schedules[self.index])
    
    def previous_schedule(self):
        self.index += 1
        if self.index >= len(self.schedules):
            self.index = 0
        schedules_view.display_schedule(self.schedules[self.index])
    
    def save_schedules():
        pass
    
    def entry(self):
        while(True):
            input = schedules_view.schedule_navigation_view()
            if input == "1":
                schedules_view.display_schedule(self.next_schedule())
            elif input == "2":
                schedules_view.display_schedule(self.previous_schedule())
            elif input == "3":
                self.save_schedule
            elif input == "4":
                break
            