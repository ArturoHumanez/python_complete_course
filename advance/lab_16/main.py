import logging

from fastapi import FastAPI

from advance.lab_16.infrastructure.api.router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(title="Orders API — Clean Architecture", version="0.3.0")
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Orders API — Arquitectura Limpia"}
