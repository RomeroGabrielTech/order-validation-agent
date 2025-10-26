"""
CLI principal para el sistema de validación de órdenes.
Incluye ejemplos de validación y modo interactivo.
"""

import sys
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from loguru import logger

from .agents.order_validator import validate_order

# Configurar consola Rich
console = Console()

# Configurar logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)


# Ejemplos de órdenes para pruebas
EXAMPLE_ORDERS = {
    "CUST001": {
        "order_id": "ORD-001",
        "customer_id": "CUST001",
        "items": [
            {"product_id": "PROD001", "quantity": 2, "unit_price": 1200.0},
            {"product_id": "PROD002", "quantity": 5, "unit_price": 25.0}
        ],
        "description": "Orden válida - Cliente activo con crédito suficiente"
    },
    "CUST002": {
        "order_id": "ORD-002",
        "customer_id": "CUST002",
        "items": [
            {"product_id": "PROD001", "quantity": 5, "unit_price": 1200.0}
        ],
        "description": "Orden rechazada - Crédito insuficiente (necesita $6000, tiene $500)"
    },
    "CUST003": {
        "order_id": "ORD-003",
        "customer_id": "CUST003",
        "items": [
            {"product_id": "PROD004", "quantity": 2, "unit_price": 350.0}
        ],
        "description": "Orden rechazada - Cliente inactivo"
    },
    "CUST004": {
        "order_id": "ORD-004",
        "customer_id": "CUST004",
        "items": [
            {"product_id": "PROD005", "quantity": 3, "unit_price": 120.0},
            {"product_id": "PROD002", "quantity": 2, "unit_price": 25.0}
        ],
        "description": "Orden rechazada - Producto sin stock (PROD005)"
    },
    "CUST005": {
        "order_id": "ORD-005",
        "customer_id": "CUST005",
        "items": [
            {"product_id": "PROD999", "quantity": 1, "unit_price": 100.0},
            {"product_id": "PROD001", "quantity": 2, "unit_price": 1200.0}
        ],
        "description": "Orden rechazada - Producto inexistente (PROD999)"
    }
}


def print_header():
    """Imprime el encabezado de la aplicación."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Sistema de Validación de Órdenes[/bold cyan]\n"
        "[dim]Powered by LangChain + LangGraph[/dim]",
        border_style="cyan"
    ))
    console.print()


def print_validation_result(result: Dict[str, Any], order_data: Dict[str, Any]):
    """
    Imprime el resultado de validación de forma bonita.
    
    Args:
        result: Resultado de la validación
        order_data: Datos originales de la orden
    """
    # Panel principal con información de la orden
    order_info = (
        f"[bold]Order ID:[/bold] {order_data['order_id']}\n"
        f"[bold]Customer ID:[/bold] {order_data['customer_id']}\n"
        f"[bold]Items:[/bold] {len(order_data['items'])}\n"
        f"[bold]Total:[/bold] ${result['total_amount']:.2f}"
    )
    
    # Color según el estado
    if result["approved"]:
        status_color = "green"
        status_icon = "✓"
        border_style = "green"
    else:
        status_color = "red"
        status_icon = "✗"
        border_style = "red"
    
    console.print(Panel(
        order_info,
        title=f"[{status_color}]{status_icon} {result['status'].upper()}[/{status_color}]",
        border_style=border_style
    ))
    
    # Mensaje principal
    console.print(f"\n[bold]{result['message']}[/bold]\n")
    
    # Tabla de validaciones
    table = Table(title="Detalles de Validación", box=box.ROUNDED)
    table.add_column("Validación", style="cyan", no_wrap=True)
    table.add_column("Estado", justify="center")
    table.add_column("Detalles", style="dim")
    
    # Validación de cliente
    customer_val = result["validation_details"].get("customer", {})
    if customer_val:
        customer_status = "✓ Válido" if customer_val.get("valid") else "✗ Inválido"
        customer_style = "green" if customer_val.get("valid") else "red"
        customer_details = customer_val.get("message", "N/A")
        table.add_row(
            "Cliente",
            f"[{customer_style}]{customer_status}[/{customer_style}]",
            customer_details
        )
    
    # Validación de items
    items_val = result["validation_details"].get("items", {})
    if items_val:
        items_status = "✓ Válido" if items_val.get("valid") else "✗ Inválido"
        items_style = "green" if items_val.get("valid") else "red"
        items_details = items_val.get("message", "N/A")
        table.add_row(
            "Items",
            f"[{items_style}]{items_status}[/{items_style}]",
            items_details
        )
    
    # Validación de crédito
    credit_val = result["validation_details"].get("credit", {})
    if credit_val:
        credit_status = "✓ Suficiente" if credit_val.get("has_credit") else "✗ Insuficiente"
        credit_style = "green" if credit_val.get("has_credit") else "red"
        credit_details = credit_val.get("message", "N/A")
        table.add_row(
            "Crédito",
            f"[{credit_style}]{credit_status}[/{credit_style}]",
            credit_details
        )
    
    console.print(table)
    
    # Mostrar errores si existen
    if result["errors"]:
        console.print("\n[bold red]Errores encontrados:[/bold red]")
        for i, error in enumerate(result["errors"], 1):
            console.print(f"  {i}. [red]{error}[/red]")
    
    # Mostrar advertencias si existen
    if result["warnings"]:
        console.print("\n[bold yellow]Advertencias:[/bold yellow]")
        for i, warning in enumerate(result["warnings"], 1):
            console.print(f"  {i}. [yellow]{warning}[/yellow]")
    
    # Detalles de items validados
    if result["approved"] and items_val.get("validated_items"):
        console.print("\n[bold cyan]Items Aprobados:[/bold cyan]")
        items_table = Table(box=box.SIMPLE)
        items_table.add_column("Producto", style="cyan")
        items_table.add_column("Nombre", style="white")
        items_table.add_column("Cantidad", justify="right")
        items_table.add_column("Precio Unit.", justify="right")
        items_table.add_column("Total", justify="right", style="green")
        
        for item in items_val["validated_items"]:
            items_table.add_row(
                item["product_id"],
                item["product_name"],
                str(item["quantity"]),
                f"${item['unit_price']:.2f}",
                f"${item['item_total']:.2f}"
            )
        
        console.print(items_table)
    
    console.print("\n" + "─" * 80 + "\n")


def run_example_validations():
    """Ejecuta validaciones de ejemplo con los 5 casos de prueba."""
    console.print("[bold cyan]Ejecutando Validaciones de Ejemplo[/bold cyan]\n")
    
    results_summary = []
    
    for customer_key, order_data in EXAMPLE_ORDERS.items():
        console.print(f"[bold yellow]Caso de Prueba:[/bold yellow] {order_data['description']}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(
                f"Validando orden {order_data['order_id']}...",
                total=None
            )
            
            # Ejecutar validación
            result = validate_order(
                order_id=order_data["order_id"],
                customer_id=order_data["customer_id"],
                items=order_data["items"]
            )
            
            progress.update(task, completed=True)
        
        # Mostrar resultado
        print_validation_result(result, order_data)
        
        # Guardar resumen
        results_summary.append({
            "order_id": order_data["order_id"],
            "customer_id": order_data["customer_id"],
            "approved": result["approved"],
            "total": result["total_amount"]
        })
    
    # Mostrar resumen final
    console.print("[bold cyan]Resumen de Validaciones[/bold cyan]\n")
    
    summary_table = Table(title="Resultados", box=box.ROUNDED)
    summary_table.add_column("Order ID", style="cyan")
    summary_table.add_column("Customer ID", style="white")
    summary_table.add_column("Total", justify="right")
    summary_table.add_column("Estado", justify="center")
    
    approved_count = 0
    rejected_count = 0
    
    for summary in results_summary:
        status = "✓ Aprobada" if summary["approved"] else "✗ Rechazada"
        status_style = "green" if summary["approved"] else "red"
        
        summary_table.add_row(
            summary["order_id"],
            summary["customer_id"],
            f"${summary['total']:.2f}",
            f"[{status_style}]{status}[/{status_style}]"
        )
        
        if summary["approved"]:
            approved_count += 1
        else:
            rejected_count += 1
    
    console.print(summary_table)
    console.print(f"\n[green]Aprobadas: {approved_count}[/green] | [red]Rechazadas: {rejected_count}[/red]\n")


def validate_custom_order():
    """Permite al usuario ingresar una orden personalizada para validar."""
    console.print("[bold cyan]Validación de Orden Personalizada[/bold cyan]\n")
    
    # Solicitar datos de la orden
    order_id = Prompt.ask("[cyan]Order ID[/cyan]", default="ORD-CUSTOM")
    customer_id = Prompt.ask("[cyan]Customer ID[/cyan] (CUST001-CUST005)")
    
    # Solicitar items
    items = []
    console.print("\n[yellow]Ingrese los items de la orden (deje vacío para terminar)[/yellow]")
    
    while True:
        console.print(f"\n[dim]Item #{len(items) + 1}[/dim]")
        product_id = Prompt.ask("  Product ID", default="")
        
        if not product_id:
            break
        
        quantity = Prompt.ask("  Cantidad", default="1")
        unit_price = Prompt.ask("  Precio unitario", default="0")
        
        try:
            items.append({
                "product_id": product_id,
                "quantity": int(quantity),
                "unit_price": float(unit_price)
            })
            console.print(f"  [green]✓ Item agregado[/green]")
        except ValueError:
            console.print(f"  [red]✗ Error: valores inválidos[/red]")
    
    if not items:
        console.print("[red]No se agregaron items. Cancelando validación.[/red]")
        return
    
    # Confirmar validación
    console.print(f"\n[bold]Resumen:[/bold]")
    console.print(f"  Order ID: {order_id}")
    console.print(f"  Customer ID: {customer_id}")
    console.print(f"  Items: {len(items)}")
    
    if not Confirm.ask("\n¿Proceder con la validación?", default=True):
        console.print("[yellow]Validación cancelada.[/yellow]")
        return
    
    # Ejecutar validación
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"Validando orden {order_id}...", total=None)
        
        result = validate_order(
            order_id=order_id,
            customer_id=customer_id,
            items=items
        )
        
        progress.update(task, completed=True)
    
    # Mostrar resultado
    order_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items
    }
    print_validation_result(result, order_data)


def show_menu():
    """Muestra el menú principal y maneja la selección del usuario."""
    while True:
        console.print("[bold cyan]Menú Principal[/bold cyan]\n")
        console.print("1. Ejecutar validaciones de ejemplo")
        console.print("2. Validar orden personalizada")
        console.print("3. Salir\n")
        
        choice = Prompt.ask(
            "Seleccione una opción",
            choices=["1", "2", "3"],
            default="1"
        )
        
        console.print()
        
        if choice == "1":
            run_example_validations()
        elif choice == "2":
            validate_custom_order()
        elif choice == "3":
            console.print("[yellow]¡Hasta luego![/yellow]")
            break
        
        if choice in ["1", "2"]:
            if not Confirm.ask("\n¿Volver al menú principal?", default=True):
                console.print("[yellow]¡Hasta luego![/yellow]")
                break
            console.print()


def main():
    """Función principal de la CLI."""
    try:
        print_header()
        show_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operación cancelada por el usuario.[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error en la aplicación")
        sys.exit(1)


if __name__ == "__main__":
    main()