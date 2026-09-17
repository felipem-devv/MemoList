"""Modelos de dados para o MemoList."""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any
import uuid


@dataclass
class ReviewRecord:
    date: str  # ISO-8601 string
    grade: int  # 1 (Errei), 3 (Difícil), 4 (Bom), 5 (Fácil)
    items_correct: int
    items_total: int
    interval_days: int
    ease_factor: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewRecord":
        return cls(
            date=data["date"],
            grade=int(data["grade"]),
            items_correct=int(data.get("items_correct", 0)),
            items_total=int(data.get("items_total", 0)),
            interval_days=int(data.get("interval_days", 1)),
            ease_factor=float(data.get("ease_factor", 2.5)),
        )


@dataclass
class SRSData:
    repetitions: int = 0
    interval_days: int = 0
    ease_factor: float = 2.5
    next_review: str = field(default_factory=lambda: date.today().isoformat())
    last_reviewed: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SRSData":
        return cls(
            repetitions=int(data.get("repetitions", 0)),
            interval_days=int(data.get("interval_days", 0)),
            ease_factor=float(data.get("ease_factor", 2.5)),
            next_review=data.get("next_review", date.today().isoformat()),
            last_reviewed=data.get("last_reviewed"),
        )

    @property
    def next_review_date(self) -> date:
        return date.fromisoformat(self.next_review)

    @property
    def is_due(self) -> bool:
        return date.today() >= self.next_review_date

    @property
    def days_until_due(self) -> int:
        delta = (self.next_review_date - date.today()).days
        return delta


@dataclass
class ItemList:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    items: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    srs: SRSData = field(default_factory=SRSData)
    review_history: list[ReviewRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "items": list(self.items),
            "created_at": self.created_at,
            "srs": self.srs.to_dict(),
            "review_history": [record.to_dict() for record in self.review_history],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ItemList":
        srs_raw = data.get("srs", {})
        srs_obj = SRSData.from_dict(srs_raw) if isinstance(srs_raw, dict) else SRSData()
        
        history_raw = data.get("review_history", [])
        history_objs = [
            ReviewRecord.from_dict(rec) for rec in history_raw if isinstance(rec, dict)
        ]

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", "Sem título"),
            description=data.get("description", ""),
            items=list(data.get("items", [])),
            created_at=data.get("created_at", datetime.now().isoformat()),
            srs=srs_obj,
            review_history=history_objs,
        )

    @property
    def is_due(self) -> bool:
        return self.srs.is_due

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def status_display(self) -> str:
        if self.srs.repetitions == 0 and self.srs.last_reviewed is None:
            return "Nova lista"
        days = self.srs.days_until_due
        if days < 0:
            return f"Atrasada ({abs(days)}d)"
        elif days == 0:
            return "Devida hoje"
        elif days == 1:
            return "Amanhã"
        else:
            return f"Em {days} dias"
