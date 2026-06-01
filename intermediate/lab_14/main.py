import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MODEL_PATH = Path("intermediate/lab_14/order_classifier.joblib")


def load_and_clean(filepath: str) -> pd.DataFrame:
    """Carga y limpia el dataset."""
    logger.info("Cargando dataset desde %s", filepath)
    df = pd.read_csv(filepath)

    logger.info("Shape: %s", df.shape)
    logger.info("Columnas: %s", list(df.columns))

    # Verificar nulos
    nulls = df.isnull().sum()
    if nulls.any():
        logger.warning("Valores nulos encontrados:\n%s", nulls[nulls > 0])
        df = df.dropna()

    # Convertir booleano
    df["has_laptop"] = df["has_laptop"].astype(int)

    logger.info("Distribución de status:\n%s", df["status"].value_counts())
    return df


def train_model(df: pd.DataFrame) -> tuple:
    """Entrena un clasificador de Random Forest."""
    # Features y target
    features = ["num_items", "total", "has_laptop"]
    X = df[features]
    y = LabelEncoder().fit_transform(df["status"])  # cancelled=0, completed=1

    # Dividir en train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(
        "Train: %d muestras, Test: %d muestras",
        len(X_train), len(X_test),
    )

    # Entrenar
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluar
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info("Accuracy: %.2f%%", accuracy * 100)
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=["cancelled", "completed"]))

    # Importancia de features
    print("Importancia de features:")
    for name, importance in zip(features, model.feature_importances_):
        print(f"  {name}: {importance:.3f}")

    return model, features


def save_model(model, filepath: Path) -> None:
    """Guarda el modelo entrenado."""
    joblib.dump(model, filepath)
    logger.info("Modelo guardado en %s", filepath)


def load_model(filepath: Path):
    """Carga un modelo guardado."""
    model = joblib.load(filepath)
    logger.info("Modelo cargado desde %s", filepath)
    return model


def predict(model, orders: list[dict], features: list[str]) -> list[str]:
    """Predice el status de nuevas órdenes."""
    df = pd.DataFrame(orders)
    predictions = model.predict(df[features])
    labels = ["cancelled" if p == 0 else "completed" for p in predictions]
    return labels


if __name__ == "__main__":
    # === Cargar y limpiar ===
    df = load_and_clean("intermediate/lab_14/orders_dataset.csv")

    # === Entrenar ===
    print("\n=== Entrenamiento ===")
    model, features = train_model(df)

    # === Guardar ===
    save_model(model, MODEL_PATH)

    # === Cargar y predecir (simulando producción) ===
    print("\n=== Inferencia con modelo guardado ===")
    loaded_model = load_model(MODEL_PATH)

    new_orders = [
        {"num_items": 1, "total": 350, "has_laptop": 0},
        {"num_items": 4, "total": 45000, "has_laptop": 1},
        {"num_items": 2, "total": 1200, "has_laptop": 0},
        {"num_items": 5, "total": 80000, "has_laptop": 1},
    ]

    predictions = predict(loaded_model, new_orders, features)
    print("\nPredicciones:")
    for order, pred in zip(new_orders, predictions):
        print(f"  {order} → {pred}")