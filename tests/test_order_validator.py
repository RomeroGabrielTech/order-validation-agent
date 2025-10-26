"""
Tests para el sistema de validación de órdenes.
Incluye tests para herramientas, agente y casos edge.
"""

import pytest
from typing import Dict, Any, List

from src.tools.validation_tools import (
    validate_customer_exists,
    check_customer_credit,
    validate_order_items,
    MOCK_CUSTOMERS,
    MOCK_PRODUCTS
)
from src.agents.order_validator import validate_order


class TestValidationTools:
    """Tests para las herramientas de validación."""
    
    def test_validate_customer_exists_valid(self):
        """Test: Cliente válido y activo."""
        result = validate_customer_exists.invoke({"customer_id": "CUST001"})
        
        assert result["valid"] is True
        assert result["exists"] is True
        assert result["active"] is True
        assert result["customer_data"] is not None
        assert result["customer_data"]["id"] == "CUST001"
        assert "válido y activo" in result["message"]
    
    def test_validate_customer_exists_inactive(self):
        """Test: Cliente existe pero está inactivo."""
        result = validate_customer_exists.invoke({"customer_id": "CUST003"})
        
        assert result["valid"] is False
        assert result["exists"] is True
        assert result["active"] is False
        assert result["customer_data"] is not None
        assert "inactivo" in result["message"]
    
    def test_validate_customer_exists_not_found(self):
        """Test: Cliente no existe."""
        result = validate_customer_exists.invoke({"customer_id": "CUST999"})
        
        assert result["valid"] is False
        assert result["exists"] is False
        assert result["active"] is False
        assert result["customer_data"] is None
        assert "no existe" in result["message"]
    
    def test_validate_customer_exists_empty_id(self):
        """Test: ID de cliente vacío."""
        result = validate_customer_exists.invoke({"customer_id": ""})
        
        assert result["valid"] is False
        assert result["exists"] is False
        assert "no proporcionado" in result["message"]
    
    def test_check_customer_credit_sufficient(self):
        """Test: Cliente con crédito suficiente."""
        # CUST001 tiene límite de 10000 y balance de 2000, disponible: 8000
        result = check_customer_credit.invoke({
            "customer_id": "CUST001",
            "order_amount": 5000.0
        })
        
        assert result["has_credit"] is True
        assert result["credit_limit"] == 10000.0
        assert result["current_balance"] == 2000.0
        assert result["available_credit"] == 8000.0
        assert result["required_amount"] == 5000.0
        assert "suficiente" in result["message"].lower()
    
    def test_check_customer_credit_insufficient(self):
        """Test: Cliente con crédito insuficiente."""
        # CUST002 tiene límite de 5000 y balance de 4500, disponible: 500
        result = check_customer_credit.invoke({
            "customer_id": "CUST002",
            "order_amount": 1000.0
        })
        
        assert result["has_credit"] is False
        assert result["available_credit"] == 500.0
        assert result["required_amount"] == 1000.0
        assert "insuficiente" in result["message"].lower()
    
    def test_check_customer_credit_customer_not_found(self):
        """Test: Verificar crédito de cliente inexistente."""
        result = check_customer_credit.invoke({
            "customer_id": "CUST999",
            "order_amount": 100.0
        })
        
        assert result["has_credit"] is False
        assert result["credit_limit"] == 0.0
        assert "no encontrado" in result["message"]
    
    def test_validate_order_items_valid(self):
        """Test: Items válidos con stock suficiente."""
        items = [
            {"product_id": "PROD001", "quantity": 2, "unit_price": 1200.0},
            {"product_id": "PROD002", "quantity": 5, "unit_price": 25.0}
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is True
        assert result["total_amount"] == 2525.0  # (2 * 1200) + (5 * 25)
        assert len(result["validated_items"]) == 2
        assert len(result["invalid_items"]) == 0
        assert "válidos" in result["message"]
    
    def test_validate_order_items_insufficient_stock(self):
        """Test: Item sin stock suficiente."""
        items = [
            {"product_id": "PROD005", "quantity": 10, "unit_price": 120.0}
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is False
        assert len(result["invalid_items"]) == 1
        assert "Stock insuficiente" in result["invalid_items"][0]["reason"]
    
    def test_validate_order_items_product_not_found(self):
        """Test: Producto no existe."""
        items = [
            {"product_id": "PROD999", "quantity": 1, "unit_price": 100.0}
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is False
        assert len(result["invalid_items"]) == 1
        assert "no existe" in result["invalid_items"][0]["reason"]
    
    def test_validate_order_items_invalid_quantity(self):
        """Test: Cantidad inválida (cero o negativa)."""
        items = [
            {"product_id": "PROD001", "quantity": 0, "unit_price": 1200.0}
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is False
        assert len(result["invalid_items"]) == 1
        assert "mayor a 0" in result["invalid_items"][0]["reason"]
    
    def test_validate_order_items_wrong_price(self):
        """Test: Precio incorrecto."""
        items = [
            {"product_id": "PROD001", "quantity": 1, "unit_price": 999.0}  # Precio real: 1200
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is False
        assert len(result["invalid_items"]) == 1
        assert "Precio incorrecto" in result["invalid_items"][0]["reason"]
    
    def test_validate_order_items_empty_list(self):
        """Test: Lista de items vacía."""
        result = validate_order_items.invoke({"items": []})
        
        assert result["valid"] is False
        assert result["total_amount"] == 0.0
        assert "No se proporcionaron items" in result["message"]
    
    def test_validate_order_items_mixed_valid_invalid(self):
        """Test: Mezcla de items válidos e inválidos."""
        items = [
            {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0},  # Válido
            {"product_id": "PROD999", "quantity": 1, "unit_price": 100.0},   # No existe
            {"product_id": "PROD002", "quantity": 2, "unit_price": 25.0}     # Válido
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is False
        assert len(result["validated_items"]) == 2
        assert len(result["invalid_items"]) == 1


class TestOrderValidator:
    """Tests para el agente de validación de órdenes."""
    
    def test_validate_order_success(self):
        """Test: Orden completamente válida."""
        result = validate_order(
            order_id="ORD-TEST-001",
            customer_id="CUST001",
            items=[
                {"product_id": "PROD001", "quantity": 2, "unit_price": 1200.0},
                {"product_id": "PROD002", "quantity": 5, "unit_price": 25.0}
            ]
        )
        
        assert result["status"] == "approved"
        assert result["approved"] is True
        assert result["total_amount"] == 2525.0
        assert len(result["errors"]) == 0
        assert "aprobada exitosamente" in result["message"]
    
    def test_validate_order_customer_not_found(self):
        """Test: Cliente no existe."""
        result = validate_order(
            order_id="ORD-TEST-002",
            customer_id="CUST999",
            items=[
                {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0}
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert len(result["errors"]) > 0
        assert any("no existe" in error for error in result["errors"])
    
    def test_validate_order_customer_inactive(self):
        """Test: Cliente inactivo."""
        result = validate_order(
            order_id="ORD-TEST-003",
            customer_id="CUST003",
            items=[
                {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0}
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert any("inactivo" in error for error in result["errors"])
    
    def test_validate_order_insufficient_credit(self):
        """Test: Crédito insuficiente."""
        result = validate_order(
            order_id="ORD-TEST-004",
            customer_id="CUST002",  # Tiene solo 500 disponible
            items=[
                {"product_id": "PROD001", "quantity": 5, "unit_price": 1200.0}  # Total: 6000
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert any("insuficiente" in error.lower() for error in result["errors"])
    
    def test_validate_order_invalid_items(self):
        """Test: Items inválidos."""
        result = validate_order(
            order_id="ORD-TEST-005",
            customer_id="CUST001",
            items=[
                {"product_id": "PROD999", "quantity": 1, "unit_price": 100.0}
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_order_no_stock(self):
        """Test: Producto sin stock."""
        result = validate_order(
            order_id="ORD-TEST-006",
            customer_id="CUST001",
            items=[
                {"product_id": "PROD005", "quantity": 5, "unit_price": 120.0}  # Stock: 0
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert any("stock" in error.lower() for error in result["errors"])
    
    def test_validate_order_missing_order_id(self):
        """Test: Orden sin ID."""
        result = validate_order(
            order_id="",
            customer_id="CUST001",
            items=[
                {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0}
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert any("orden no proporcionado" in error.lower() for error in result["errors"])
    
    def test_validate_order_empty_items(self):
        """Test: Orden sin items."""
        result = validate_order(
            order_id="ORD-TEST-007",
            customer_id="CUST001",
            items=[]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert any("items" in error.lower() for error in result["errors"])
    
    def test_validate_order_validation_details_structure(self):
        """Test: Estructura de validation_details."""
        result = validate_order(
            order_id="ORD-TEST-008",
            customer_id="CUST001",
            items=[
                {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0}
            ]
        )
        
        assert "validation_details" in result
        assert "customer" in result["validation_details"]
        assert "items" in result["validation_details"]
        assert "credit" in result["validation_details"]
        assert "summary" in result["validation_details"]
    
    def test_validate_order_large_order(self):
        """Test: Orden grande con múltiples items."""
        result = validate_order(
            order_id="ORD-TEST-009",
            customer_id="CUST005",  # Límite alto: 20000, balance: 15000, disponible: 5000
            items=[
                {"product_id": "PROD001", "quantity": 2, "unit_price": 1200.0},
                {"product_id": "PROD002", "quantity": 10, "unit_price": 25.0},
                {"product_id": "PROD003", "quantity": 5, "unit_price": 45.0},
                {"product_id": "PROD004", "quantity": 1, "unit_price": 350.0}
            ]
        )
        
        # Total: (2*1200) + (10*25) + (5*45) + (1*350) = 2400 + 250 + 225 + 350 = 3225
        assert result["total_amount"] == 3225.0
        
        if result["approved"]:
            assert result["status"] == "approved"
            assert len(result["errors"]) == 0
        else:
            assert result["status"] == "rejected"


class TestEdgeCases:
    """Tests para casos edge y situaciones especiales."""
    
    def test_zero_price_item(self):
        """Test: Item con precio cero."""
        items = [
            {"product_id": "PROD001", "quantity": 1, "unit_price": 0.0}
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        # Debería fallar porque el precio real es 1200, no 0
        assert result["valid"] is False
    
    def test_negative_quantity(self):
        """Test: Cantidad negativa."""
        items = [
            {"product_id": "PROD001", "quantity": -5, "unit_price": 1200.0}
        ]
        
        result = validate_order_items.invoke({"items": items})
        
        assert result["valid"] is False
        assert len(result["invalid_items"]) == 1
    
    def test_customer_at_credit_limit(self):
        """Test: Cliente en el límite exacto de crédito."""
        # CUST005: límite 20000, balance 15000, disponible 5000
        result = check_customer_credit.invoke({
            "customer_id": "CUST005",
            "order_amount": 5000.0
        })
        
        assert result["has_credit"] is True
        assert result["available_credit"] == 5000.0
    
    def test_customer_exceeds_credit_by_one_cent(self):
        """Test: Cliente excede crédito por un centavo."""
        result = check_customer_credit.invoke({
            "customer_id": "CUST005",
            "order_amount": 5000.01
        })
        
        assert result["has_credit"] is False
    
    def test_multiple_validation_errors(self):
        """Test: Múltiples errores de validación simultáneos."""
        result = validate_order(
            order_id="ORD-TEST-010",
            customer_id="CUST001",  # Cliente válido para que continúe a validar items
            items=[
                {"product_id": "PROD999", "quantity": 1, "unit_price": 100.0},  # No existe
                {"product_id": "PROD005", "quantity": 10, "unit_price": 120.0}  # Sin stock
            ]
        )
        
        assert result["status"] == "rejected"
        assert result["approved"] is False
        assert len(result["errors"]) >= 2  # Items inválidos (múltiples errores)


# Fixtures para pytest

@pytest.fixture
def valid_order_data():
    """Fixture con datos de orden válida."""
    return {
        "order_id": "ORD-FIXTURE-001",
        "customer_id": "CUST001",
        "items": [
            {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0}
        ]
    }


@pytest.fixture
def invalid_customer_order_data():
    """Fixture con datos de orden con cliente inválido."""
    return {
        "order_id": "ORD-FIXTURE-002",
        "customer_id": "CUST999",
        "items": [
            {"product_id": "PROD001", "quantity": 1, "unit_price": 1200.0}
        ]
    }


def test_with_valid_fixture(valid_order_data):
    """Test usando fixture de orden válida."""
    result = validate_order(**valid_order_data)
    assert result["approved"] is True


def test_with_invalid_fixture(invalid_customer_order_data):
    """Test usando fixture de orden inválida."""
    result = validate_order(**invalid_customer_order_data)
    assert result["approved"] is False