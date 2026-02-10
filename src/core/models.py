from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ServiceItem:
    name: str
    price: float
    category: Optional[str]
    source: str
    url: Optional[str] = None
