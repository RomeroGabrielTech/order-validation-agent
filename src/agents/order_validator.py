"""
Agente de validación de órdenes usando LangGraph.
Implementa un StateGraph con múltiples nodos de validación y manejo de errores.
"""

from typing import TypedDict, List, Dict, Any, Literal, Optional
from langgraph.graph import StateGraph, END
from loguru import logger
import json

from ..tools.validation_tools import (
    validate_customer_exists,
    check_customer_credit,
    validate_order_items
)


class OrderState(TypedDict):
    """Estado del proceso de validación de orden."""
    # Datos de entrada
    order_id: str
    customer_id: str
    items: List[Dict[str, Any]]
    
    # Resultados de validación
    customer_validation: Optional[Dict[str, Any]]
    items_validation: Optional[Dict[str, Any]]
    credit_validation: Optional[Dict[str, Any]]
    
    # Estado del proceso
    status: str  # "pending", "validating", "approved", "rejected", "error"
    errors: List[str]
    warnings: List[str]
    
    # Resultado final
    total_amount: float
    approved: bool
    message: str
    validation_details: Dict[str, Any]


def parse_order(state: OrderState) -> OrderState:
    """
    Nodo inicial: parsea y valida la estructura básica de la orden.
    
    Args:
        state: Estado actual de la orden
        
    Returns:
        Estado actualizado con validaciones iniciales
    """
    logger.info(f"Parseando orden {state.get('order_id', 'N/A')}")
    
    errors = []
    warnings = []
    
    # Validar campos requeridos
    if not state.get("order_id"):
        errors.append("ID de orden no proporcionado")
    
    if not state.get("customer_id"):
        errors.append("ID de cliente no proporcionado")
    
    if not state.get("items"):
        errors.append("No se proporcionaron items en la orden")
    elif not isinstance(state["items"], list):
        errors.append("Items debe ser una lista")
    elif len(state["items"]) == 0:
        errors.append("La lista de items está vacía")
    
    # Actualizar estado
    state["errors"] = errors
    state["warnings"] = warnings
    state["status"] = "error" if errors else "validating"
    state["approved"] = False
    state["total_amount"] = 0.0
    state["validation_details"] = {}
    
    if errors:
        logger.error(f"Errores en parseo de orden {state.get('order_id')}: {errors}")
        state["message"] = f"Errores en estructura de orden: {'; '.join(errors)}"
    else:
        logger.info(f"Orden {state['order_id']} parseada correctamente")
        state["message"] = "Orden parseada, iniciando validaciones"
    
    return state


def validate_customer_node(state: OrderState) -> OrderState:
    """
    Nodo de validación: verifica que el cliente existe y está activo.
    
    Args:
        state: Estado actual de la orden
        
    Returns:
        Estado actualizado con resultado de validación de cliente
    """
    logger.info(f"Validando cliente {state['customer_id']} para orden {state['order_id']}")
    
    try:
        # Invocar herramienta de validación
        result = validate_customer_exists.invoke({"customer_id": state["customer_id"]})
        
        state["customer_validation"] = result
        
        if not result["valid"]:
            state["errors"].append(result["message"])
            logger.warning(f"Validación de cliente fallida: {result['message']}")
        else:
            logger.info(f"Cliente validado exitosamente: {state['customer_id']}")
        
    except Exception as e:
        error_msg = f"Error al validar cliente: {str(e)}"
        state["errors"].append(error_msg)
        logger.error(error_msg)
        state["customer_validation"] = {
            "valid": False,
            "message": error_msg
        }
    
    return state


def validate_items_node(state: OrderState) -> OrderState:
    """
    Nodo de validación: verifica items, stock y calcula total.
    
    Args:
        state: Estado actual de la orden
        
    Returns:
        Estado actualizado con resultado de validación de items
    """
    logger.info(f"Validando items para orden {state['order_id']}")
    
    try:
        # Invocar herramienta de validación
        result = validate_order_items.invoke({"items": state["items"]})
        
        state["items_validation"] = result
        state["total_amount"] = result.get("total_amount", 0.0)
        
        if not result["valid"]:
            state["errors"].append(result["message"])
            logger.warning(f"Validación de items fallida: {result['message']}")
            
            # Agregar detalles de items inválidos
            for invalid_item in result.get("invalid_items", []):
                state["errors"].append(
                    f"Item {invalid_item['product_id']}: {invalid_item['reason']}"
                )
        else:
            logger.info(f"Items validados exitosamente. Total: ${result['total_amount']:.2f}")
        
    except Exception as e:
        error_msg = f"Error al validar items: {str(e)}"
        state["errors"].append(error_msg)
        logger.error(error_msg)
        state["items_validation"] = {
            "valid": False,
            "message": error_msg
        }
    
    return state


def check_credit_node(state: OrderState) -> OrderState:
    """
    Nodo de validación: verifica crédito disponible del cliente.
    
    Args:
        state: Estado actual de la orden
        
    Returns:
        Estado actualizado con resultado de validación de crédito
    """
    logger.info(f"Verificando crédito para orden {state['order_id']}")
    
    try:
        # Invocar herramienta de validación
        result = check_customer_credit.invoke({
            "customer_id": state["customer_id"],
            "order_amount": state["total_amount"]
        })
        
        state["credit_validation"] = result
        
        if not result["has_credit"]:
            state["errors"].append(result["message"])
            logger.warning(f"Validación de crédito fallida: {result['message']}")
        else:
            logger.info(f"Crédito suficiente para orden {state['order_id']}")
        
    except Exception as e:
        error_msg = f"Error al verificar crédito: {str(e)}"
        state["errors"].append(error_msg)
        logger.error(error_msg)
        state["credit_validation"] = {
            "has_credit": False,
            "message": error_msg
        }
    
    return state


def process_order_node(state: OrderState) -> OrderState:
    """
    Nodo final: procesa la orden aprobada y genera resultado final.
    
    Args:
        state: Estado actual de la orden
        
    Returns:
        Estado actualizado con resultado final
    """
    logger.info(f"Procesando orden aprobada {state['order_id']}")
    
    state["status"] = "approved"
    state["approved"] = True
    state["message"] = f"Orden {state['order_id']} aprobada exitosamente. Total: ${state['total_amount']:.2f}"
    
    # Compilar detalles de validación
    state["validation_details"] = {
        "customer": state.get("customer_validation", {}),
        "items": state.get("items_validation", {}),
        "credit": state.get("credit_validation", {}),
        "summary": {
            "order_id": state["order_id"],
            "customer_id": state["customer_id"],
            "total_amount": state["total_amount"],
            "items_count": len(state.get("items_validation", {}).get("validated_items", [])),
            "approved": True
        }
    }
    
    logger.info(f"Orden {state['order_id']} procesada exitosamente")
    
    return state


def error_handler_node(state: OrderState) -> OrderState:
    """
    Nodo de manejo de errores: procesa órdenes rechazadas.
    
    Args:
        state: Estado actual de la orden
        
    Returns:
        Estado actualizado con información de rechazo
    """
    logger.warning(f"Manejando errores para orden {state['order_id']}")
    
    state["status"] = "rejected"
    state["approved"] = False
    
    error_count = len(state["errors"])
    state["message"] = f"Orden {state['order_id']} rechazada. {error_count} error(es) encontrado(s)."
    
    # Compilar detalles de validación con errores
    state["validation_details"] = {
        "customer": state.get("customer_validation", {}),
        "items": state.get("items_validation", {}),
        "credit": state.get("credit_validation", {}),
        "errors": state["errors"],
        "warnings": state["warnings"],
        "summary": {
            "order_id": state["order_id"],
            "customer_id": state.get("customer_id", "N/A"),
            "total_amount": state["total_amount"],
            "approved": False,
            "error_count": error_count
        }
    }
    
    logger.info(f"Orden {state['order_id']} rechazada con {error_count} errores")
    
    return state


# Funciones de enrutamiento condicional

def should_continue_after_customer(state: OrderState) -> Literal["validate_items", "error_handler"]:
    """
    Decide si continuar a validación de items o ir a manejo de errores.
    
    Args:
        state: Estado actual
        
    Returns:
        Nombre del siguiente nodo
    """
    customer_valid = state.get("customer_validation", {}).get("valid", False)
    
    if customer_valid:
        logger.debug("Cliente válido, continuando a validación de items")
        return "validate_items"
    else:
        logger.debug("Cliente inválido, redirigiendo a manejo de errores")
        return "error_handler"


def should_continue_after_items(state: OrderState) -> Literal["check_credit", "error_handler"]:
    """
    Decide si continuar a validación de crédito o ir a manejo de errores.
    
    Args:
        state: Estado actual
        
    Returns:
        Nombre del siguiente nodo
    """
    items_valid = state.get("items_validation", {}).get("valid", False)
    
    if items_valid:
        logger.debug("Items válidos, continuando a verificación de crédito")
        return "check_credit"
    else:
        logger.debug("Items inválidos, redirigiendo a manejo de errores")
        return "error_handler"


def should_continue_after_credit(state: OrderState) -> Literal["process_order", "error_handler"]:
    """
    Decide si procesar la orden o ir a manejo de errores.
    
    Args:
        state: Estado actual
        
    Returns:
        Nombre del siguiente nodo
    """
    has_credit = state.get("credit_validation", {}).get("has_credit", False)
    
    if has_credit:
        logger.debug("Crédito suficiente, procesando orden")
        return "process_order"
    else:
        logger.debug("Crédito insuficiente, redirigiendo a manejo de errores")
        return "error_handler"


# Construcción del grafo

def create_order_validation_graph() -> StateGraph:
    """
    Crea y configura el grafo de validación de órdenes.
    
    Returns:
        StateGraph configurado y compilado
    """
    logger.info("Creando grafo de validación de órdenes")
    
    # Crear el grafo
    workflow = StateGraph(OrderState)
    
    # Agregar nodos
    workflow.add_node("parse_order", parse_order)
    workflow.add_node("validate_customer", validate_customer_node)
    workflow.add_node("validate_items", validate_items_node)
    workflow.add_node("check_credit", check_credit_node)
    workflow.add_node("process_order", process_order_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Definir punto de entrada
    workflow.set_entry_point("parse_order")
    
    # Agregar edges condicionales
    workflow.add_conditional_edges(
        "parse_order",
        lambda state: "validate_customer" if state["status"] == "validating" else "error_handler"
    )
    
    workflow.add_conditional_edges(
        "validate_customer",
        should_continue_after_customer
    )
    
    workflow.add_conditional_edges(
        "validate_items",
        should_continue_after_items
    )
    
    workflow.add_conditional_edges(
        "check_credit",
        should_continue_after_credit
    )
    
    # Agregar edges finales
    workflow.add_edge("process_order", END)
    workflow.add_edge("error_handler", END)
    
    # Compilar el grafo
    app = workflow.compile()
    
    logger.info("Grafo de validación compilado exitosamente")
    
    return app


# Función principal de validación

def validate_order(
    order_id: str,
    customer_id: str,
    items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Valida una orden completa usando el grafo de LangGraph.
    
    Args:
        order_id: ID único de la orden
        customer_id: ID del cliente
        items: Lista de items de la orden
        
    Returns:
        Dict con resultado de validación:
        - status: estado final ("approved" o "rejected")
        - approved: bool indicando si fue aprobada
        - message: mensaje descriptivo
        - total_amount: monto total de la orden
        - errors: lista de errores encontrados
        - warnings: lista de advertencias
        - validation_details: detalles completos de validación
    """
    logger.info(f"Iniciando validación de orden {order_id}")
    
    # Crear estado inicial
    initial_state: OrderState = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items,
        "customer_validation": None,
        "items_validation": None,
        "credit_validation": None,
        "status": "pending",
        "errors": [],
        "warnings": [],
        "total_amount": 0.0,
        "approved": False,
        "message": "",
        "validation_details": {}
    }
    
    try:
        # Crear y ejecutar el grafo
        app = create_order_validation_graph()
        final_state = app.invoke(initial_state)
        
        # Preparar resultado
        result = {
            "status": final_state["status"],
            "approved": final_state["approved"],
            "message": final_state["message"],
            "total_amount": final_state["total_amount"],
            "errors": final_state["errors"],
            "warnings": final_state["warnings"],
            "validation_details": final_state["validation_details"]
        }
        
        logger.info(f"Validación completada para orden {order_id}: {result['status']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error crítico en validación de orden {order_id}: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "approved": False,
            "message": error_msg,
            "total_amount": 0.0,
            "errors": [error_msg],
            "warnings": [],
            "validation_details": {}
        }