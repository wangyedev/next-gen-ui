# Multi-Agent API

A LangGraph-based multi-agent system that processes natural language queries and selects appropriate UI components for rendering.

## Features

- **Answer Agent**: Generates natural language responses with mock weather tool
- **Weather Tool Integration**: Simulated weather data for demonstration purposes
- **UI Agent**: Selects and structures data for appropriate UI components
- **Component Support**: Weather cards, charts, data tables, and info cards
- **FastAPI Backend**: RESTful API with WebSocket support
- **Real-time Communication**: WebSocket endpoints for streaming responses

## Setup

1. **Environment Setup**:
   ```bash
   cd packages/api
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

2. **Install Dependencies**:
   ```bash
   uv add fastapi uvicorn pydantic langchain langgraph langchain-google-genai python-multipart websockets httpx
   uv add --dev pytest pytest-asyncio black isort mypy
   ```

3. **Run the API**:
   ```bash
   uv run python main.py
   ```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/query` - Process a query and return structured response
- `WebSocket /ws/query` - Real-time query processing

## Architecture

### Agents

1. **Answer Agent** (`agents/answer_agent.py`)
   - Uses Google's Gemini 2.5 Flash model
   - Generates natural language responses with mock weather tool
   - Automatically generates simulated weather data for weather queries
   - Handles context and query understanding

2. **UI Agent** (`agents/ui_agent.py`)
   - Analyzes queries and answers
   - Selects appropriate UI components
   - Structures data according to component schemas

### Schemas

Component schemas are defined in `schemas/components.py`:

- `WeatherCardSchema` - Weather information display
- `ChartCardSchema` - Data visualization (bar, line, pie, area)
- `DataTableSchema` - Tabular data with sorting/searching
- `InfoCardSchema` - General information cards

### Workflow

1. User submits query
2. Answer Agent generates natural language response
3. UI Agent analyzes query/answer and selects component
4. Structured data is returned to frontend
5. Frontend renders the appropriate component

## Example Queries

### Weather Queries (Uses Mock Weather Tool)
- "What's the weather in Paris today?"
- "How's the temperature in Tokyo?"
- "Is it going to rain in London?"

### Data Visualization Queries  
- "Show me sales data for Q1"
- "Create a chart of monthly revenue"
- "Display user information in a table"

### General Information
- "Explain machine learning concepts"
- "How does photosynthesis work?"