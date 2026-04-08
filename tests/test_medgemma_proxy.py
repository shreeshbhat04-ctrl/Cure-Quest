from types import SimpleNamespace

from cure_quest.services.huggingface_medical import HuggingFaceMedicalService


def test_medgemma_proxy_uses_flash_but_preserves_medgemma_label(monkeypatch) -> None:
    captured: dict = {}

    class DummyModels:
        def generate_content(self, *, model, contents, config):
            captured["model"] = model
            captured["contents"] = contents
            captured["config"] = config
            return SimpleNamespace(text="Clinical Impression\nStable summary")

    class DummyClient:
        def __init__(self, api_key: str) -> None:
            captured["api_key"] = api_key
            self.models = DummyModels()

    monkeypatch.setattr("cure_quest.services.huggingface_medical.genai.Client", DummyClient)

    service = HuggingFaceMedicalService()
    service.settings.google_api_key = "test-key"
    service.settings.medgemma_proxy_enabled = True
    service.settings.gemini_fast_model_id = "gemini-3.1-flash-lite-preview"
    service.settings.medgemma_model_id = "google/medgemma-1.5-4b-it"

    result = service.medgemma_generate(prompt="Review this prescription risk.", max_new_tokens=200)

    assert captured["api_key"] == "test-key"
    assert captured["model"] == "gemini-3.1-flash-lite-preview"
    assert result["provider"] == "gemini-proxy"
    assert result["model"] == "google/medgemma-1.5-4b-it"
    assert result["result"]["proxy_model"] == "gemini-3.1-flash-lite-preview"
    assert result["result"]["proxy_enabled"] is True
    assert "Clinical Impression" in result["result"]["text"]
    assert "Review this prescription risk." in captured["contents"][-1]
