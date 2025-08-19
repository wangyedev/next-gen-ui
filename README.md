# Next-Gen UI: Multi-Agent System with LangGraph

A sophisticated multi-agent system built with LangGraph that enables LLMs to select and render appropriate UI components based on natural language queries.

## 🎯 Project Goal

Create an intelligent system where:
1. **LLM generates natural language answers** to user queries
2. **Multi-agent system selects appropriate UI components** based on content
3. **Structured data is produced** according to component schemas
4. **Dynamic UI rendering** happens on the client with beautiful components

## 🏗️ Architecture

### Backend (Python + LangGraph)
- **Answer Agent**: Generates comprehensive answers using OpenAI's GPT models
- **UI Agent**: Analyzes queries/answers and selects optimal UI components
- **FastAPI**: RESTful API with WebSocket support for real-time communication
- **Component Schemas**: Pydantic models defining UI component structures

### Frontend (Next.js + shadcn/ui)
- **Dynamic Component System**: Renders components based on agent decisions
- **Chat Interface**: Beautiful, real-time query interface
- **TypeScript**: Full type safety with shared schemas
- **shadcn/ui**: Consistent, accessible design system

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** with uv package manager
- **Node.js 18+** with pnpm
- **Google API Key** for Gemini

### 1. Clone and Setup
```bash
git clone <repository>
cd next-gen-ui
```

### 2. Backend Setup
```bash
cd packages/api
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
uv add fastapi uvicorn pydantic langchain langgraph langchain-google-genai python-multipart websockets httpx
uv run python main.py
```

### 3. Frontend Setup
```bash
cd packages/web
cp .env.local.example .env.local
pnpm install
pnpm dev
```

### 4. Open Application
Visit [http://localhost:3000](http://localhost:3000)

## 💡 Example Workflows

### Weather Query
```
User: "What's the weather in Paris?"
→ Answer Agent: Generates weather description
→ UI Agent: Selects WeatherCard component
→ Frontend: Renders weather card with temperature, conditions, humidity, wind
```

### Data Visualization
```
User: "Show me Q1 sales data as a chart"
→ Answer Agent: Provides sales analysis
→ UI Agent: Selects ChartCard with bar chart type
→ Frontend: Renders interactive bar chart
```

### Tabular Data
```
User: "Display user information in a table"
→ Answer Agent: Describes user data structure
→ UI Agent: Selects DataTable component
→ Frontend: Renders sortable, searchable data table
```

### General Information
```
User: "Explain machine learning"
→ Answer Agent: Provides comprehensive explanation
→ UI Agent: Selects InfoCard component
→ Frontend: Renders formatted information card
```

## 🎨 Available Components

### WeatherCard
- **Purpose**: Weather information display
- **Features**: Temperature, conditions, humidity, wind speed, weather icons
- **Schema**: Location, temperature, condition, optional metrics

### ChartCard
- **Purpose**: Data visualization
- **Types**: Bar, line, pie, area charts
- **Features**: Interactive charts with labels, colors, axis customization
- **Schema**: Title, chart type, data points, axis labels

### DataTable
- **Purpose**: Tabular data display
- **Features**: Sorting, searching, pagination-ready
- **Schema**: Columns definition, rows data, searchable flag

### InfoCard
- **Purpose**: General information display
- **Variants**: Default, success, warning, error
- **Features**: Icons, formatted content, status indicators
- **Schema**: Title, content, icon, variant

## 🔧 Development

### Adding New Components

1. **Backend**: Define schema in `packages/api/schemas/components.py`
2. **Backend**: Create tool in `packages/api/agents/ui_agent.py`
3. **Frontend**: Add TypeScript interface in `packages/web/lib/types.ts`
4. **Frontend**: Implement component in `packages/web/components/ui-components/`
5. **Frontend**: Update `ComponentRenderer` to handle new type

### Project Structure
```
next-gen-ui/
├── packages/
│   ├── api/                    # Python backend
│   │   ├── agents/            # LangGraph agents
│   │   ├── schemas/           # Pydantic schemas
│   │   └── main.py           # FastAPI application
│   └── web/                   # Next.js frontend
│       ├── components/        # React components
│       ├── lib/              # Utilities and types
│       └── app/              # Next.js app router
├── pnpm-workspace.yaml       # Monorepo configuration
└── README.md                 # This file
```

## 🛠️ Technology Stack

### Backend
- **LangGraph**: Multi-agent orchestration
- **LangChain**: LLM integration and tools
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Google Gemini**: Gemini 2.5 Flash for natural language processing
- **uv**: Fast Python package manager

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **shadcn/ui**: Component library built on Radix UI
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **pnpm**: Fast, efficient package manager

## 📋 Features

### Multi-Agent System
- ✅ **Answer Agent** with natural language generation
- ✅ **UI Agent** with component selection logic
- ✅ **LangGraph workflow** orchestration
- ✅ **Error handling** and fallback mechanisms

### API & Communication
- ✅ **RESTful endpoints** for query processing
- ✅ **WebSocket support** for real-time communication
- ✅ **CORS configuration** for frontend integration
- ✅ **Health checks** and monitoring

### Frontend Interface
- ✅ **Chat-like interface** with message history
- ✅ **Dynamic component rendering** based on agent decisions
- ✅ **Real-time updates** with loading states
- ✅ **Error handling** with user-friendly messages
- ✅ **Responsive design** for all screen sizes

### Component System
- ✅ **Type-safe schemas** shared between backend and frontend
- ✅ **Extensible architecture** for adding new components
- ✅ **Consistent styling** with shadcn/ui design system
- ✅ **Interactive features** (sorting, searching, etc.)

## 🎯 Use Cases

- **Dashboard Generation**: Convert natural language requests into data visualizations
- **Report Creation**: Generate formatted reports with mixed content types
- **Data Exploration**: Interactive exploration of datasets through conversation
- **Content Management**: Dynamic content presentation based on user queries
- **Business Intelligence**: Natural language interface for business metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details