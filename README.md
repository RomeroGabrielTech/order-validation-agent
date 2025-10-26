# 🤖 Order Validation Agent

I created this PoC immediately after the interview to validate my skillset with your exact stack.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An intelligent pre-order validation system built with LangGraph that automates customer verification and credit checks through a multi-stage conditional workflow.

## 🎯 Overview

This agent validates orders before processing by checking:
- ✅ Customer existence in the database
- 💰 Available credit limits
- 📦 Order items validity
- 🔄 Data integrity and consistency

The system uses **LangGraph** to implement a state machine with conditional routing, automatically rejecting invalid orders and providing detailed error messages.

## ✨ Features

- **Multi-stage Validation**: Sequential validation with fail-fast behavior
- **Conditional Routing**: Smart workflow navigation based on validation results
- **Comprehensive Error Handling**: Detailed error messages for debugging
- **Credit Management**: Real-time credit availability checks
- **Extensible Architecture**: Easy to add new validation rules
- **Test Suite**: Complete test coverage with pytest
- **Rich CLI Output**: Beautiful console output using Rich library
- **Logging**: Detailed logging with Loguru

## 🏗️ Architecture

```
┌─────────────┐
│ Order JSON  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  parse_order     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│validate_customer │──❌─→ Error Handler
└──────┬───────────┘
       │✅
       ▼
┌──────────────────┐
│ validate_items   │──❌─→ Error Handler
└──────┬───────────┘
       │✅
       ▼
┌──────────────────┐
│  check_credit    │──❌─→ Error Handler
└──────┬───────────┘
       │✅
       ▼
┌──────────────────┐
│ process_order    │
│   ✅ APPROVED    │
└──────────────────┘
```

### Validation Flow

1. **Parse Order**: Extracts customer_id, amount, and items from JSON
2. **Validate Customer**: Checks if customer exists and is active
3. **Validate Items**: Verifies item data and calculates totals
4. **Check Credit**: Ensures sufficient credit is available
5. **Process Order**: Approves order if all validations pass
6. **Error Handler**: Captures and reports validation failures

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/order-validation-agent.git
cd order-validation-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 📖 Usage

### Basic Usage

```python
from src.agents.order_validator import validate_order

# Define your order
order = {
    "customer_id": "CUST001",
    "total_amount": 1500.0,
    "items": [
        {"product": "Laptop", "quantity": 1, "price": 1500.0}
    ]
}

# Validate the order
result = validate_order(order)

print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
```

### CLI Usage

```bash
# Run example validations
python src/main.py

# Validate a custom order interactively
python src/main.py --custom

# Show help
python src/main.py --help
```

### Example Output

```
═══════════════════════════════════════════════════════
Pedido ORD001
═══════════════════════════════════════════════════════

Status: APPROVED
Cliente: CUST001
Monto: $1500.00

Validaciones:
  • Cliente existe: ✅
  • Cliente activo: ✅
  • Items válidos: ✅
  • Crédito suficiente: ✅

Crédito Disponible: $4000.00
Mensaje: Pedido aprobado para cliente CUST001...
```

## 🧪 Testing

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_order_validator.py -v

# Run specific test
pytest tests/test_order_validator.py::TestOrderValidation::test_valid_order_approved -v
```

### Test Coverage

The project includes comprehensive tests covering:
- ✅ Valid orders (happy path)
- ❌ Invalid customers
- ❌ Insufficient credit
- ❌ Invalid items
- ❌ Inactive customers
- ⚠️ Edge cases (zero amounts, floating point precision)

## 📊 API Response Format

### Success Response

```json
{
  "status": "approved",
  "customer_id": "CUST001",
  "order_amount": 1500.0,
  "error": null,
  "message": "Pedido aprobado para cliente CUST001...",
  "credit_available": 4000.0,
  "credit_shortage": 0.0,
  "validations": {
    "customer_exists": true,
    "customer_active": true,
    "items_valid": true,
    "has_credit": true
  }
}
```

### Error Response

```json
{
  "status": "rejected",
  "customer_id": "CUST999",
  "order_amount": 500.0,
  "error": "❌ Cliente CUST999 no existe en el sistema",
  "message": "El ID de cliente proporcionado no fue encontrado...",
  "credit_available": 0.0,
  "credit_shortage": 0.0,
  "validations": {
    "customer_exists": false,
    "customer_active": false,
    "items_valid": false,
    "has_credit": false
  }
}
```

## 🗂️ Project Structure

```
order-validation-agent/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── order_validator.py      # Main validation agent
│   ├── tools/
│   │   ├── __init__.py
│   │   └── validation_tools.py     # Validation tools
│   ├── utils/
│   │   └── __init__.py
│   └── main.py                     # CLI entry point
├── tests/
│   ├── __init__.py
│   └── test_order_validator.py     # Test suite
├── config/
│   └── config.yaml                 # Configuration file
├── data/
│   └── sample_data/
│       └── sample_orders.json      # Sample orders
├── docs/                           # Documentation
├── .gitignore
├── requirements.txt
└── README.md
```

## 🛠️ Configuration

Edit `config/config.yaml` to customize:

```yaml
# Validation rules
validation_rules:
  max_order_amount: 100000.0
  min_order_amount: 0.0
  max_items_per_order: 100
  credit_check_enabled: true
  customer_check_enabled: true

# Logging
logging:
  level: "INFO"
  format: "<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"
```

## 🔧 Tech Stack

- **LangGraph**: State machine and workflow orchestration
- **LangChain**: Tool definitions and chains
- **Pydantic**: Data validation and settings management
- **Pytest**: Testing framework
- **Rich**: Beautiful terminal output
- **Loguru**: Advanced logging
- **PyYAML**: Configuration management

## 🚦 Validation Rules

### Customer Validation
- Customer must exist in the database
- Customer account must be active
- Customer ID format must be valid

### Credit Validation
- Available credit = Credit Limit - Used Credit
- Order amount must not exceed available credit
- Credit calculations use 2 decimal precision

### Items Validation
- Order must contain at least one item
- Each item must have: product name, quantity > 0, price > 0
- Calculated total must match declared total (±$0.01 tolerance)

## 🔮 Future Enhancements

- [ ] **Inventory Check**: Validate product availability
- [ ] **Fraud Detection**: Integrate fraud scoring system
- [ ] **Address Validation**: Verify shipping addresses
- [ ] **Payment Gateway**: Connect to payment processors
- [ ] **Database Integration**: PostgreSQL/MySQL support
- [ ] **API Endpoints**: REST API with FastAPI
- [ ] **Async Support**: Asynchronous validation pipeline
- [ ] **Caching**: Redis for customer/credit data
- [ ] **Notifications**: Email/SMS alerts for rejections
- [ ] **Dashboard**: Web UI for monitoring validations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## 🔑 Configuración de API Key

### Obtener tu API Key de Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Click en **"Create API Key"**
4. Copia la API key generada

### Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env y agregar tu API key
# GOOGLE_API_KEY=tu_api_key_aquí
```

**⚠️ IMPORTANTE:** Nunca subas tu archivo `.env` a GitHub. Ya está incluido en `.gitignore`.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🙏 Acknowledgments

- [LangChain Team](https://github.com/langchain-ai) for LangGraph
- [Anthropic](https://www.anthropic.com/) for Claude AI assistance
- Community contributors

## 📧 Contact

Project Link: [https://github.com/yourusername/order-validation-agent](https://github.com/yourusername/order-validation-agent)

---

⭐ If you find this project useful, please consider giving it a star!
