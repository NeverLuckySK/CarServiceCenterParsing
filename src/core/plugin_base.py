from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import ServiceItem


class PluginBase(ABC):
    name: str = "Unnamed"
    version: str = "0.0"
    description: str = ""

    @abstractmethod
    def load(self) -> Iterable[ServiceItem]:
        raise NotImplementedError
