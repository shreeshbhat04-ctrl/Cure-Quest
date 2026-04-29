import re
import httpx

from cure_quest.config import get_settings


class WikipediaAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary"

    def lookup_drug_label(self, medication_name: str) -> dict:
        with httpx.Client(timeout=20.0) as client:
            for term in self._build_search_terms(medication_name):
                data = self._fetch_summary(client, term)
                if data:
                    return self._format_result(medication_name, data)

        return {"medication_name": medication_name, "found": False, "label": None}

    def _fetch_summary(self, client: httpx.Client, term: str) -> dict | None:
        url = f"{self.base_url}/{term}"
        response = client.get(url)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def _build_search_terms(self, medication_name: str) -> list[str]:
        cleaned = " ".join(medication_name.split())

        normalized = re.sub(r"\s+\d.*$", "", cleaned).strip(" ,-/")
        normalized = re.sub(
            r"\b(tablet|tablets|capsule|capsules|cream|ointment|gel|solution|suspension|injection|patch|spray|drops)\b$",
            "",
            normalized,
            flags=re.IGNORECASE,
        ).strip(" ,-/")

        terms = [cleaned]
        if normalized and normalized != cleaned:
            terms.append(normalized)

        # Wikipedia prefers underscores instead of spaces
        return [term.replace(" ", "_") for term in terms]

    def _format_result(self, medication_name: str, data: dict) -> dict:
        label = {
            "title": data.get("title"),
            "description": data.get("description"),
            "summary": data.get("extract"),
            "source_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        }

        return {
            "medication_name": medication_name,
            "found": True,
            "label": label,
        }
