# Gennie: AI-Driven UI Generation System

A complete implementation of the "gennie" architecture - an AI-driven system that translates natural language prompts into production-ready UI components through a sophisticated multi-agent workflow.

## 🎯 Project Overview

**Core Data Flow:**
```
CLI Analysis → JSON Schemas → SDK → Router Agent → Dynamic Tools → Component Rendering
     ↓              ↓           ↓         ↓              ↓              ↓
Component Props → Single Source → React → Category → Filtered Tools → UI Response
```

This system provides:
1. **Natural Language Understanding** with Google Gemini integration
2. **Intelligent Component Selection** via hierarchical agent routing
3. **Schema-Driven Architecture** ensuring type safety across the stack
4. **Dynamic Tool Generation** from JSON schemas at runtime
5. **Production-Ready UI Rendering** with shadcn/ui components

## 🏗️ Architecture

### Monorepo Structure
```
next-gen-ui/
├── apps/web/                   # Next.js React application
├── packages/
│   ├── sdk/                   # TypeScript SDK (@gennie/sdk)
│   └── cli/                   # Component management CLI (@gennie/cli)
├── services/agent-service/    # FastAPI + LangGraph backend
└── schemas/                   # JSON schemas (single source of truth)
```

### Multi-Agent Workflow
1. **Answer Agent**: Generates natural language responses using Google Gemini
2. **Router Agent**: Categorizes queries and filters available tools by category
3. **UI Agent**: Selects specific components using dynamically generated tools
4. **Dynamic Tool Generator**: Creates LangChain tools from JSON schemas at runtime

### Key Components
- **Schema-Driven System**: JSON schemas in `/schemas` directory are the single source of truth
- **CLI Component Analysis**: Analyzes React components and generates schemas automatically
- **SDK Abstraction**: TypeScript SDK handles schema loading and backend communication
- **Category-Based Routing**: Scales to hundreds of components via intelligent filtering

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** with uv package manager
- **Node.js 18+** with pnpm workspaces
- **GOOGLE_API_KEY** environment variable

### 1. Clone and Install Dependencies
```bash
git clone <repository>
cd next-gen-ui
pnpm install
```

### 2. Backend Setup
```bash
cd services/agent-service
uv sync
# Create .env file with GOOGLE_API_KEY
echo "GOOGLE_API_KEY=your_api_key_here" > app/.env
```

### 3. Generate Schemas (First Time Setup)
```bash
cd packages/cli
pnpm build
node dist/index.js sync --path ../../apps/web/components/ui-components --output ../../schemas
```

### 4. Start Development Servers
```bash
# Terminal 1: Start backend
cd services/agent-service/app && uv run python main.py

# Terminal 2: Start frontend
pnpm dev:web
```

### 5. Open Application
Visit [http://localhost:3000](http://localhost:3000)

## 💡 Example Workflows

### Weather Query
```
User: "What's the weather in Paris?"
→ Answer Agent: Generates weather description
→ Router Agent: Routes to "data_display" category
→ UI Agent: Selects WeatherCard tool from filtered options
→ Frontend: Renders weather card with temperature, conditions, humidity, wind
```

### Data Visualization  
```
User: "Show me Q1 sales data as a chart"
→ Answer Agent: Provides sales analysis
→ Router Agent: Routes to "data_visualization" category
→ UI Agent: Selects ChartCard tool with bar chart configuration
→ Frontend: Renders interactive chart with Recharts
```

### Tabular Data
```
User: "Display user information in a table"
→ Answer Agent: Describes user data structure
→ Router Agent: Routes to "data_display" category
→ UI Agent: Selects DataTable tool with column definitions
→ Frontend: Renders sortable, searchable table with shadcn/ui
```

### General Information
```
User: "Explain machine learning"
→ Answer Agent: Provides comprehensive explanation
→ Router Agent: Routes to "content" category
→ UI Agent: Selects InfoCard tool for content display
→ Frontend: Renders formatted information card
```

## 🎨 Available Components

All components are automatically discovered and categorized by the system:

### Component Categories
- **`data_display`**: Tables, lists, weather cards - for showing structured data
- **`data_visualization`**: Charts, graphs, analytics - for visual data representation  
- **`content`**: Info cards, text content, explanations - for general information
- **`general`**: Fallback category for miscellaneous components

### Core Components

#### WeatherCard (`data_display`)
- **Purpose**: Weather information display with icons and metrics
- **Features**: Temperature, conditions, humidity, wind speed, location
- **Auto-Generated Schema**: Location, temperature, condition, optional weather metrics

#### ChartCard (`data_visualization`)
- **Purpose**: Interactive data visualization with Recharts
- **Types**: Bar, line, pie, area charts with responsive design
- **Auto-Generated Schema**: Title, chart type, data points, axis configuration

#### DataTable (`data_display`)
- **Purpose**: Sortable, searchable tabular data display
- **Features**: Column sorting, search filtering, responsive design
- **Auto-Generated Schema**: Column definitions, row data, search capabilities

#### InfoCard (`content`)
- **Purpose**: General information display with status variants
- **Variants**: Default, success, warning, error styling
- **Auto-Generated Schema**: Title, content, icon, variant type

## 🔧 Development

### Adding New Components (Fully Automated)

1. **Create React Component**: Add to `apps/web/components/ui-components/`
2. **Define TypeScript Interface**: Add props interface to `apps/web/lib/types.ts` 
3. **Generate Schema**: Run CLI sync command to analyze component and auto-generate JSON schema
4. **Update Component Renderer**: Add new component type to the renderer mapping
5. **Test Integration**: Schema automatically becomes available to Python agents

The system automatically handles:
- Tool generation from schemas at runtime
- Category routing based on component naming conventions
- Type safety between frontend and backend
- Dynamic component loading and rendering

### Essential Development Commands

```bash
# Generate schemas from React components
cd packages/cli && node dist/index.js sync --path ../../apps/web/components/ui-components --output ../../schemas

# Start frontend development server
pnpm dev:web

# Start backend with auto-reload
cd services/agent-service/app && uv run python main.py

# Build all packages
pnpm -w build:web  # Web app only
cd packages/cli && pnpm build     # CLI package  
cd packages/sdk && pnpm build     # SDK package

# Format Python code
cd services/agent-service/app && uv run black . && uv run isort .

# Run Python tests
cd services/agent-service/app && uv run pytest
```

### Project Structure (Actual)
```
next-gen-ui/
├── apps/web/                   # Next.js React application
│   ├── components/ui-components/   # Auto-analyzed UI components
│   ├── lib/                   # Types, utilities, SDK integration
│   └── app/                   # Next.js App Router
├── packages/
│   ├── sdk/                   # TypeScript SDK (@gennie/sdk)
│   └── cli/                   # Component analyzer CLI (@gennie/cli)
├── services/agent-service/    # Python backend
│   ├── app/agents/           # Multi-agent system (Router, UI, Answer)
│   ├── app/schemas/          # Pydantic schemas
│   └── app/main.py          # FastAPI application
├── schemas/                   # Generated JSON schemas (single source of truth)
├── pnpm-workspace.yaml       # Monorepo configuration
└── CLAUDE.md                 # Development guidance
```

## 🛠️ Technology Stack

### Backend (Python Ecosystem)
- **LangGraph**: Multi-agent orchestration and workflow management
- **LangChain**: LLM integration and dynamic tool generation
- **FastAPI**: Modern async Python web framework
- **Pydantic**: Data validation and schema generation
- **Google Gemini**: Gemini 2.0 Flash for natural language processing
- **uv**: Ultra-fast Python package and dependency manager

### Frontend (TypeScript Ecosystem)
- **Next.js 15**: React framework with App Router and Turbopack
- **TypeScript 5**: Full type safety across the entire stack
- **shadcn/ui**: Modern component library built on Radix UI primitives
- **Tailwind CSS 4**: Utility-first CSS with latest features
- **Recharts**: Composable charting library for React
- **Lucide React**: Beautiful, customizable icon library
- **pnpm**: Fast, disk space efficient package manager

### Development Tools
- **@gennie/cli**: Custom CLI for component analysis and schema generation
- **@gennie/sdk**: TypeScript SDK for seamless backend communication
- **uv**: Python dependency management and virtual environments
- **ESLint 9**: Code linting with modern configuration
- **Prettier**: Code formatting for consistent style

## 📋 Features

### Intelligent Multi-Agent System
- ✅ **Answer Agent** with Google Gemini integration for natural language understanding
- ✅ **Router Agent** with category-based tool filtering for scalability
- ✅ **UI Agent** with dynamic component selection from filtered tools
- ✅ **Dynamic Tool Generator** creating LangChain tools from JSON schemas at runtime
- ✅ **LangGraph workflow** orchestration with state management
- ✅ **Error handling** and graceful fallback mechanisms

### Schema-Driven Architecture
- ✅ **CLI Component Analysis** automatically discovering React components
- ✅ **JSON Schema Generation** from TypeScript interfaces and React props
- ✅ **Single Source of Truth** ensuring consistency across frontend and backend
- ✅ **Type Safety** with automatic validation and serialization
- ✅ **Hot Reloading** of schemas during development

### API & Communication
- ✅ **RESTful endpoints** for query processing with async support
- ✅ **WebSocket support** for real-time communication (future feature)
- ✅ **CORS configuration** for seamless frontend integration
- ✅ **Health checks** and comprehensive error responses
- ✅ **SDK Integration** with TypeScript client library

### Frontend Interface
- ✅ **Modern chat interface** with message history and typing indicators
- ✅ **Dynamic component rendering** based on intelligent agent decisions
- ✅ **Loading states** with skeleton components and progress indicators
- ✅ **Error boundaries** with user-friendly error messages
- ✅ **Fully responsive design** optimized for desktop and mobile
- ✅ **Context-aware theming** with dark/light mode support

### Component Ecosystem
- ✅ **Auto-discovered components** with zero manual configuration
- ✅ **Category-based organization** for intelligent routing and scaling
- ✅ **shadcn/ui integration** ensuring consistent, accessible design
- ✅ **Interactive features** including sorting, searching, filtering
- ✅ **Extensible architecture** supporting hundreds of components

## 🎯 Use Cases

- **Dashboard Generation**: Convert natural language requests into interactive data visualizations
- **Report Creation**: Generate formatted reports with mixed content types and automatic component selection
- **Data Exploration**: Interactive exploration of datasets through conversational interface
- **Content Management**: Dynamic content presentation with intelligent component routing
- **Business Intelligence**: Natural language interface for business metrics and KPI visualization
- **Rapid Prototyping**: Quickly test UI concepts through natural language descriptions
- **Component Documentation**: Automatic generation of component usage examples and schemas

## 🔍 Key Implementation Details

### CLI Tool (@gennie/cli)
- **Component Analysis**: Parses React components and extracts prop interfaces
- **Schema Generation**: Creates JSON schemas with LangChain tool definitions
- **Category Detection**: Automatically categorizes components based on naming conventions
- **Validation**: Ensures type safety and schema correctness

### SDK Integration (@gennie/sdk)
- **Schema Loading**: Loads JSON schemas from static files or API endpoints
- **Type Safety**: Provides TypeScript interfaces for all component interactions
- **Error Handling**: Graceful error recovery with detailed error messages
- **Caching**: Intelligent caching of schemas and API responses

### Backend Architecture
- **Dynamic Tool Creation**: Runtime generation of LangChain tools from schemas
- **Category Routing**: Intelligent filtering of available tools based on query analysis
- **State Management**: LangGraph state management for complex multi-step workflows
- **Extensibility**: Easy addition of new agents and tool generators

## 🤝 Contributing

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Install Dependencies**: Run `pnpm install` to install all workspace dependencies
3. **Generate Schemas**: Use the CLI to sync component schemas before development
4. **Create Feature Branch**: Create a descriptive branch for your changes
5. **Follow Conventions**: Use existing code patterns and naming conventions
6. **Test Changes**: Ensure all tests pass and add new tests for new features
7. **Update Documentation**: Update CLAUDE.md if adding significant features
8. **Submit Pull Request**: Create a PR with a clear description of changes

### Development Guidelines
- Follow the existing monorepo structure and naming conventions
- Use the provided CLI tools for schema generation and component management
- Maintain type safety across the entire stack
- Add appropriate error handling and fallback mechanisms
- Document any new agents, tools, or architectural patterns

## 📄 License

MIT License - see LICENSE file for details