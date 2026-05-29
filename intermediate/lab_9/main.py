from fastapi import FastAPI

from intermediate.lab_9.database import create_tables
from intermediate.lab_9.routers import auth, orders
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Orders API",
    version="0.1.0",
    description="API REST de órdenes —  Lab 9",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(auth.router)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/")
def root():
    return {"message": "Orders API funcionando", "docs": "/docs"}