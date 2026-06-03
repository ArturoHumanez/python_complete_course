from __future__ import annotations

from typing import Any

from advance.lab_16.infrastructure.adapters.memory_repo import (
    InMemoryOrderRepository,
)


class InMemoryUnitOfWork:
    def __init__(self, repo: Any) -> None:
        self.orders:Any  = repo
        self._committed = False

    def __enter__(self) -> "InMemoryUnitOfWork":
        self._committed = False
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if not self._committed and exc_type is not None:
            self.rollback()
        return False

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._committed = False