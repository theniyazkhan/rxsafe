"""OCR and VLM recognition wrappers.

Provides unified interface for extracting text/medication lists from prescription images
using traditional OCR engines (e.g. Tesseract) and Vision-Language Models (VLMs).
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
from PIL import Image


class OCRWrapper:
    """Wrapper around Tesseract OCR engine."""

    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def extract_text(self, image_input: Union[str, Path, Image.Image]) -> str:
        """Extract raw text from prescription image using pytesseract."""
        try:
            import pytesseract
            if isinstance(image_input, (str, Path)):
                img = Image.open(image_input)
            else:
                img = image_input
            return pytesseract.image_to_string(img, lang=self.lang)
        except ImportError:
            # Fallback if pytesseract engine is not available in environment
            return "[OCR Engine Not Installed]"

    def extract_medication_list(self, image_input: Union[str, Path, Image.Image]) -> List[str]:
        """Extract candidate medication names from image."""
        raw_text = self.extract_text(image_input)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return lines


class VLMWrapper:
    """Wrapper for Vision-Language Models (e.g. HuggingFace / VLM APIs)."""

    def __init__(self, model_name: str = "google/paligemma-3b-pt-224"):
        self.model_name = model_name
        self._model = None
        self._processor = None

    def load_model(self) -> None:
        """Lazy loader for VLM weights."""
        if self._model is None:
            # Placeholder for loading VLM transformer / API client
            pass

    def extract_medications(self, image_input: Union[str, Path, Image.Image]) -> List[str]:
        """Extract structured list of medications using VLM prompt."""
        self.load_model()
        # Fallback / mock return signature
        return []
