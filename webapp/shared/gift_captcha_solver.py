"""Shared ONNX-based captcha solver used by the web backend.

This module is adapted from the original Discord bot implementation located in
``cogs/gift_captchasolver.py``. Discord specific types have been removed so the
logic can be reused by the FastAPI backend.
"""

from __future__ import annotations

import io
import json
import logging
import logging.handlers
import os
import time
from dataclasses import dataclass
from typing import Optional

try:
    import onnxruntime as ort  # type: ignore
    import numpy as np  # type: ignore
    from PIL import Image  # type: ignore

    ONNX_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency during CI
    ort = None  # type: ignore
    np = None  # type: ignore
    Image = None  # type: ignore
    ONNX_AVAILABLE = False


@dataclass
class CaptchaResult:
    """Container describing the outcome of a captcha solving attempt."""

    code: Optional[str]
    success: bool
    method: str
    confidence: float
    duration: float


class GiftCaptchaSolver:
    """ONNX based captcha solver used for gift code redemption."""

    def __init__(self, save_images: int = 0) -> None:
        self.save_images_mode = save_images
        self.onnx_session = None
        self.model_metadata = None
        self.is_initialized = False

        self.logger = logging.getLogger("gift_solver")
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.INFO)
            self.logger.propagate = False
            log_dir = "log"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "gift_solver.txt")
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=3 * 1024 * 1024, backupCount=3, encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            self.logger.addHandler(handler)

        self.captcha_dir = "captcha_images"
        os.makedirs(self.captcha_dir, exist_ok=True)

        self._initialize_onnx_model()

        self.stats = {
            "total_attempts": 0,
            "successful_decodes": 0,
            "failures": 0,
        }
        self.reset_run_stats()

    # ------------------------------------------------------------------
    # Public helpers
    def reset_run_stats(self) -> None:
        self.run_stats = {
            "total_attempts": 0,
            "successful_decodes": 0,
            "failures": 0,
            "start_time": time.time(),
        }

    def get_run_stats_report(self) -> str:
        duration = time.time() - self.run_stats["start_time"]
        success_rate = 0.0
        if self.run_stats["total_attempts"] > 0:
            success_rate = (
                self.run_stats["successful_decodes"]
                / self.run_stats["total_attempts"]
            ) * 100

        report = [
            "\n=== Captcha Solver Statistics ===",
            f"Total captcha attempts: {self.run_stats['total_attempts']}",
            f"Successful decodes: {self.run_stats['successful_decodes']}",
            f"Failures: {self.run_stats['failures']}",
            f"Success rate: {success_rate:.2f}%",
            f"Processing time: {duration:.2f} seconds",
            "==========================================",
        ]
        return "\n".join(report)

    # ------------------------------------------------------------------
    async def solve_captcha(
        self, image_bytes: bytes, fid: Optional[str] = None, attempt: int = 0
    ) -> CaptchaResult:
        """Attempts to solve a captcha image using the ONNX model."""

        if not self.is_initialized or not self.onnx_session or not self.model_metadata:
            self.logger.error(
                "ONNX model not initialized. Cannot solve captcha for ID %s.", fid
            )
            return CaptchaResult(None, False, "ONNX", 0.0, 0.0)

        self.stats["total_attempts"] += 1
        self.run_stats["total_attempts"] += 1
        start_time = time.time()

        image_array = self._preprocess_image(image_bytes)
        if image_array is None:
            self.logger.error("Failed to preprocess captcha for %s", fid)
            self.stats["failures"] += 1
            self.run_stats["failures"] += 1
            return CaptchaResult(None, False, "ONNX", 0.0, time.time() - start_time)

        try:
            input_name = self.onnx_session.get_inputs()[0].name
            outputs = self.onnx_session.run(None, {input_name: image_array})

            characters = []
            confidences = []
            for position, logits in enumerate(outputs):
                probs = self._softmax(logits[0])
                predicted_index = int(probs.argmax())
                predicted_char = self.model_metadata["character_set"][predicted_index]
                confidence = float(probs[predicted_index])

                characters.append(predicted_char)
                confidences.append(confidence)

                self.logger.debug(
                    "Position %s predicted %s with confidence %.4f",
                    position,
                    predicted_char,
                    confidence,
                )

            solved_code = "".join(characters)
            average_confidence = sum(confidences) / len(confidences)

            self.stats["successful_decodes"] += 1
            self.run_stats["successful_decodes"] += 1

            duration = time.time() - start_time
            self.logger.info(
                "Solved captcha for %s in %.2fs with confidence %.2f",
                fid,
                duration,
                average_confidence,
            )
            return CaptchaResult(
                solved_code, True, "ONNX", average_confidence, duration
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            duration = time.time() - start_time
            self.logger.exception("Failed to solve captcha for %s: %s", fid, exc)
            self.stats["failures"] += 1
            self.run_stats["failures"] += 1
            return CaptchaResult(None, False, "ONNX", 0.0, duration)

    # ------------------------------------------------------------------
    def _initialize_onnx_model(self) -> None:
        if not ONNX_AVAILABLE:
            self.logger.error(
                "ONNX Runtime or required libraries not found. Captcha solving disabled."
            )
            self.is_initialized = False
            return

        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            models_dir = os.path.join(base_dir, "models")
            model_path = os.path.join(models_dir, "captcha_model.onnx")
            metadata_path = os.path.join(models_dir, "captcha_model_metadata.json")

            if not os.path.exists(model_path) or not os.path.exists(metadata_path):
                self.logger.error("Captcha model files are missing from %s", models_dir)
                self.is_initialized = False
                return

            self.onnx_session = ort.InferenceSession(model_path)
            with open(metadata_path, "r", encoding="utf-8") as fh:
                self.model_metadata = json.load(fh)

            height, width = self.model_metadata["input_shape"][1:3]
            dummy_img = np.random.rand(1, 1, height, width).astype(np.float32)
            input_name = self.onnx_session.get_inputs()[0].name
            outputs = self.onnx_session.run(None, {input_name: dummy_img})

            if len(outputs) != 4:
                self.logger.error(
                    "ONNX model test failed. Expected 4 outputs, got %s", len(outputs)
                )
                self.is_initialized = False
            else:
                self.logger.info("ONNX model loaded successfully")
                self.is_initialized = True
        except Exception as exc:  # pragma: no cover
            self.logger.exception("Failed during ONNX model initialization: %s", exc)
            self.onnx_session = None
            self.model_metadata = None
            self.is_initialized = False

    # ------------------------------------------------------------------
    def _preprocess_image(self, image_bytes: bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != "L":
                image = image.convert("L")

            height, width = self.model_metadata["input_shape"][1:3]
            image = image.resize((width, height), Image.LANCZOS)

            image_array = np.array(image, dtype=np.float32)
            mean = self.model_metadata["normalization"]["mean"][0]
            std = self.model_metadata["normalization"]["std"][0]
            image_array = (image_array / 255.0 - mean) / std

            image_array = image_array[np.newaxis, np.newaxis, :, :]
            return image_array
        except Exception as exc:
            self.logger.error("Error preprocessing image: %s", exc)
            return None

    def _softmax(self, logits):
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / exp_logits.sum(axis=-1, keepdims=True)


__all__ = ["GiftCaptchaSolver", "CaptchaResult", "ONNX_AVAILABLE"]
