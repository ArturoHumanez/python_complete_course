import logging

from advance.lab_18.config import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def verify_settings() -> None:
    """Verifica que la configuración cargue correctamente."""
    # Sin .env usa defaults
    settings = Settings()

    logger.info("=== Configuración cargada ===")
    logger.info("  API Title: %s", settings.api_title)
    logger.info("  Debug: %s", settings.debug)
    logger.info("  DB URL: %s", settings.database_url)
    logger.info("  Token expire: %d min", settings.access_token_expire_minutes)

    # Nunca loggear el secret completo
    masked = settings.secret_key[:4] + "****"
    logger.info("  Secret key: %s", masked)

    # Validar que no sea el default en producción
    if not settings.debug and settings.secret_key == "dev-secret-change-me":
        logger.warning("SECRET_KEY tiene el valor default — " "NO usar en producción")


if __name__ == "__main__":
    verify_settings()
