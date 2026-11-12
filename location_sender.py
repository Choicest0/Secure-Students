import math
import time
from plyer import gps, sms


class LocationSender:
    """Manages live GPS tracking, geofence calculations, and Google Maps SMS alerts."""

    def __init__(self, storage_manager, on_status_update=None):
        self.storage = storage_manager
        self.on_status_update = on_status_update
        config = self.storage.get_all()
        self.current_lat = config["school_lat"]
        self.current_lon = config["school_lon"]
        self.gps_active = False
        self.last_sms_time = 0

    def start_gps(self):
        try:
            gps.configure(on_location=self._on_location, on_status=self._on_gps_status)
            gps.start(minTime=3000, minDistance=5)
            self.gps_active = True
        except Exception as e:
            self.gps_active = False
            print(f"[LocationSender] GPS hardware unavailable (Simulator mode): {e}")

    def stop_gps(self):
        try:
            gps.stop()
            self.gps_active = False
        except Exception:
            pass

    def _on_location(self, **kwargs):
        self.current_lat = float(kwargs.get("lat", self.current_lat))
        self.current_lon = float(kwargs.get("lon", self.current_lon))
        if self.on_status_update:
            self.on_status_update(self.current_lat, self.current_lon)

    def _on_gps_status(self, stype, status):
        print(f"[LocationSender] GPS Status ({stype}): {status}")

    def calculate_distance_meters(self, lat1, lon1, lat2, lon2):
        earth_radius = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius * c

    def check_geofence_status(self):
        config = self.storage.get_all()
        radius = config["geofence_radius"]

        dist_school = self.calculate_distance_meters(
            self.current_lat, self.current_lon, config["school_lat"], config["school_lon"]
        )
        dist_home = self.calculate_distance_meters(
            self.current_lat, self.current_lon, config["home_lat"], config["home_lon"]
        )

        if dist_school <= radius:
            return "AT_SCHOOL", dist_school, dist_home
        elif dist_home <= radius:
            return "AT_HOME", dist_school, dist_home
        else:
            return "IN_TRANSIT", dist_school, dist_home

    def build_google_maps_link(self):
        return f"https://google.com{self.current_lat:.6f},{self.current_lon:.6f}"

    def send_parent_alert(self, alert_title, details, bypass_cooldown=False):
        now = time.time()
        if not bypass_cooldown and (now - self.last_sms_time < 15):
            return False, "Cooldown active (prevents duplicate SMS)"

        self.last_sms_time = now
        config = self.storage.get_all()
        parent_phone = config["parent_phone"]
        student_name = config["student_name"]
        maps_url = self.build_google_maps_link()

        message_body = (
            f"[{alert_title}] Student: {student_name}\n"
            f"{details}\n"
            f"Live Google Maps: {maps_url}"
        )

        print(f"\n=== SENDING SMS TO {parent_phone} ===\n{message_body}\n===============================")
        try:
            sms.send(recipient=parent_phone, message=message_body)
            return True, f"SMS Alert sent to {parent_phone}"
        except Exception as e:
            return False, f"Simulated SMS Logged (Desktop/No SIM): {e}"
