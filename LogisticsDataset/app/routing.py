import requests
import os


ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"


def get_routes(
    origin_lon,
    origin_lat,
    destination_lon,
    destination_lat
):
    """
    Get alternative driving routes between two coordinates.

    Returns a list of routes containing:
    - route name
    - distance in km
    - duration in minutes
    - geometry
    """

    api_key = os.getenv("ORS_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ORS_API_KEY environment variable is not set."
        )

    coordinates = [
        [origin_lon, origin_lat],
        [destination_lon, destination_lat]
    ]

    params = {
        "api_key": api_key,
        "start": f"{origin_lon},{origin_lat}",
        "end": f"{destination_lon},{destination_lat}"
    }

    response = requests.get(
        ORS_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    routes = []

    for i, route in enumerate(data.get("features", []), start=1):

        summary = route["properties"]["summary"]

        routes.append({
            "route": f"Route {chr(64 + i)}",
            "distance_km": summary["distance"] / 1000,
            "routing_duration_minutes": summary["duration"] / 60,
            "geometry": route["geometry"]
        })

    return routes