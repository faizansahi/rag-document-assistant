import hashlib
import math
import re
from dataclasses import dataclass

DIMENSIONS = 384


def embed(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for token in re.findall(r"[\w-]{2,}", text.lower()):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:2], "big") % DIMENSIONS
        vector[index] += 1.0 if digest[2] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


@dataclass(frozen=True)
class Chunk:
    text: str
    page: int
    index: int


def chunk_pages(pages: list[str], size: int = 900, overlap: int = 150) -> list[Chunk]:
    chunks = []
    for page_number, text in enumerate(pages, 1):
        clean = re.sub(r"\s+", " ", text).strip()
        start = 0
        index = 0
        while start < len(clean):
            end = min(start + size, len(clean))
            chunks.append(Chunk(clean[start:end], page_number, index))
            index += 1
            if end == len(clean):
                break
            start = end - overlap
    return chunks


def grounded_answer(question: str, hits: list[dict], threshold: float = 0.18) -> dict:
    if not hits or hits[0]["score"] < threshold:
        return {
            "answer": "Insufficient evidence in the uploaded documents.",
            "confidence": "low",
            "citations": [],
        }
    terms = set(re.findall(r"[\w-]{3,}", question.lower()))
    sentences = []
    for hit in hits:
        candidates = re.split(r"(?<=[.!?])\s+", hit["text"])
        best = max(
            candidates, key=lambda sentence: len(terms & set(sentence.lower().split())), default=""
        )
        if best and best not in sentences:
            sentences.append(best)
    return {
        "answer": " ".join(sentences[:3]),
        "confidence": "high" if hits[0]["score"] >= 0.35 else "medium",
        "citations": [
            {"filename": h["filename"], "page": h["page"], "score": round(h["score"], 3)}
            for h in hits
        ],
    }
