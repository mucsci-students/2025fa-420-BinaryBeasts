from typing import Optional, Any


class main_model:
    """
    Main model now implementing Singleton pattern.
    Ensuring only one instance exists throughout the application.
    """
    _instance = None

    def __new__(cls):
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the model only once."""
        # Only initialize once to prevent resetting state on multiple instantiations
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._reset()
            self._initialized = True

    def _reset(self):
        """Reset singleton state - useful for testing and initialization."""
        self.schedules = []
        self.current_schedule_index = 0
        self.config: Optional[Any] = None
        self.num_schedules = 0

    @classmethod
    def reset_instance(cls):
        """Force reset the singleton - for testing only."""
        if cls._instance and hasattr(cls._instance, '_reset'):
            cls._instance._reset()

    def set_config(self, config):
        self.config = config

    def set_num_schedules(self, num):
        self.num_schedules = num

    def set_limit(self, limit: int):
        if self.config is not None:
            self.config.limit = limit

    def next_schedule(self, num):
        return self.schedules[num]

    def previous_schedule(self, num):
        return self.schedules[num]
