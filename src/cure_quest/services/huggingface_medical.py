import logging
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

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


logger = logging.getLogger(__name__)

MEDGEMMA_PROXY_SYSTEM_PROMPT = """
You are operating as MedGemma inside Cure-Quest, but your execution backend is Gemini Flash.

Behave like a careful medical reasoning assistant for chronic-care support:
- Use precise, clinically informed language without pretending to be a licensed clinician.
- Prioritize medication safety, likely interpretations, contraindication awareness, and escalation triggers.
- If the request includes an image, describe only what is visually supportable and clearly state uncertainty.
- Never claim a diagnosis with certainty from limited context.
- Highlight urgent red flags that need immediate clinician or emergency attention.
- Keep the response structured, practical, and calm.
- the response should not contain any of the following keywords: **, ##, or any special symbols. The tone should be point to point in a professional but caring manner, and the analysis should be concise yet thorough.
- they response should be grounded in the patient data provided and should not make assumptions beyond that data & ask the user for if any thing he has consumed lately and what are his current symptoms if the data provided is not sufficient to make a recommendation.

Response style:
1. Start with a short clinical impression.
2. Add key considerations or possible explanations.
3. Add red flags / escalation advice when relevant.
4. End with next-step guidance for the patient or caregiver.

Do not mention Gemini, proxying, model substitution, or internal tooling.
Speak as if you are the MedGemma reasoning layer for Cure-Quest.
Do not claim you lack access to personal files, Drive, tools, or records unless the provided context explicitly says access is unavailable.
""".strip()


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
        if self.settings.medgemma_proxy_enabled:
            return self._medgemma_proxy_generate(prompt=prompt, image_path=image_path, max_new_tokens=max_new_tokens)

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

    def _medgemma_proxy_generate(self, prompt: str, image_path: str | None = None, max_new_tokens: int = 128) -> dict[str, Any]:
        if not self.settings.google_api_key:
            raise RuntimeError("GOOGLE_API_KEY is required when MEDGEMMA_PROXY_ENABLED=true.")

        client = genai.Client(api_key=self.settings.google_api_key)
        contents: list[Any] = []
        if image_path:
            image_part = self._build_gemini_image_part(image_path)
            if image_part is not None:
                contents.append(image_part)
            else:
                logger.info("MedGemma proxy could not attach image %s; passing it as text context only.", image_path)
                contents.append(f"Referenced medical image: {image_path}")

        contents.append(self._build_medgemma_proxy_user_prompt(prompt, image_path=image_path))
        response, resolved_model = self._generate_gemini_with_fallback(
            client=client,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=MEDGEMMA_PROXY_SYSTEM_PROMPT,
                temperature=0.2,
                max_output_tokens=max_new_tokens,
            ),
        )

        return {
            "provider": "gemini-proxy",
            "model": self.settings.medgemma_model_id,
            "prompt": prompt,
            "image_path": image_path,
            "result": {
                "text": (response.text or "").strip(),
                "proxy_model": resolved_model,
                "proxy_enabled": True,
            },
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

    def _build_gemini_image_part(self, image_path: str):
        path = Path(image_path)
        if not path.exists():
            return None
        return types.Part.from_bytes(
            data=path.read_bytes(),
            mime_type=self._mime_for_extension(path.suffix.lower()),
        )

    def _build_medgemma_proxy_user_prompt(self, prompt: str, image_path: str | None = None) -> str:
        image_note = (
            "An image is attached. Use it only as supporting evidence and be explicit about visual uncertainty.\n"
            if image_path
            else ""
        )
        return (
            f"{image_note}"
            "User request:\n"
            f"{prompt}\n\n"
            "Return a medically careful answer with these sections:\n"
            "- Clinical Impression\n"
            "- Key Considerations\n"
            "- Red Flags\n"
            "- Recommended Next Steps\n"
        )

    @staticmethod
    def _mime_for_extension(ext: str) -> str:
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".heic": "image/heic",
            ".gif": "image/gif",
        }
        return mime_map.get(ext, "application/octet-stream")

    def _generate_gemini_with_fallback(self, client: genai.Client, contents: list[Any], config: types.GenerateContentConfig):
        last_error: Exception | None = None
        for model_id in self.settings.gemini_fast_model_candidates:
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=config,
                )
                return response, model_id
            except Exception as error:
                last_error = error
        raise last_error or RuntimeError("Gemini generation failed.")
