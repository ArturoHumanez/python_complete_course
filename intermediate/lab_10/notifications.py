import httpx


def send_order_notification(order_id: int, customer: str, total: float) -> bool:
    """Envía una notificación por HTTP cuando se crea una orden."""
    try:
        response = httpx.post(
            "https://api.notifications.example.com/send",
            json={
                "to": customer,
                "message": f"Tu orden #{order_id} por ${total:,.2f} fue recibida",
            },
            timeout=5.0,
        )
        response.raise_for_status()
        return True
    except (httpx.RequestError, httpx.HTTPStatusError):
        return False


def process_new_order(order_id: int, customer: str, total: float) -> dict:
    """Procesa una orden nueva y notifica al cliente."""
    notified = send_order_notification(order_id, customer, total)
    return {
        "order_id": order_id,
        "status": "confirmed",
        "notified": notified,
    }
