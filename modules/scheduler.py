"""
Scheduler Module
Controls when automation should run based on time settings
"""

import datetime
import time


class Scheduler:
    def __init__(self, config):
        self.config = config["bot"]["scheduler"]
        self.enabled = self.config.get("enabled", False)
        
        if self.enabled:
            try:
                self.start_time = datetime.datetime.strptime(
                    self.config.get("start_time", "00:00"), "%H:%M"
                ).time()
                self.end_time = datetime.datetime.strptime(
                    self.config.get("end_time", "23:59"), "%H:%M"
                ).time()
            except ValueError:
                print("Invalid time format in config. Using default times.")
                self.start_time = datetime.time(0, 0)
                self.end_time = datetime.time(23, 59)
        else:
            self.start_time = datetime.time(0, 0)
            self.end_time = datetime.time(23, 59)

    def should_run(self):
        """Check if current time is within the allowed window"""
        if not self.enabled:
            return True

        now = datetime.datetime.now().time()
        
        if self.start_time <= self.end_time:
            return self.start_time <= now <= self.end_time
        else:
            # Overnight schedule (e.g., 22:00 to 06:00)
            return now >= self.start_time or now <= self.end_time

    def get_remaining_time(self):
        """Get seconds until next allowed run window"""
        if not self.enabled or self.should_run():
            return 0

        now = datetime.datetime.now()
        today = now.date()
        
        start_dt = datetime.datetime.combine(today, self.start_time)
        
        if now.time() > self.end_time:
            # Next window is tomorrow
            start_dt += datetime.timedelta(days=1)
        
        return (start_dt - now).total_seconds()
