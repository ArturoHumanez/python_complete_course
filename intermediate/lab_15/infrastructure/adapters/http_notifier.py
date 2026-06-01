import logging

logger = logging.getLogger(__name__)


class LogNotifier:
    """Adaptador de notificación que solo loggea — para desarrollo."""

    def send(self, to: str, message: str) -> bool:
        logger.info("Notificación a %s: %s", to, message)
        return True


class FakeNotifier:
    """Para tests — registra sin enviar."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, to: str, message: str) -> bool:
        self.sent.append({"to": to, "message": message})
        return True