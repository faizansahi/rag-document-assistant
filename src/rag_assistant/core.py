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
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
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
    terms = set(re.findall(r"[\w-]{3,}", question.lower()))
    sentences: list[str] = []
    citations: list[dict] = []
    scores: list[float] = []
    for hit in sorted(hits, key=lambda item: item["score"], reverse=True):
        if hit["score"] < threshold:
            continue
        candidates = re.split(r"(?<=[.!?])\s+", hit["text"])

        def overlap(sentence: str) -> int:
            return len(terms & set(re.findall(r"[\w-]{3,}", sentence.lower())))

        best = max(candidates, key=overlap, default="")
        if not best or not overlap(best) or best in sentences:
            continue
        sentences.append(best)
        citations.append(
            {"filename": hit["filename"], "page": hit["page"], "score": round(hit["score"], 3)}
        )
        scores.append(hit["score"])
        if len(sentences) == 3:
            break
    if not sentences:
        return {
            "answer": "Insufficient evidence in the uploaded documents.",
            "confidence": "low",
            "citations": [],
        }
    return {
        "answer": " ".join(sentences),
        "confidence": "high" if min(scores) >= 0.35 else "medium",
        "citations": citations,
    }
