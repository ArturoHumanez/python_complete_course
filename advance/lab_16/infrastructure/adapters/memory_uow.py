from advance.lab_16.infrastructure.adapters.memory_repo import (
    InMemoryOrderRepository,
)


class InMemoryUnitOfWork:
    def __init__(self, repo: InMemoryOrderRepository) -> None:
        self.orders = repo
        self._committed = False

    def __enter__(self):
        self._committed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._committed and exc_type is not None:
            self.rollback()
        return False

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._committed = False