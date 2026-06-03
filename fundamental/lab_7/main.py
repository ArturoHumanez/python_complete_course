import logging
import time
import functools
from pathlib import Path
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# === Decorador de reintentos (reutilizado del lab 3) ===


def retry(
    max_attempts: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    if attempt == max_attempts:
                        logger.error(
                            "Falló después de %d intentos: %s", max_attempts, e
                        )
                        raise
                    logger.warning(
                        "Intento %d falló: %s — reintentando en %.1fs...",
                        attempt,
                        e,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    return decorator


# === Cliente HTTP robusto ===


class OrdersApiClient:
    """Cliente para consumir una API de ejemplo."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )
        logger.info("Cliente HTTP creado — base_url: %s", base_url)

    def close(self) -> None:
        self._client.close()
        logger.info("Cliente HTTP cerrado")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @retry(max_attempts=3, initial_delay=0.5)
    def get_post(self, post_id: int) -> dict:
        """Obtiene un post por ID."""
        response = self._client.get(f"/posts/{post_id}")
        response.raise_for_status()
        return response.json()

    @retry(max_attempts=3, initial_delay=0.5)
    def get_posts(self, user_id: int) -> dict:
        """Obtiene posts por ID de usuario."""
        response = self._client.get(f"/posts?userId={user_id}")
        response.raise_for_status()
        return response.json()

    @retry(max_attempts=3, initial_delay=0.5)
    def create_post(self, title: str, body: str, user_id: int) -> dict:
        """Crea un nuevo post."""
        response = self._client.post(
            "/posts",
            json={"title": title, "body": body, "userId": user_id},
        )
        response.raise_for_status()
        post = response.json()
        logger.info("Post creado con id: %s", post.get("id"))
        return post

    @retry(max_attempts=3, initial_delay=0.5)
    def get_user(self, user_id: int) -> dict:
        """Obtiene información de un usuario."""
        response = self._client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()


def download_file(url: str, output_path: Path) -> None:
    """Descarga un archivo grande usando streaming."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Descargando %s...", url)
    with httpx.stream("GET", url, timeout=30.0) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with output_path.open("wb") as f:
            for chunk in response.iter_bytes(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
            if total and total >= downloaded:
                pct = (downloaded / total) * 100
                print(f"\r  Progreso: {pct:.1f}%", end="", flush=True)
            else:
                print(
                    f"\r  Descargados: {downloaded / 1024:.1f} KB", end="", flush=True
                )

    print()
    logger.info("Descarga completa: %s (%.1f KB)", output_path, downloaded / 1024)


if __name__ == "__main__":
    print("=== Cliente HTTP con reintentos ===\n")

    with OrdersApiClient("https://jsonplaceholder.typicode.com") as client:
        # GET — obtener posts de un usuario
        posts = client.get_posts(user_id=1)
        print(f"Posts del usuario 1: {len(posts)}")
        print(f"  Primer post: {posts[0]['title'][:50]}...")

        # GET — un post específico
        post = client.get_post(1)
        print(f"\nPost #1: {post['title']}")

        # POST — crear uno nuevo
        new_post = client.create_post(
            title="Mi post desde Python",
            body="Creado con httpx y reintentos automáticos",
            user_id=1,
        )
        print(f"\nPost creado: {new_post}")

        # Combinar datos de dos endpoints
        user = client.get_user(1)
        print(f"\nUsuario: {user['name']} ({user['email']})")
        # print(f"  Tiene {len(posts)} posts")

    # === Streaming — descargar un archivo ===
    print("\n=== Descarga por streaming ===")
    download_file(
        url="https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat",
        output_path=Path("fundamental/lab_7/airports.dat"),
    )
