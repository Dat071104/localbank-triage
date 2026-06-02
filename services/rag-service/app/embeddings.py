from __future__ import annotations

import math
import re
import unicodedata
from hashlib import sha256


TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


def normalize_text(text: str) -> str:
    lowered = text.lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    return normalized.encode("ascii", "ignore").decode("ascii")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(normalize_text(text))


def embed_text(text: str, vector_size: int = 64) -> list[float]:
    vector = [0.0] * vector_size
    tokens = tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        digest = sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % vector_size
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
