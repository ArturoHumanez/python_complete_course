import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="CLI para gestionar órdenes")
console = Console()

BASE_URL = "http://localhost:8000"


@app.command()
def list_orders(
    status: str = typer.Option(None, help="Filtrar por status: pending, completed, cancelled"),
):
    """Lista todas las órdenes."""
    params = {"status": status} if status else {}
    try:
        response = httpx.get(f"{BASE_URL}/orders/", params=params, timeout=10)
        response.raise_for_status()
        orders = response.json()

        if not orders:
            console.print("[yellow]No se encontraron órdenes[/yellow]")
            return

        table = Table(title="Órdenes")
        table.add_column("ID", style="cyan")
        table.add_column("Cliente", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("Total", justify="right", style="bold")
        table.add_column("Items", justify="right")

        for order in orders:
            table.add_row(
                str(order["id"]),
                order["customer"],
                order["status"],
                f"${order['total']:,.2f}",
                str(order["item_count"]),
            )

        console.print(table)

    except httpx.RequestError as e:
        console.print(f"[red]Error de conexión: {e}[/red]")


@app.command()
def get_order(order_id: int = typer.Argument(help="ID de la orden")):
    """Obtiene una orden por ID."""
    try:
        response = httpx.get(f"{BASE_URL}/orders/{order_id}", timeout=10)
        if response.status_code == 404:
            console.print(f"[red]Orden {order_id} no encontrada[/red]")
            return
        response.raise_for_status()
        order = response.json()

        console.print(f"\n[bold cyan]Orden #{order['id']}[/bold cyan]")
        console.print(f"  Cliente: {order['customer']}")
        console.print(f"  Status:  {order['status']}")
        console.print(f"  Total:   ${order['total']:,.2f}")
        console.print(f"  Items:")
        for item in order["items"]:
            console.print(
                f"    - {item['product']} x{item['quantity']} = ${item['subtotal']:,.2f}"
            )

    except httpx.RequestError as e:
        console.print(f"[red]Error de conexión: {e}[/red]")


@app.command()
def create_order(
    customer: str = typer.Option(..., prompt="Nombre del cliente"),
    token: str = typer.Option(..., prompt="Token JWT"),
):
    """Crea una nueva orden de forma interactiva."""
    items = []
    while True:
        console.print(f"\n[cyan]Item #{len(items) + 1}[/cyan] (deja producto vacío para terminar)")
        product = typer.prompt("  Producto", default="")
        if not product:
            break
        price = typer.prompt("  Precio", type=float)
        quantity = typer.prompt("  Cantidad", type=int, default=1)
        items.append({"product": product, "price": price, "quantity": quantity})

    if not items:
        console.print("[red]Debes agregar al menos un item[/red]")
        return

    try:
        response = httpx.post(
            f"{BASE_URL}/orders/",
            json={"customer": customer, "items": items},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if response.status_code == 201:
            order = response.json()
            console.print(
                f"\n[green]Orden #{order['id']} creada — ${order['total']:,.2f}[/green]"
            )
        elif response.status_code == 401:
            console.print("[red]Token inválido o expirado[/red]")
        else:
            console.print(f"[red]Error: {response.json().get('detail', response.text)}[/red]")

    except httpx.RequestError as e:
        console.print(f"[red]Error de conexión: {e}[/red]")


@app.command()
def delete_order(
    order_id: int = typer.Argument(help="ID de la orden a eliminar"),
    token: str = typer.Option(..., prompt="Token JWT"),
):
    """Elimina una orden."""
    confirm = typer.confirm(f"¿Seguro que quieres eliminar la orden {order_id}?")
    if not confirm:
        console.print("[yellow]Cancelado[/yellow]")
        return

    try:
        response = httpx.delete(
            f"{BASE_URL}/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if response.status_code == 204:
            console.print(f"[green]Orden {order_id} eliminada[/green]")
        elif response.status_code == 404:
            console.print(f"[red]Orden {order_id} no encontrada[/red]")
        elif response.status_code == 401:
            console.print("[red]Token inválido o expirado[/red]")

    except httpx.RequestError as e:
        console.print(f"[red]Error de conexión: {e}[/red]")


if __name__ == "__main__":
    app()