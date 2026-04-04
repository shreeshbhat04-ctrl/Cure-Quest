import httpx

from cure_quest.config import get_settings


class OpenFDAAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.fda.gov/drug/label.json"

    def lookup_drug_label(self, medication_name: str) -> dict:
        params = {
            "search": f'openfda.brand_name:"{medication_name}" openfda.generic_name:"{medication_name}"',
            "limit": 1,
        }
        if self.settings.openfda_api_key:
            params["api_key"] = self.settings.openfda_api_key

        with httpx.Client(timeout=20.0) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        results = payload.get("results", [])
        if not results:
            return {"medication_name": medication_name, "found": False, "label": None}

        result = results[0]
        return {
            "medication_name": medication_name,
            "found": True,
            "label": {
                "manufacturer_name": result.get("openfda", {}).get("manufacturer_name"),
                "brand_name": result.get("openfda", {}).get("brand_name"),
                "generic_name": result.get("openfda", {}).get("generic_name"),
                "indications_and_usage": result.get("indications_and_usage"),
                "warnings": result.get("warnings"),
            },
        }
