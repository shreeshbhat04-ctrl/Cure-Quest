import httpx

from cure_quest.config import get_settings


class PharmacySearchAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def search_nearby_pharmacies(self, location_query: str) -> dict:
        if not self.settings.google_maps_api_key:
            return {"pharmacies": [], "provider": "disabled"}

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.settings.google_maps_api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.googleMapsUri",
        }
        body = {
            "textQuery": f"pharmacy near {location_query}",
        }
        with httpx.Client(timeout=20.0) as client:
            response = client.post(self.base_url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()

        places = payload.get("places", [])
        return {
            "provider": "google_places",
            "pharmacies": [
                {
                    "name": place.get("displayName", {}).get("text"),
                    "address": place.get("formattedAddress"),
                    "maps_url": place.get("googleMapsUri"),
                }
                for place in places
            ],
        }
