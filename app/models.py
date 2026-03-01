import random
import time
from shapely.geometry import Point
from geopy.distance import geodesic
from .config import SEND_INTERVAL_RANGE, BASE_LAT, BASE_LON, ROUTES_PER_TEAM, ZONES_PER_TEAM_RANGE
from .zoneGenerator import generate_zone, generate_route_within_zone


class Radio:
    def __init__(self, radio_id, serial_number, name, team_name, is_stolen, route, zone):
        self.id = radio_id
        self.serial_number = serial_number
        self.name = name
        self.team = team_name
        self.is_stolen = is_stolen
        self.route = route
        self.zone = zone
        self.route_index = 0

        self.battery = random.uniform(60, 100)
        self.active = True
        self.signal_strength = 0 # Will be dynamically calculated

        self.next_send_time = time.time() + random.randint(*SEND_INTERVAL_RANGE)

    def _calculate_signal_strength(self, lat, lon):
        dist_km = geodesic((lat, lon), (BASE_LAT, BASE_LON)).kilometers
        
        # Simple simulated attenuation curve
        # Base signal is strong (-50 dBm), attenuates by roughly 2.5 dBm per km
        # Random noise +/- 3 dBm
        base_signal = -50
        attenuation = dist_km * 2.5
        noise = random.uniform(-3, 3)
        
        strength = base_signal - attenuation + noise
        
        # Cap realistically between excellent (-40) and dead zone (-120)
        return int(max(-120, min(-40, strength)))

    def move_and_send(self):
        now = time.time()

        if not self.active:
            return None

        if now < self.next_send_time:
            return None

        self.next_send_time = now + random.randint(*SEND_INTERVAL_RANGE)

        lat, lon = self.route[self.route_index]
        self.route_index = (self.route_index + 1) % len(self.route)

        # Battery drain
        self.battery -= random.uniform(0.1, 0.5)
        if self.battery <= 0:
            self.active = False

        # Random signal drop
        if random.random() < 0.01:
            self.active = False

        # Random geofence violation
        if random.random() < 0.02:
            lat += random.uniform(0.02, 0.05)
            lon += random.uniform(0.02, 0.05)

        outside_zone = not self.zone.contains(Point(lat, lon))

        # Dynamic Signal Attenuation based on distance
        self.signal_strength = self._calculate_signal_strength(lat, lon)

        payload = {
            "radioId": self.id,
            "serialNumber": self.serial_number,
            "name": self.name,
            "team": self.team,
            "isStolen": self.is_stolen,
            "latitude": lat,
            "longitude": lon,
            "battery": round(self.battery, 2),
            "signalStrength": self.signal_strength,
            "active": self.active,
            "outsideZone": outside_zone,
            "timestamp": int(time.time())
        }

        return payload

class Team:
    def __init__(self, team_model, radio_models, routes_with_zones):
        self.id = team_model.id
        self.name = team_model.name
        self.description = team_model.description
        self.radios = []

        # routes_with_zones is a list of (route, zone) tuples
        self.routes_with_zones = routes_with_zones

        # Create radios from the provided database models
        for rm in radio_models:
            route, zone = random.choice(self.routes_with_zones)
            radio = Radio(
                radio_id=rm.id,
                serial_number=rm.serial_number,
                name=rm.name,
                team_name=self.name,
                is_stolen=rm.is_stolen,
                route=route,
                zone=zone
            )
            self.radios.append(radio)