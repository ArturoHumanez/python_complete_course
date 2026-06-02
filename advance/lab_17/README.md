# Lab 17: Empaquetado, Docker y CI/CD

## Archivos creados

Los archivos de este laboratorio viven en la raíz del proyecto
por requerimiento de las herramientas:

- `/Dockerfile` — Build multistage con python:3.12-slim y usuario sin root
- `/.dockerignore` — Exclusiones para el build de Docker
- `/.github/workflows/ci.yml` — Pipeline CI con lint, type-check, tests y cobertura

## Cómo ejecutar

```bash
# Build de la imagen
docker build -t orders-api .

# Correr el contenedor
docker run -p 8000:8000 orders-api

# CI se ejecuta automáticamente en push a main
```# Lab 17: Empaquetado, Docker y CI/CD

## Archivos creados

Los archivos de este laboratorio viven en la raíz del proyecto
por requerimiento de las herramientas:

- `/Dockerfile` — Build multistage con python:3.12-slim y usuario sin root
- `/.dockerignore` — Exclusiones para el build de Docker
- `/.github/workflows/ci.yml` — Pipeline CI con lint, type-check, tests y cobertura

## Cómo ejecutar

```bash
# Build de la imagen
docker build -t orders-api .

# Correr el contenedor
docker run -p 8000:8000 orders-api

# CI se ejecuta automáticamente en push a main
```