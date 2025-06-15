# Smart Order Intake System

A modular, AI-powered system that automatically parses customer emails to extract product order information, validates it against a product catalog, and outputs structured JSON with intelligent suggestions.

## 🏗️ **Modular Architecture**

The system follows **SOLID principles** with clear separation of concerns:

```
├── core/                    # Core models and interfaces
│   ├── models.py           # Pydantic data models
│   ├── interfaces.py       # Protocols and abstract classes
│   └── exceptions.py       # Custom exceptions
├── parsing/                # Email parsing logic
│   ├── email_parser.py     # LangChain-based parser
│   └── email_data.py       # Email data models
├── prompts/                # LangChain prompt templates
│   └── email_extraction.py # Email extraction prompts
├── validation/             # Order validation logic
│   ├── result.py          # Validation result classes
│   └── catalog_validator.py # Catalog-based validation
├── data_sources/           # Data source implementations
│   └── catalog_csv.py     # CSV catalog data source
├── processing/             # Order processing logic
│   ├── order_processor.py  # Main order processor
│   └── llm_factory.py     # LLM provider factory
├── ui/                     # Streamlit UI components
│   ├── display.py         # Order display components
│   └── config.py          # Configuration display
└── main.py                 # Application entry point
```

## ✨ **Features**

- **🔌 Modular LLM Providers**: Support for OpenAI, Anthropic, and Google models
- **🎯 Advanced Email Parsing**: Using LangChain with Pydantic output parsing
- **🧠 Intelligent Validation**: Product catalog validation with smart suggestions
- **📊 MOQ & Stock Checking**: Minimum order quantity and stock availability verification
- **🎨 Modern UI**: Clean Streamlit interface with real-time provider switching
- **📋 Structured Output**: Comprehensive JSON output with validation results
- **🏗️ SOLID Architecture**: Clean, maintainable, and extensible codebase

## 🚀 **Quick Start**

1. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd smart-order-intake
   python scripts/setup.py
   ```

2. **Configure Environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Run Application**:
   ```bash
   uv run streamlit run main.py
   ```

## ⚙️ **Configuration**

Edit `.env` file:
```env
# Required for OpenAI (default provider)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Alternative providers
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.0
```

## 🧩 **Modular Design Principles**

### **Single Responsibility**
- Each module handles one specific concern
- Clear separation between parsing, validation, and display
- Individual classes have focused responsibilities

### **Open/Closed Principle**
- Easy to add new LLM providers via `LLMProvider` interface
- New validation rules via `OrderValidator` protocol
- Extensible data sources via `CatalogDataSource` protocol

### **Liskov Substitution**
- All implementations honor their protocol contracts
- Consistent interfaces across modules

### **Interface Segregation**
- Small, focused protocols
- No unnecessary dependencies

### **Dependency Inversion**
- High-level modules depend on abstractions
- Dependencies injected through constructors
- Easy to swap implementations

## 📝 **Usage Examples**

### **Basic Usage**
```python
from main import initialize_components
from processing.order_processor import SmartOrderProcessor

# Initialize components
parser, validator = initialize_components("openai")
processor = SmartOrderProcessor(parser, validator)

# Process email
order = processor.process_order(email_text)
```

### **Custom LLM Provider**
```python
from processing.llm_factory import LLMFactory
from core.interfaces import LLMProvider

class CustomProvider(LLMProvider):
    def create_llm(self, **kwargs):
        # Your custom LLM implementation
        pass
    
    def get_default_config(self):
        return {"model": "custom-model"}

# Register and use
LLMFactory.register_provider("custom", CustomProvider())
llm = LLMFactory.create_llm("custom")
```

### **Custom Data Source**
```python
from core.interfaces import CatalogDataSource

class DatabaseCatalogSource(CatalogDataSource):
    def get_product_details(self, sku: str):
        # Database lookup implementation
        pass
    
    def find_similar_products(self, sku: str):
        # Similarity search implementation
        pass
```

## 🧪 **Testing**

```bash
# Run tests with coverage
uv run pytest --cov=. tests/

# Run specific module tests
uv run pytest tests/test_parsing/ -v

# Format and lint code
uv run ruff format .
uv run ruff check . --fix

# Run all checks (format + lint + test)
python scripts/dev.py check
```

## 📊 **Validation Features**

The system provides intelligent suggestions for:

1. **Invalid SKUs**: Suggests similar products
2. **MOQ Violations**: Recommends optimal quantities
3. **Stock Issues**: Suggests available quantities
4. **Out of Stock**: Provides alternatives

## 🔧 **Extension Points**

- **New LLM Providers**: Implement `LLMProvider` interface
- **Custom Validators**: Implement `OrderValidator` protocol
- **Data Sources**: Implement `CatalogDataSource` protocol
- **UI Components**: Add new display components in `ui/`
- **Prompt Templates**: Add new templates in `prompts/`

## 📈 **Performance**

- **Modular Loading**: Only load required components
- **Efficient Caching**: Smart data source caching
- **Parallel Processing**: Support for concurrent validation
- **Memory Efficient**: Lazy loading of large datasets

## 🛠️ **Development Workflow**

Using `uv` for fast package management and `ruff` for formatting/linting:

```bash
# Quick setup
python scripts/setup.py

# Development commands
python scripts/dev.py format    # Format code
python scripts/dev.py lint      # Lint code  
python scripts/dev.py test      # Run tests
python scripts/dev.py app       # Run app
python scripts/dev.py check     # All checks

# Direct uv commands
uv sync                          # Install dependencies
uv sync --extra dev             # Install with dev dependencies
uv run streamlit run main.py   # Run app
uv run pytest                  # Run tests
uv run ruff format .           # Format code
uv run ruff check . --fix      # Lint and fix
```

## 🤝 **Contributing**

1. Follow the modular architecture
2. Implement appropriate protocols/interfaces
3. Add comprehensive tests
4. Update documentation
5. Ensure SOLID principles compliance

The system is designed to be **simple yet powerful**, maintaining clean separation of concerns while providing comprehensive functionality for order processing! 🎯
