import time
import functools
import random
from contextlib import contextmanager


def retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0):
    """Decorador que reintenta una función si lanza excepción."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        print(f"  ✗ Falló después de {max_attempts} intentos")
                        raise
                    print(
                        f"  ⚠ Intento {attempt} falló: {e}"
                        f" — reintentando en {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

@retry(max_attempts=6, initial_delay=0.5)
def call_unreliable_api():
    """Simula una API que falla ~50% de las veces."""
    if random.random() < 0.5:
        raise ConnectionError("Servidor no disponible")
    return {"status": "ok", "data": [1, 2, 3]}

@retry(max_attempts=3, initial_delay=0.5)
def send_to_api(orders_batch):
    """Simula enviar un lote de órdenes a una API."""
    if random.random() < 0.4:
        raise ConnectionError("Timeout del servidor")
    print(f"    ✓ Enviadas {len(orders_batch)} órdenes")
    return {"sent": len(orders_batch)}


@contextmanager
def timer(label="Operación"):
    """Context manager que mide el tiempo de un bloque de código."""
    start = time.time()
    print(f"⏱ {label} — iniciando...")
    yield
    elapsed = time.time() - start
    print(f"⏱ {label} — terminó en {elapsed:.2f}s")

def batch(items, size):
    """Generador que entrega items en lotes."""
    for i in range(0, len(items), size):
        yield items[i : i + size]
        
if __name__ == "__main__":
    print("=== Probando decorador de reintentos ===")
    try:
        result = call_unreliable_api()
        print(f"  ✓ Éxito: {result}")
    except ConnectionError:
        print("  ✗ La API no respondió después de todos los intentos")
        
        
    # Context manager + generador + decorador juntos
    print("\n=== Probando context manager + generador ===")
    orders = list(range(1, 21))

    with timer("Procesamiento por lotes"):
        for group in batch(orders, 5):
            print(f"  Procesando lote: {group}")
            time.sleep(0.3)
            
    # Ejemplo integrador
    print("\n=== Combinando todo ===")
    orders = [{"id": i, "total": i * 100} for i in range(1, 16)]
    
    with timer("Envío de órdenes a API"):
        for group in batch(orders, 4):
            ids = [o["id"] for o in group]
            print(f"  Lote con órdenes {ids}:")
            try:
                send_to_api(group)
            except ConnectionError:
                print(f"    ✗ Lote {ids} falló definitivamente")