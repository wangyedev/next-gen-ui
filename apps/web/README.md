# Multi-Agent UI Frontend

A Next.js frontend for the multi-agent system that renders dynamic UI components based on LangGraph agent decisions.

## Features

- **Dynamic Component Rendering**: Renders components based on agent selection
- **Chat Interface**: Real-time query interface with streaming responses
- **shadcn/ui Components**: Beautiful, accessible UI components
- **TypeScript**: Full type safety with component schemas
- **Real-time Communication**: HTTP and WebSocket support

## Components

### UI Components

1. **WeatherCard**: Displays weather information with icons and metrics
2. **ChartCard**: Renders various chart types (bar, line, pie, area)
3. **DataTable**: Sortable, searchable data tables
4. **InfoCard**: General information cards with variants

### Core Features

- **ComponentRenderer**: Dynamic component selection and rendering
- **QueryInterface**: Chat-like interface for user interactions
- **API Client**: HTTP client for backend communication
- **WebSocket Client**: Real-time streaming support

## Setup

1. **Environment Setup**:
   ```bash
   cd packages/web
   cp .env.local.example .env.local
   # Edit .env.local if needed (API URL)
   ```

2. **Install Dependencies**:
   ```bash
   pnpm install
   ```

3. **Run Development Server**:
   ```bash
   pnpm dev
   ```

4. **Open Browser**:
   Visit [http://localhost:3000](http://localhost:3000)

## Architecture

### Component System

- **TypeScript Types**: Shared component schemas (`lib/types.ts`)
- **UI Components**: Individual component implementations
- **Component Renderer**: Dynamic component selection logic
- **API Integration**: Communication with multi-agent backend

### Query Flow

1. User enters query in chat interface
2. Frontend sends request to backend API
3. Backend processes with LangGraph agents
4. Structured response received with component data
5. ComponentRenderer selects and renders appropriate component
6. User sees natural language answer + visual component

## Example Usage

### Weather Query
```
User: "What's the weather in Paris?"
→ WeatherCard component with temperature, conditions, etc.
```

### Data Visualization
```
User: "Show me sales data as a chart"
→ ChartCard component with bar/line chart
```

### Tabular Data
```
User: "Display user data in a table"
→ DataTable component with sorting/filtering
```

### General Information
```
User: "Explain machine learning"
→ InfoCard component with formatted content
```

## Development

### Adding New Components

1. Create component schema in `lib/types.ts`
2. Implement component in `components/ui-components/`
3. Add to `ComponentRenderer` switch statement
4. Update backend schemas to match

### Styling

Uses Tailwind CSS with shadcn/ui components for consistent design system.
