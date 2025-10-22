class main_model:
    def __init__(self):
        super().__init__()
        self.schedules = []
        self.current_schedule_index = 0
        self.config = None
        self.num_schedules = 0

    def set_config(self, config):
        self.config = config

    def set_num_schedules(self, num):
        self.num_schedules = num

    def set_limit(self, limit: int):
        self.config.limit = limit

    def next_schedule(self, num):
        return self.schedules[num]

    def previous_schedule(self, num):
        return self.schedules[num]
