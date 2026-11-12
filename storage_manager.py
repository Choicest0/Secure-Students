import json
import os


class StorageManager:
    """Handles persistent local storage for School/Home GPS, schedules, and contacts."""

    def __init__(self, filename="safety_config.json"):
        self.filename = filename
        self.default_data = {
            "student_name": "Student",
            "parent_phone": "+919876543210",
            "school_lat": 30.3165,
            "school_lon": 78.0322,
            "home_lat": 30.3250,
            "home_lon": 78.0410,
            "geofence_radius": 150.0,
            "school_start_time": "07:00",
            "school_end_time": "15:00",
        }
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            self.save_data(self.default_data)
            return self.default_data.copy()
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                loaded = json.load(file)
                for key, value in self.default_data.items():
                    if key not in loaded:
                        loaded[key] = value
                return loaded
        except Exception as e:
            print(f"[StorageManager] Error loading config: {e}")
            return self.default_data.copy()

    def save_data(self, new_data=None):
        if new_data is not None:
            self.data.update(new_data)
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4)
            return True
        except Exception as e:
            print(f"[StorageManager] Error saving config: {e}")
            return False

    def update_school_location(self, lat, lon):
        self.data["school_lat"] = float(lat)
        self.data["school_lon"] = float(lon)
        return self.save_data()

    def update_home_location(self, lat, lon):
        self.data["home_lat"] = float(lat)
        self.data["home_lon"] = float(lon)
        return self.save_data()

    def update_parent_info(self, student_name, parent_phone, start_time, end_time):
        self.data["student_name"] = student_name.strip()
        self.data["parent_phone"] = parent_phone.strip()
        self.data["school_start_time"] = start_time.strip()
        self.data["school_end_time"] = end_time.strip()
        return self.save_data()

    def get_all(self):
        return self.data
