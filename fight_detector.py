import math
from plyer import accelerometer


class FightDetector:
    """Detects sudden violent shaking, falls, or physical struggles via accelerometer."""

    def __init__(self, threshold=28.0):
        self.threshold = threshold
        self.enabled = False

    def start(self):
        try:
            accelerometer.enable()
            self.enabled = True
        except Exception as e:
            self.enabled = False
            print(f"[FightDetector] Accelerometer unavailable: {e}")

    def stop(self):
        try:
            accelerometer.disable()
            self.enabled = False
        except Exception:
            pass

    def check_for_fight_or_impact(self):
        if not self.enabled:
            return False, 0.0
        try:
            accel = accelerometer.acceleration
            if accel and accel[0] is not None:
                ax, ay, az = accel[0], accel[1], accel[2]
                magnitude = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
                if magnitude >= self.threshold:
                    return True, magnitude
                return False, magnitude
        except Exception:
            pass
        return False, 0.0
