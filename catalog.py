import json
import re
from dataclasses import dataclass, field

KEY_TYPE_MAP = {
    "Ability & Aptitude": "A",
    "Assessment Exercises": "E",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S",
}


@dataclass
class Assessment:
    entity_id: str
    name: str
    url: str
    description: str
    keys: list = field(default_factory=list)
    job_levels: list = field(default_factory=list)
    languages: list = field(default_factory=list)
    duration: str = ""
    remote: str = ""
    adaptive: str = ""

    @property
    def test_type(self) -> str:
        codes = [KEY_TYPE_MAP.get(k, k[0].upper()) for k in self.keys]
        return ",".join(codes) if codes else "K"

    def to_compact(self) -> str:
        return f"- {self.name} [{self.test_type}] {self.url}"

    def to_full(self) -> str:
        langs = self.languages[:5]
        lang_str = ", ".join(langs)
        if len(self.languages) > 5:
            lang_str += f" (+{len(self.languages) - 5} more)"
        return (
            f"Name: {self.name}\n"
            f"URL: {self.url}\n"
            f"Test Type: {self.test_type} ({', '.join(self.keys)})\n"
            f"Job Levels: {', '.join(self.job_levels) or '—'}\n"
            f"Duration: {self.duration or '—'}\n"
            f"Remote: {self.remote} | Adaptive: {self.adaptive}\n"
            f"Languages: {lang_str or '—'}\n"
            f"Description: {self.description}"
        )


class Catalog:
    def __init__(self, path: str = "dataset.json"):
        from rank_bm25 import BM25Okapi

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        self.items: list[Assessment] = []
        for d in data:
            self.items.append(
                Assessment(
                    entity_id=d["entity_id"],
                    name=d["name"],
                    url=d["link"],
                    description=d.get("description", ""),
                    keys=d.get("keys", []),
                    job_levels=d.get("job_levels", []),
                    languages=d.get("languages", []),
                    duration=d.get("duration", ""),
                    remote=d.get("remote", ""),
                    adaptive=d.get("adaptive", ""),
                )
            )

        corpus = [
            re.findall(
                r"\w+",
                f"{a.name} {a.description} {' '.join(a.keys)} {' '.join(a.job_levels)}".lower(),
            )
            for a in self.items
        ]
        self.bm25 = BM25Okapi(corpus)
        self.url_set = {a.url for a in self.items}
        self._compact = "\n".join(a.to_compact() for a in self.items)

        # Anchor assessments: always include these in retrieval for coverage
        _anchor_names = {
            "Occupational Personality Questionnaire OPQ32r",
            "SHL Verify Interactive G+",
        }
        self._anchors = [a for a in self.items if a.name in _anchor_names]

    def _bm25_search(self, query: str, top_k: int) -> list:
        tokens = re.findall(r"\w+", query.lower())
        scores = self.bm25.get_scores(tokens)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.items[i] for i in ranked[:top_k] if scores[i] > 0]

    def search(self, query: str, top_k: int = 20) -> list:
        """Multi-pass retrieval: role-specific BM25 + anchors + personality & cognitive."""
        primary = self._bm25_search(query, top_k=15)
        seen = {a.url for a in primary}

        # Always include anchor assessments (OPQ32r, Verify G+)
        anchors = [a for a in self._anchors if a.url not in seen]
        seen.update(a.url for a in anchors)

        # Supplement with top cognitive/ability assessments
        cognitive = [
            a for a in self._bm25_search(
                "cognitive ability numerical verbal inductive reasoning verify aptitude", top_k=8
            )
            if a.url not in seen
        ]

        combined = primary + anchors + cognitive[:2]
        return combined[:top_k] if combined else self.items[:top_k]

    @property
    def compact(self) -> str:
        return self._compact

    def is_valid_url(self, url: str) -> bool:
        return url in self.url_set
