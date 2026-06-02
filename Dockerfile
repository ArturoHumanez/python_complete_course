# === Etapa 1: Builder ===
FROM python:3.12-slim AS builder

RUN pip install poetry==2.3.1 poetry-plugin-export

WORKDIR /app

# Copiar solo archivos de dependencias primero (cache de Docker)
COPY pyproject.toml poetry.lock ./

# Exportar dependencias a requirements.txt (sin poetry en producción)
RUN poetry export -f requirements.txt --without dev -o requirements.txt

# === Etapa 2: Runtime ===
FROM python:3.12-slim AS runtime

WORKDIR /app

# Crear usuario sin privilegios
RUN useradd --create-home appuser

# Instalar dependencias
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY advance/lab_16/ ./advance/lab_16/

# Cambiar a usuario sin privilegios
USER appuser

EXPOSE 8000

CMD ["uvicorn", "advance.lab_16.main:app", "--host", "0.0.0.0", "--port", "8000"]