import random
import time
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import joinedload
from .models import Team
from .config import BASE_LAT, BASE_LON, LOOP_SLEEP, SERVER_HOST, SERVER_PORT, ROUTES_PER_TEAM, ZONES_PER_TEAM_RANGE
from .server import start_server, global_state
from .database import SessionLocal, TeamModel
from .zoneGenerator import generate_zone, fetch_all_routes_batch_sync

class Simulator:
    def __init__(self):
        self.teams = []

        db = SessionLocal()
        try:
            # Query all teams and eagerly load radios
            db_teams = db.query(TeamModel).options(joinedload(TeamModel.radios)).all()
            
            # 1. Prepare base data and generate zones
            teams_base_info = []
            route_tasks = [] 

            for db_team in db_teams:
                # Seed RNG per team for deterministic zones
                team_rng = random.Random(db_team.id)
                
                center_lat = BASE_LAT + team_rng.uniform(-0.5, 0.5)
                center_lon = BASE_LON + team_rng.uniform(-0.5, 0.5)
                
                team_zones = []
                num_zones = team_rng.randint(*ZONES_PER_TEAM_RANGE)
                for _ in range(num_zones):
                    zone = generate_zone(center_lat, center_lon)
                    team_zones.append(zone)

                for ridx in range(ROUTES_PER_TEAM):
                    zone = team_rng.choice(team_zones)
                    # Use a tuple for stable hashing in joblib
                    route_tasks.append((db_team.id, zone, ridx))

                radios_data = [
                    {"id": rm.id, "serial_number": rm.serial_number, "name": rm.name, "is_stolen": rm.is_stolen}
                    for rm in db_team.radios
                ]

                teams_base_info.append({
                    "id": db_team.id,
                    "name": db_team.name,
                    "description": db_team.description,
                    "radios": radios_data,
                })
        finally:
            db.close()

        print(f"🚀 Fetching {len(route_tasks)} routes...")
        
        # 2. Fetch ALL routes concurrently (using batch cache)
        all_fetched_routes = self._fetch_all_routes_cached(route_tasks)

        # 3. Assemble Team objects
        total_routes = sum(len(r) for r in all_fetched_routes.values())
        print(f"✅ Route retrieval complete. Total routes: {total_routes}")
        
        # Assemble teams using the fetched routes
        for info in teams_base_info:
            team_id = info["id"]
            team_routes = all_fetched_routes.get(team_id, [])
            if not team_routes:
                continue

            class MockModel:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)

            team_model = MockModel(id=info["id"], name=info["name"], description=info["description"])
            radio_models = [MockModel(**rm) for rm in info["radios"]]
            self.teams.append(Team(team_model, radio_models, team_routes))

    def _fetch_all_routes_cached(self, route_tasks):
        """Wrapper to call the batch-cached fetcher from zoneGenerator."""
        return fetch_all_routes_batch_sync(route_tasks)

    def run(self):
        print("🚀 Radio Fleet Simulator Started")
        print(f"Teams: {len(self.teams)}")
        
        # Start the local HTTP server in a background thread
        start_server(SERVER_HOST, SERVER_PORT)

        print("Running...")

        while True:
            for team in self.teams:
                for radio in team.radios:
                    payload = radio.move_and_send()
                    if payload:
                        # Update the centralized state for the server to serve
                        global_state[payload["radioId"]] = payload

            time.sleep(LOOP_SLEEP)