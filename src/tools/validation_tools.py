"""
Herramientas de validación para órdenes usando LangChain.
Incluye validación de clientes, crédito y items.
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from loguru import logger

# Datos mock de clientes
MOCK_CUSTOMERS = {
    "CUST001": {
        "id": "CUST001",
        "name": "Acme Corporation",
        "email": "contact@acme.com",
        "status": "active",
        "credit_limit": 10000.0,
        "current_balance": 2000.0
    },
    "CUST002": {
        "id": "CUST002",
        "name": "TechStart Inc",
        "email": "info@techstart.com",
        "status": "active",
        "credit_limit": 5000.0,
        "current_balance": 4500.0
    },
    "CUST003": {
        "id": "CUST003",
        "name": "Global Solutions",
        "email": "sales@globalsolutions.com",
        "status": "inactive",
        "credit_limit": 15000.0,
        "current_balance": 0.0
    },
    "CUST004": {
        "id": "CUST004",
        "name": "Innovation Labs",
        "email": "hello@innovationlabs.com",
        "status": "active",
        "credit_limit": 8000.0,
        "current_balance": 1000.0
    },
    "CUST005": {
        "id": "CUST005",
        "name": "Enterprise Systems",
        "email": "contact@enterprise.com",
        "status": "active",
        "credit_limit": 20000.0,
        "current_balance": 15000.0
    }
}

# Datos mock de productos/items
MOCK_PRODUCTS = {
    "PROD001": {
        "id": "PROD001",
        "name": "Laptop Pro 15",
        "price": 1200.0,
        "stock": 50,
        "category": "electronics"
    },
    "PROD002": {
        "id": "PROD002",
        "name": "Wireless Mouse",
        "price": 25.0,
        "stock": 200,
        "category": "accessories"
    },
    "PROD003": {
        "id": "PROD003",
        "name": "USB-C Hub",
        "price": 45.0,
        "stock": 100,
        "category": "accessories"
    },
    "PROD004": {
        "id": "PROD004",
        "name": "Monitor 27 inch",
        "price": 350.0,
        "stock": 30,
        "category": "electronics"
    },
    "PROD005": {
        "id": "PROD005",
        "name": "Mechanical Keyboard",
        "price": 120.0,
        "stock": 0,  # Sin stock
        "category": "accessories"
    },
    "PROD006": {
        "id": "PROD006",
        "name": "Webcam HD",
        "price": 80.0,
        "stock": 75,
        "category": "electronics"
    }
}


@tool
def validate_customer_exists(customer_id: str) -> Dict[str, Any]:
    """
    Valida si un cliente existe en el sistema y está activo.
    
    Args:
        customer_id: ID único del cliente a validar
        
    Returns:
        Dict con información de validación del cliente:
        - valid: bool indicando si el cliente es válido
        - exists: bool indicando si el cliente existe
        - active: bool indicando si el cliente está activo
        - customer_data: datos del cliente si existe
        - message: mensaje descriptivo del resultado
    """
    logger.info(f"Validando existencia del cliente: {customer_id}")
    
    if not customer_id:
        logger.warning("ID de cliente vacío proporcionado")
        return {
            "valid": False,
            "exists": False,
            "active": False,
            "customer_data": None,
            "message": "ID de cliente no proporcionado"
        }
    
    customer = MOCK_CUSTOMERS.get(customer_id)
    
    if not customer:
        logger.warning(f"Cliente no encontrado: {customer_id}")
        return {
            "valid": False,
            "exists": False,
            "active": False,
            "customer_data": None,
            "message": f"Cliente {customer_id} no existe en el sistema"
        }
    
    is_active = customer.get("status") == "active"
    
    if not is_active:
        logger.warning(f"Cliente inactivo: {customer_id}")
        return {
            "valid": False,
            "exists": True,
            "active": False,
            "customer_data": customer,
            "message": f"Cliente {customer_id} existe pero está inactivo"
        }
    
    logger.info(f"Cliente válido: {customer_id} - {customer['name']}")
    return {
        "valid": True,
        "exists": True,
        "active": True,
        "customer_data": customer,
        "message": f"Cliente {customer_id} válido y activo"
    }


@tool
def check_customer_credit(customer_id: str, order_amount: float) -> Dict[str, Any]:
    """
    Verifica si un cliente tiene crédito suficiente para una orden.
    
    Args:
        customer_id: ID único del cliente
        order_amount: Monto total de la orden
        
    Returns:
        Dict con información de crédito:
        - has_credit: bool indicando si tiene crédito suficiente
        - credit_limit: límite de crédito del cliente
        - current_balance: balance actual del cliente
        - available_credit: crédito disponible
        - required_amount: monto requerido para la orden
        - message: mensaje descriptivo del resultado
    """
    logger.info(f"Verificando crédito para cliente {customer_id}, monto: ${order_amount:.2f}")
    
    customer = MOCK_CUSTOMERS.get(customer_id)
    
    if not customer:
        logger.error(f"Cliente no encontrado al verificar crédito: {customer_id}")
        return {
            "has_credit": False,
            "credit_limit": 0.0,
            "current_balance": 0.0,
            "available_credit": 0.0,
            "required_amount": order_amount,
            "message": f"Cliente {customer_id} no encontrado"
        }
    
    credit_limit = customer.get("credit_limit", 0.0)
    current_balance = customer.get("current_balance", 0.0)
    available_credit = credit_limit - current_balance
    
    has_sufficient_credit = available_credit >= order_amount
    
    if has_sufficient_credit:
        logger.info(f"Crédito suficiente para {customer_id}: ${available_credit:.2f} disponible")
        return {
            "has_credit": True,
            "credit_limit": credit_limit,
            "current_balance": current_balance,
            "available_credit": available_credit,
            "required_amount": order_amount,
            "message": f"Crédito suficiente. Disponible: ${available_credit:.2f}, Requerido: ${order_amount:.2f}"
        }
    else:
        deficit = order_amount - available_credit
        logger.warning(f"Crédito insuficiente para {customer_id}: falta ${deficit:.2f}")
        return {
            "has_credit": False,
            "credit_limit": credit_limit,
            "current_balance": current_balance,
            "available_credit": available_credit,
            "required_amount": order_amount,
            "message": f"Crédito insuficiente. Disponible: ${available_credit:.2f}, Requerido: ${order_amount:.2f}, Falta: ${deficit:.2f}"
        }


@tool
def validate_order_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Valida los items de una orden verificando existencia, stock y precios.
    
    Args:
        items: Lista de items con estructura:
            - product_id: ID del producto
            - quantity: cantidad solicitada
            - unit_price: precio unitario (opcional, se valida contra precio real)
            
    Returns:
        Dict con información de validación:
        - valid: bool indicando si todos los items son válidos
        - total_amount: monto total calculado
        - validated_items: lista de items validados con detalles
        - invalid_items: lista de items inválidos con razones
        - message: mensaje descriptivo del resultado
    """
    logger.info(f"Validando {len(items)} items de la orden")
    
    if not items:
        logger.warning("Lista de items vacía")
        return {
            "valid": False,
            "total_amount": 0.0,
            "validated_items": [],
            "invalid_items": [],
            "message": "No se proporcionaron items en la orden"
        }
    
    validated_items = []
    invalid_items = []
    total_amount = 0.0
    
    for idx, item in enumerate(items):
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)
        provided_price = item.get("unit_price")
        
        logger.debug(f"Validando item {idx + 1}: {product_id}, cantidad: {quantity}")
        
        # Validar que el producto existe
        product = MOCK_PRODUCTS.get(product_id)
        if not product:
            logger.warning(f"Producto no encontrado: {product_id}")
            invalid_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "reason": f"Producto {product_id} no existe en el catálogo"
            })
            continue
        
        # Validar cantidad
        if quantity <= 0:
            logger.warning(f"Cantidad inválida para {product_id}: {quantity}")
            invalid_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "reason": f"Cantidad debe ser mayor a 0"
            })
            continue
        
        # Validar stock disponible
        available_stock = product.get("stock", 0)
        if quantity > available_stock:
            logger.warning(f"Stock insuficiente para {product_id}: solicitado {quantity}, disponible {available_stock}")
            invalid_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "available_stock": available_stock,
                "reason": f"Stock insuficiente. Solicitado: {quantity}, Disponible: {available_stock}"
            })
            continue
        
        # Validar precio si se proporciona
        actual_price = product.get("price", 0.0)
        if provided_price is not None and abs(provided_price - actual_price) > 0.01:
            logger.warning(f"Precio incorrecto para {product_id}: proporcionado ${provided_price:.2f}, actual ${actual_price:.2f}")
            invalid_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "provided_price": provided_price,
                "actual_price": actual_price,
                "reason": f"Precio incorrecto. Proporcionado: ${provided_price:.2f}, Actual: ${actual_price:.2f}"
            })
            continue
        
        # Item válido
        item_total = actual_price * quantity
        total_amount += item_total
        
        validated_items.append({
            "product_id": product_id,
            "product_name": product.get("name"),
            "quantity": quantity,
            "unit_price": actual_price,
            "item_total": item_total,
            "category": product.get("category")
        })
        
        logger.debug(f"Item válido: {product_id} - {product.get('name')}, total: ${item_total:.2f}")
    
    is_valid = len(invalid_items) == 0 and len(validated_items) > 0
    
    if is_valid:
        logger.info(f"Todos los items son válidos. Total: ${total_amount:.2f}")
        message = f"Todos los {len(validated_items)} items son válidos. Total: ${total_amount:.2f}"
    else:
        logger.warning(f"Validación fallida: {len(invalid_items)} items inválidos")
        message = f"Validación fallida: {len(invalid_items)} items inválidos de {len(items)} totales"
    
    return {
        "valid": is_valid,
        "total_amount": total_amount,
        "validated_items": validated_items,
        "invalid_items": invalid_items,
        "message": message
    }


# Lista de todas las herramientas para fácil importación
VALIDATION_TOOLS = [
    validate_customer_exists,
    check_customer_credit,
    validate_order_items
]