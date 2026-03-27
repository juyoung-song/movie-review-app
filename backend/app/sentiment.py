from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Optional
from urllib.parse import quote

import requests

DEFAULT_MODEL_ID = "daekeun-ml/koelectra-small-v3-nsmc"
MAX_INPUT_LENGTH = 512


@dataclass
class SentimentResult:
    label: str
    score: float


class SentimentAnalyzer:
    def __init__(self) -> None:
        self._model_id = os.getenv("HF_API_MODEL_ID", DEFAULT_MODEL_ID)
        encoded_model_id = quote(self._model_id, safe="/")
        default_url = f"https://router.huggingface.co/hf-inference/models/{encoded_model_id}"
        self._api_url = os.getenv("HF_API_URL", default_url)
        self._timeout = float(os.getenv("HF_API_TIMEOUT", "30"))
        self._session = requests.Session()
        self._token = os.getenv("HF_API_TOKEN") or os.getenv("HF_TOKEN")

    def analyze(self, text: str) -> SentimentResult:
        text = (text or "").strip()
        if not text:
            return SentimentResult(label="neutral", score=0.0)

        output = self._request_inference(text[:MAX_INPUT_LENGTH])
        raw_label, confidence = self._extract_label_and_score(output)
        mapped = self._map_transformer_output(raw_label, confidence)
        if mapped is None:
            raise RuntimeError("Unsupported sentiment label returned by model")
        return mapped

    def _request_inference(self, text: str) -> Any:
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        payload = {
            "inputs": text,
            "options": {"wait_for_model": True},
            "parameters": {"top_k": 3},
        }

        try:
            response = self._session.post(
                self._api_url,
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Hugging Face API request failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(f"Hugging Face API invalid response: {response.text[:200]}") from exc

        if response.status_code >= 400:
            error_text = data.get("error") if isinstance(data, dict) else str(data)
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {error_text}")

        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(f"Hugging Face API error: {data['error']}")

        return data

    def _extract_label_and_score(self, output: Any) -> tuple[str, float]:
        # Common shapes:
        # - [{"label":"1","score":0.99}]
        # - [[{"label":"1","score":0.99}, ...]]
        if isinstance(output, dict):
            if "label" in output:
                return str(output.get("label", "")), float(output.get("score", 0.0))
            raise RuntimeError(f"Unexpected inference response: {output}")

        if not isinstance(output, list) or not output:
            raise RuntimeError(f"Unexpected inference response: {output}")

        candidates = output
        if isinstance(output[0], list):
            candidates = output[0]

        if not isinstance(candidates, list) or not candidates or not isinstance(candidates[0], dict):
            raise RuntimeError(f"Unexpected inference response: {output}")

        best = max(candidates, key=lambda item: float(item.get("score", 0.0)))
        return str(best.get("label", "")), float(best.get("score", 0.0))

    def _map_transformer_output(self, raw_label: str, confidence: float) -> Optional[SentimentResult]:
        normalized = raw_label.strip().lower()
        upper_label = raw_label.strip().upper()

        if normalized.startswith("1 star") or normalized.startswith("2 star"):
            return SentimentResult("negative", -min(1.0, max(0.0, confidence)))
        if normalized.startswith("4 star") or normalized.startswith("5 star"):
            return SentimentResult("positive", min(1.0, max(0.0, confidence)))
        if normalized.startswith("3 star"):
            return SentimentResult("neutral", 0.0)

        if normalized in {"positive", "pos", "긍정", "1", "2"} or upper_label in {"LABEL_1", "LABEL_2"}:
            return SentimentResult("positive", min(1.0, max(0.0, confidence)))
        if normalized in {"negative", "neg", "부정", "0"} or upper_label == "LABEL_0":
            return SentimentResult("negative", -min(1.0, max(0.0, confidence)))
        if normalized in {"neutral", "중립"}:
            return SentimentResult("neutral", 0.0)
        return None

analyzer = SentimentAnalyzer()
