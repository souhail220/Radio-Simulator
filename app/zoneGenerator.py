import random
import requests
import httpx
import os
import asyncio
from joblib import Memory
from shapely.geometry import Polygon

# Joblib Memory for persistent caching
CACHE_DIR = ".cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
memory = Memory(CACHE_DIR, verbose=0)

def generate_zone(center_lat, center_lon, size=0.02):
    return Polygon([
        (center_lat - size, center_lon - size),
        (center_lat - size, center_lon + size),
        (center_lat + size, center_lon + size),
        (center_lat + size, center_lon - size),
    ])

@memory.cache
def fetch_route_sync(coordinates_str):
    """Synchronous OSRM fetch with joblib caching."""
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coordinates_str}?overview=full&geometries=geojson"
    try:
        response = requests.get(osrm_url, timeout=1)
        data = response.json()
        if data.get("code") == "Ok":
            route_coords = data["routes"][0]["geometry"]["coordinates"]
            return [(lat, lon) for lon, lat in route_coords]
    except Exception:
        pass
    return None

async def fetch_route_async(client, coordinates_str):
    """Asynchronous OSRM fetch with joblib caching."""
    # Check cache first using the decorated sync function
    route = fetch_route_sync(coordinates_str)
    if route:
        return route

    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coordinates_str}?overview=full&geometries=geojson"
    try:
        response = await client.get(osrm_url, timeout=1.0)
        data = response.json()
        if data.get("code") == "Ok":
            route_coords = data["routes"][0]["geometry"]["coordinates"]
            route = [(lat, lon) for lon, lat in route_coords]
            # Populate cache manually for future sync/async calls
            _ = fetch_route_sync(coordinates_str) 
            return route
    except Exception:
        pass
    return None

def generate_route_within_zone(zone, route_index=0, num_waypoints=3):
    """Synchronous version using deterministic waypoints for caching."""
    minx, miny, maxx, maxy = zone.bounds
    
    # Use a seed based on zone and index for deterministic waypoints
    seed = f"{minx},{miny},{maxx},{maxy},{route_index}"
    rng = random.Random(seed)

    waypoints = []
    for _ in range(num_waypoints):
        lat = rng.uniform(minx, maxx)
        lon = rng.uniform(miny, maxy)
        waypoints.append((lon, lat))

    coordinates_str = ";".join([f"{lon},{lat}" for lon, lat in waypoints])
    route = fetch_route_sync(coordinates_str)
    
    if route:
        return route

    # Fallback to deterministic straight line
    return [(rng.uniform(minx, maxx), rng.uniform(miny, maxy)) for _ in range(num_waypoints * 5)]

async def generate_route_within_zone_async(client, zone, route_index=0, num_waypoints=3):
    """Asynchronous version using deterministic waypoints."""
    minx, miny, maxx, maxy = zone.bounds
    
    seed = f"{minx},{miny},{maxx},{maxy},{route_index}"
    rng = random.Random(seed)

    waypoints = []
    for _ in range(num_waypoints):
        lat = rng.uniform(minx, maxx)
        lon = rng.uniform(miny, maxy)
        waypoints.append((lon, lat))

    coordinates_str = ";".join([f"{lon},{lat}" for lon, lat in waypoints])
    route = await fetch_route_async(client, coordinates_str)
    
    if route:
        return route

    return [(rng.uniform(minx, maxx), rng.uniform(miny, maxy)) for _ in range(num_waypoints * 5)]

@memory.cache
def fetch_all_routes_batch_sync(route_tasks):
    """
    Synchronous batch fetcher for all routes. 
    This is cached by joblib to store the ENTIRE result set for a given simulation seed.
    """
    return asyncio.run(_fetch_all_routes_async_internal(route_tasks))

async def _fetch_all_routes_async_internal(route_tasks):
    """Internal async helper for batch fetching."""
    all_fetched_routes = {}
    async with httpx.AsyncClient() as client:
        # We don't want to use the individual cache here if we're doing batch caching,
        # but it doesn't hurt.
        tasks = []
        for tid, zone, ridx in route_tasks:
            tasks.append(_fetch_single_route_no_cache(client, tid, zone, ridx))
        
        results = await asyncio.gather(*tasks)
        
        for team_id, zone, route in results:
            if team_id not in all_fetched_routes:
                all_fetched_routes[team_id] = []
            all_fetched_routes[team_id].append((route, zone))
    return all_fetched_routes

async def _fetch_single_route_no_cache(client, team_id, zone, route_index):
    """Fetch a single route without individual joblib cache to avoid overhead in batch."""
    minx, miny, maxx, maxy = zone.bounds
    seed = f"{minx},{miny},{maxx},{maxy},{route_index}"
    rng = random.Random(seed)
    
    waypoints = []
    for _ in range(3): # num_waypoints
        lat = rng.uniform(minx, maxx)
        lon = rng.uniform(miny, maxy)
        waypoints.append((lon, lat))
    
    coordinates_str = ";".join([f"{lon},{lat}" for lon, lat in waypoints])
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coordinates_str}?overview=full&geometries=geojson"
    try:
        response = await client.get(osrm_url, timeout=1.0)
        data = response.json()
        if data.get("code") == "Ok":
            route_coords = data["routes"][0]["geometry"]["coordinates"]
            return team_id, zone, [(lat, lon) for lon, lat in route_coords]
    except Exception:
        pass
    
    # Fallback
    return team_id, zone, [(rng.uniform(minx, maxx), rng.uniform(miny, maxy)) for _ in range(15)]