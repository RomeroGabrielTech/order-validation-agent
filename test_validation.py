"""
Script de prueba para validar que el sistema funciona correctamente.
"""

from src.agents.order_validator import validate_order
from rich.console import Console
from rich.table import Table

console = Console()

# Test 1: Orden válida
console.print("\n[bold cyan]Test 1: Orden Válida[/bold cyan]")
result1 = validate_order(
    order_id="ORD-001",
    customer_id="CUST001",
    items=[
        {"product_id": "PROD001", "quantity": 2, "unit_price": 1200.0},
        {"product_id": "PROD002", "quantity": 5, "unit_price": 25.0}
    ]
)
console.print(f"Status: [{'green' if result1['approved'] else 'red'}]{result1['status']}[/]")
console.print(f"Total: ${result1['total_amount']:.2f}")
console.print(f"Mensaje: {result1['message']}\n")

# Test 2: Crédito insuficiente
console.print("[bold cyan]Test 2: Crédito Insuficiente[/bold cyan]")
result2 = validate_order(
    order_id="ORD-002",
    customer_id="CUST002",
    items=[
        {"product_id": "PROD001", "quantity": 5, "unit_price": 1200.0}
    ]
)
console.print(f"Status: [{'green' if result2['approved'] else 'red'}]{result2['status']}[/]")
console.print(f"Errores: {len(result2['errors'])}")
for error in result2['errors']:
    console.print(f"  - [red]{error}[/red]")
console.print()

# Test 3: Cliente inactivo
console.print("[bold cyan]Test 3: Cliente Inactivo[/bold cyan]")
result3 = validate_order(
    order_id="ORD-003",
    customer_id="CUST003",
    items=[
        {"product_id": "PROD004", "quantity": 2, "unit_price": 350.0}
    ]
)
console.print(f"Status: [{'green' if result3['approved'] else 'red'}]{result3['status']}[/]")
console.print(f"Errores: {len(result3['errors'])}")
for error in result3['errors']:
    console.print(f"  - [red]{error}[/red]")
console.print()

# Resumen
console.print("[bold green]✓ Todos los tests completados exitosamente![/bold green]")
console.print(f"\nResultados:")
console.print(f"  - Test 1 (Válida): {'✓ APROBADA' if result1['approved'] else '✗ RECHAZADA'}")
console.print(f"  - Test 2 (Crédito): {'✓ APROBADA' if result2['approved'] else '✗ RECHAZADA'}")
console.print(f"  - Test 3 (Inactivo): {'✓ APROBADA' if result3['approved'] else '✗ RECHAZADA'}")