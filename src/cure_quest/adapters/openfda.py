import re

import httpx

from cure_quest.config import get_settings


class OpenFDAAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.fda.gov/drug/label.json"

    def lookup_drug_label(self, medication_name: str) -> dict:
        with httpx.Client(timeout=20.0) as client:
            for search_query in self._build_search_queries(medication_name):
                payload = self._fetch_label_payload(client, search_query)
                if payload is None:
                    continue

                results = payload.get("results", [])
                if results:
                    return self._format_label_result(medication_name, results[0])

        return {"medication_name": medication_name, "found": False, "label": None}

    def _fetch_label_payload(self, client: httpx.Client, search_query: str) -> dict | None:
        params = {
            "search": search_query,
            "limit": 1,
        }
        if self.settings.openfda_api_key:
            params["api_key"] = self.settings.openfda_api_key

        response = client.get(self.base_url, params=params)
        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def _build_search_queries(self, medication_name: str) -> list[str]:
        search_terms: list[str] = []
        cleaned_name = " ".join(medication_name.split())
        if cleaned_name:
            search_terms.append(cleaned_name)

        normalized_name = re.sub(r"\s+\d.*$", "", cleaned_name).strip(" ,-/")
        normalized_name = re.sub(
            r"\b(tablet|tablets|capsule|capsules|cream|ointment|gel|solution|suspension|injection|patch|spray|drops)\b$",
            "",
            normalized_name,
            flags=re.IGNORECASE,
        ).strip(" ,-/")
        if normalized_name and normalized_name not in search_terms:
            search_terms.append(normalized_name)

        return [
            f'openfda.brand_name:"{term}" OR openfda.generic_name:"{term}"'
            for term in search_terms
        ]

    def _format_label_result(self, medication_name: str, result: dict) -> dict:
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
