import asyncio
import math
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import httpx

# === URLs para probar I/O concurrente ===
URLS = [f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 21)]


# === 1. Versión síncrona (baseline) ===

def fetch_sync(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        response = httpx.get(url, timeout=10)
        results.append(response.json())
    return results


# === 2. Versión con threads ===

def fetch_threaded(urls: list[str], workers: int = 5) -> list[dict]:
    def fetch_one(url: str) -> dict:
        return httpx.get(url, timeout=10).json()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fetch_one, urls))


# === 3. Versión async con semáforo ===

async def fetch_async(urls: list[str], max_concurrent: int = 5) -> list[dict]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(client: httpx.AsyncClient, url: str) -> dict:
        async with semaphore:
            response = await client.get(url)
            return response.json()

    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [fetch_one(client, url) for url in urls]
        return await asyncio.gather(*tasks)


# === 4. CPU-bound con multiprocessing ===

def heavy_calculation(n: int) -> float:
    """Simula trabajo pesado de CPU."""
    return sum(math.sqrt(i) for i in range(n))


def run_cpu_sync(numbers: list[int]) -> list[float]:
    return [heavy_calculation(n) for n in numbers]


def run_cpu_parallel(numbers: list[int], workers: int = 4) -> list[float]:
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(heavy_calculation, numbers))


# === Benchmark helper ===

def benchmark(label: str, func, *args) -> tuple:
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    print(f"  {label}: {elapsed:.2f}s")
    return result, elapsed


if __name__ == "__main__":
    # === I/O-bound: comparar sync vs threads vs async ===
    print(f"=== I/O-bound: Fetching {len(URLS)} URLs ===\n")

    _, t_sync = benchmark("Síncrono", fetch_sync, URLS)
    _, t_threads = benchmark("Threads (5 workers)", fetch_threaded, URLS)

    results_async, t_async = benchmark(
        "Async (5 concurrent)",
        lambda urls: asyncio.run(fetch_async(urls)),
        URLS,
    )

    print(f"\n  Speedup threads vs sync: {t_sync / t_threads:.1f}x")
    print(f"  Speedup async vs sync:   {t_sync / t_async:.1f}x")

    # === CPU-bound: comparar sync vs multiprocessing ===
    print("\n=== CPU-bound: Cálculos pesados ===\n")

    numbers = [5_000_000, 10_000_000, 8_000_000, 12_000_000]

    _, t_cpu_sync = benchmark("Síncrono", run_cpu_sync, numbers)
    _, t_cpu_parallel = benchmark("Multiprocessing (4)", run_cpu_parallel, numbers)

    print(f"\n  Speedup multiprocessing: {t_cpu_sync / t_cpu_parallel:.1f}x")