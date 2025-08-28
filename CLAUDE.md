# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development
```bash
# Start frontend development server
pnpm dev:web

# Start backend API server (requires GOOGLE_API_KEY environment variable)
cd services/agent-service/app && uv run python main.py

# Generate schemas from React components
cd packages/cli && node dist/index.js sync --path ../../apps/web/components/ui-components --output ../../schemas

# Build all packages
pnpm -w build:web  # Web app only
cd packages/cli && pnpm build     # CLI package
cd packages/sdk && pnpm build     # SDK package
```

### Backend Development
```bash
# Install Python dependencies
cd services/agent-service && uv sync

# Format Python code
cd services/agent-service/app && uv run black .
cd services/agent-service/app && uv run isort .

# Run Python tests
cd services/agent-service/app && uv run pytest
```

### Package Management
```bash
# Install dependencies for all workspaces
pnpm install

# Add dependency to specific workspace
pnpm add <package> --filter web
pnpm add <package> --filter cli
pnpm add <package> --filter sdk
```

## Architecture Overview

### Gennie: AI-Driven UI Generation System

This is a complete implementation of the "gennie" architecture - an AI-driven system that translates natural language prompts into production-ready UI components through a sophisticated multi-agent workflow.

**Core Data Flow:**
```
CLI Analysis → JSON Schemas → SDK → Router Agent → Dynamic Tools → Component Rendering
     ↓              ↓           ↓         ↓              ↓              ↓
Component Props → Single Source → React → Category → Filtered Tools → UI Response
```

### Key Architecture Components

1. **Schema-Driven System**: JSON schemas in `/schemas` directory are the single source of truth
2. **Hierarchical Agent Routing**: Router Agent → UI Agent with category-based tool filtering  
3. **Dynamic Tool Generation**: Python backend creates LangChain tools from JSON schemas
4. **CLI Component Analysis**: Analyzes React components and generates schemas automatically
5. **SDK Abstraction**: TypeScript SDK handles schema loading and backend communication

### Monorepo Structure

**Frontend (TypeScript Ecosystem):**
- `apps/web/` - Next.js React application using shadcn/ui
- `packages/sdk/` - TypeScript SDK for backend communication (`@gennie/sdk`)
- `packages/cli/` - CLI tool for component management (`@gennie/cli`)

**Backend (Python):**
- `services/agent-service/` - FastAPI + LangGraph multi-agent system

**Schemas (Language-Agnostic):**
- `/schemas/` - JSON schemas defining UI component contracts

### Multi-Agent Workflow

1. **Answer Agent**: Generates natural language responses using Google Gemini
2. **Router Agent**: Categorizes queries and filters available tools by category
3. **UI Agent**: Selects specific components using dynamically generated tools
4. **Dynamic Tool Generator**: Creates LangChain tools from JSON schemas at runtime

### Component Categories
- `data_display` - Tables, lists, weather cards
- `data_visualization` - Charts, graphs, analytics
- `content` - Info cards, text content, explanations
- `general` - Fallback category for miscellaneous components

## Critical Implementation Details

### Schema Generation Workflow
1. CLI analyzes React components in `apps/web/components/ui-components/`
2. Generates JSON schemas with tool definitions for Python backend
3. Schemas include component props, types, validation rules, and LangChain tool configs
4. Frontend loads schemas statically from `/public/schemas/`

### Backend Tool System
- `DynamicToolGenerator` creates LangChain tools from JSON schemas
- Each tool corresponds to a UI component with specific parameters
- Router Agent filters tools by category for scalability (supports hundreds of components)
- UI Agent uses filtered tools to make component selections

### Frontend Integration
- `GennieProvider` context initializes SDK with schemas
- `QueryInterface` component uses SDK instead of direct API calls
- `ComponentRenderer` dynamically renders components based on agent responses
- Static schema serving from `/public/schemas/` directory

### Environment Requirements
- **Python 3.12+** with uv package manager
- **Node.js 18+** with pnpm workspaces
- **GOOGLE_API_KEY** environment variable for Gemini API
- **TypeScript 5+** for type safety across packages

## Adding New UI Components

1. **Create React Component**: Add to `apps/web/components/ui-components/`
2. **Define TypeScript Interface**: Add props interface to `apps/web/lib/types.ts`
3. **Generate Schema**: Run CLI sync command to analyze component and generate JSON schema
4. **Update Component Renderer**: Add new component type to the renderer
5. **Test Integration**: Schema automatically becomes available to Python agents

The system automatically handles:
- Tool generation from schemas
- Category routing based on component naming
- Type safety between frontend and backend
- Dynamic component loading and rendering

## Key Files for Extension

- `packages/cli/src/utils/component-analyzer.ts` - Analyzes React components
- `packages/cli/src/utils/schema-generator.ts` - Generates JSON schemas
- `services/agent-service/app/agents/router_agent.py` - Category routing logic
- `services/agent-service/app/agents/dynamic_tool_generator.py` - Tool creation
- `apps/web/components/ui-components/component-renderer.tsx` - Component mapping
- `apps/web/lib/gennie-context.tsx` - SDK initialization and context