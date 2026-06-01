import logging

from fastapi import FastAPI

from intermediate.lab_15.infrastructure.api.router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(title="Orders API — Hexagonal", version="0.2.0")
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Orders API — Arquitectura Hexagonal"}