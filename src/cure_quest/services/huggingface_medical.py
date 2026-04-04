from pathlib import Path
from typing import Any

from cure_quest.config import get_settings

try:  # pragma: no cover - optional dependency path
    import torch
except ImportError:  # pragma: no cover - optional dependency path
    torch = None

try:  # pragma: no cover - optional dependency path
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency path
    Image = None

try:  # pragma: no cover - optional dependency path
    from transformers import (
        AutoModelForImageTextToText,
        AutoModelForZeroShotImageClassification,
        AutoProcessor,
        pipeline,
    )
except ImportError:  # pragma: no cover - optional dependency path
    AutoModelForImageTextToText = None
    AutoModelForZeroShotImageClassification = None
    AutoProcessor = None
    pipeline = None


class HuggingFaceMedicalService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._medgemma_pipeline = None
        self._medsiglip_pipeline = None
        self._medsiglip_processor = None
        self._medsiglip_model = None

    def is_configured(self) -> bool:
        return (
            self.settings.medical_model_backend == "huggingface"
            and bool(self.settings.huggingface_hub_token)
            and pipeline is not None
            and AutoProcessor is not None
            and AutoModelForZeroShotImageClassification is not None
            and AutoModelForImageTextToText is not None
            and Image is not None
            and torch is not None
        )

    def medgemma_generate(self, prompt: str, image_path: str | None = None, max_new_tokens: int = 128) -> dict[str, Any]:
        self._ensure_configured()
        pipe = self._get_medgemma_pipeline()

        content: list[dict[str, str]] = []
        if image_path:
            content.append({"type": "image", "url": self._to_image_url(image_path)})
        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]

        result = pipe(text=messages, max_new_tokens=max_new_tokens)
        return {
            "provider": "huggingface",
            "model": self.settings.medgemma_model_id,
            "prompt": prompt,
            "image_path": image_path,
            "result": result,
        }

    def medsiglip_classify(self, image_path: str, candidate_labels: list[str]) -> dict[str, Any]:
        self._ensure_configured()
        pipe = self._get_medsiglip_pipeline()
        result = pipe(self._to_image_url(image_path), candidate_labels=candidate_labels)
        return {
            "provider": "huggingface",
            "model": self.settings.medsiglip_model_id,
            "image_path": image_path,
            "candidate_labels": candidate_labels,
            "result": result,
        }

    def medsiglip_embed(self, image_path: str | None = None, text: str | None = None) -> dict[str, Any]:
        self._ensure_configured()
        processor, model = self._get_medsiglip_components()

        if image_path:
            image = self._load_local_image(image_path)
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                vector = model.get_image_features(**inputs)[0].cpu().tolist()
            return {
                "provider": "huggingface",
                "model": self.settings.medsiglip_model_id,
                "modality": "image",
                "image_path": image_path,
                "embedding_vector": vector,
            }

        if text:
            inputs = processor(text=[text], return_tensors="pt", padding=True)
            with torch.no_grad():
                vector = model.get_text_features(**inputs)[0].cpu().tolist()
            return {
                "provider": "huggingface",
                "model": self.settings.medsiglip_model_id,
                "modality": "text",
                "text": text,
                "embedding_vector": vector,
            }

        raise ValueError("Either image_path or text must be provided for MedSigLIP embeddings.")

    def _ensure_configured(self) -> None:
        if not self.is_configured():
            raise RuntimeError(
                "Hugging Face medical execution is not ready. Set MEDICAL_MODEL_BACKEND=huggingface, "
                "provide HUGGINGFACE_HUB_TOKEN, and install the optional model dependencies."
            )

    def _get_medgemma_pipeline(self):
        if self._medgemma_pipeline is None:
            self._medgemma_pipeline = pipeline(
                "image-text-to-text",
                model=self.settings.medgemma_model_id,
                token=self.settings.huggingface_hub_token,
            )
        return self._medgemma_pipeline

    def _get_medsiglip_pipeline(self):
        if self._medsiglip_pipeline is None:
            self._medsiglip_pipeline = pipeline(
                "zero-shot-image-classification",
                model=self.settings.medsiglip_model_id,
                token=self.settings.huggingface_hub_token,
            )
        return self._medsiglip_pipeline

    def _get_medsiglip_components(self):
        if self._medsiglip_processor is None or self._medsiglip_model is None:
            self._medsiglip_processor = AutoProcessor.from_pretrained(
                self.settings.medsiglip_model_id,
                token=self.settings.huggingface_hub_token,
            )
            self._medsiglip_model = AutoModelForZeroShotImageClassification.from_pretrained(
                self.settings.medsiglip_model_id,
                token=self.settings.huggingface_hub_token,
            )
        return self._medsiglip_processor, self._medsiglip_model

    def _load_local_image(self, image_path: str):
        if Image is None:
            raise RuntimeError("Pillow is required to load local images.")
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        return Image.open(path).convert("RGB")

    def _to_image_url(self, image_path: str) -> str:
        path = Path(image_path)
        if path.exists():
            return str(path.resolve())
        return image_path
