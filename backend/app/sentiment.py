from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

DEFAULT_MODEL_ID = "daekeun-ml/koelectra-small-v3-nsmc"
MAX_INPUT_LENGTH = 256


@dataclass
class SentimentResult:
    label: str
    score: float


class SentimentAnalyzer:
    def __init__(self) -> None:
        self._pipeline = None
        self._model_id = os.getenv("SENTIMENT_MODEL_ID", DEFAULT_MODEL_ID)
        self._load_transformers_pipeline()

    def _load_transformers_pipeline(self) -> None:
        try:
            from transformers import pipeline

            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self._model_id,
                tokenizer=self._model_id,
                device=-1,
            )
        except Exception:
            self._pipeline = None

    def analyze(self, text: str) -> SentimentResult:
        text = (text or "").strip()
        if not text:
            return SentimentResult(label="neutral", score=0.0)

        if self._pipeline is None:
            raise RuntimeError("Sentiment model is not available")

        output = self._pipeline(
            text,
            truncation=True,
            max_length=MAX_INPUT_LENGTH,
        )[0]
        mapped = self._map_transformer_output(output.get("label", ""), float(output.get("score", 0.0)))
        if mapped is None:
            raise RuntimeError("Unsupported sentiment label returned by model")
        return mapped

    def _map_transformer_output(self, raw_label: str, confidence: float) -> Optional[SentimentResult]:
        normalized = raw_label.strip().lower()
        upper_label = raw_label.strip().upper()

        if normalized in {"positive", "pos", "긍정", "1", "2"} or upper_label in {"LABEL_1", "LABEL_2"}:
            return SentimentResult("positive", min(1.0, max(0.0, confidence)))
        if normalized in {"negative", "neg", "부정", "0"} or upper_label == "LABEL_0":
            return SentimentResult("negative", -min(1.0, max(0.0, confidence)))
        if normalized in {"neutral", "중립"}:
            return SentimentResult("neutral", 0.0)
        return None

analyzer = SentimentAnalyzer()
