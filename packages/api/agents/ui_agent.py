from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Dict, Any, List, TypedDict, Annotated
import operator
import json
import re
from schemas.components import (
    WeatherCardSchema, 
    ChartCardSchema, 
    DataTableSchema, 
    InfoCardSchema,
    ChartType,
    ChartDataPoint,
    TableColumn,
    TableRow
)


class UIAgentState(TypedDict):
    messages: Annotated[List[Any], operator.add]
    query: str
    answer: str
    component: Dict[str, Any]
    reasoning: str




class WeatherCardTool(BaseTool):
    name: str = "create_weather_card"
    description: str = """Create a weather card component when the user asks about weather.
    
    Parameters:
    - location: city or location name (required)
    - temperature: temperature as a number (required)
    - condition: weather condition like 'Sunny', 'Cloudy', 'Rainy' (required)
    - humidity: humidity percentage as integer (optional)
    - wind_speed: wind speed as number (optional)
    - icon: weather icon like 'sunny', 'cloudy', 'rainy' (optional)
    
    Use this tool when the query and answer contain weather information."""
    
    def _parse_number(self, value, is_int=False):
        """Parse numeric values from strings with units"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return int(value) if is_int else float(value)
        
        # Extract numbers from strings like "20°C", "36%", "12 km/h"
        import re
        numbers = re.findall(r'-?\d+\.?\d*', str(value))
        if numbers:
            parsed = float(numbers[0])
            return int(parsed) if is_int else parsed
        return None
    
    def _run(self, location: str, temperature, condition: str, 
             humidity=None, wind_speed=None, icon: str = None) -> str:
        # Parse numeric values from potentially string inputs
        parsed_temp = self._parse_number(temperature)
        parsed_humidity = self._parse_number(humidity, is_int=True)
        parsed_wind = self._parse_number(wind_speed)
        
        schema = WeatherCardSchema(
            location=location,
            temperature=parsed_temp if parsed_temp is not None else 20.0,
            condition=condition,
            humidity=parsed_humidity,
            wind_speed=parsed_wind,
            icon=icon
        )
        return json.dumps(schema.model_dump())
    
    async def _arun(self, location: str, temperature, condition: str, 
                    humidity=None, wind_speed=None, icon: str = None) -> str:
        return self._run(location, temperature, condition, humidity, wind_speed, icon)


class ChartCardTool(BaseTool):
    name: str = "create_chart_card"
    description: str = """Create a chart component for data visualization.
    
    Parameters:
    - title: chart title (required)
    - chart_type: type of chart - 'bar', 'line', 'pie', or 'area' (required)
    - data: list of data points, each with 'label' and 'value' keys (required)
    - x_axis_label: label for x-axis (optional)
    - y_axis_label: label for y-axis (optional)
    
    Use this tool when the query asks for charts, graphs, or data visualization."""
    
    def _run(self, title: str, chart_type: str, data: List[dict], 
             x_axis_label: str = None, y_axis_label: str = None) -> str:
        chart_data = [ChartDataPoint(**point) for point in data]
        schema = ChartCardSchema(
            title=title,
            chart_type=ChartType(chart_type),
            data=chart_data,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label
        )
        return json.dumps(schema.model_dump())
    
    async def _arun(self, title: str, chart_type: str, data: List[dict], 
                    x_axis_label: str = None, y_axis_label: str = None) -> str:
        return self._run(title, chart_type, data, x_axis_label, y_axis_label)


class DataTableTool(BaseTool):
    name: str = "create_data_table"
    description: str = """Create a data table component for displaying tabular information.
    
    Parameters:
    - title: table title (required)
    - columns: list of column definitions with 'key' and 'label' (required)
    - rows: list of row data dictionaries (required)
    - searchable: whether table should be searchable (optional, default True)
    
    Use this tool when the query asks for tabular data, lists, or structured information."""
    
    def _run(self, title: str, columns: List[dict], rows: List[dict], 
             searchable: bool = True) -> str:
        table_columns = [TableColumn(**col) for col in columns]
        table_rows = [TableRow(data=row) for row in rows]
        schema = DataTableSchema(
            title=title,
            columns=table_columns,
            rows=table_rows,
            searchable=searchable
        )
        return json.dumps(schema.model_dump())
    
    async def _arun(self, title: str, columns: List[dict], rows: List[dict], 
                    searchable: bool = True) -> str:
        return self._run(title, columns, rows, searchable)


class InfoCardTool(BaseTool):
    name: str = "create_info_card"
    description: str = """Create an info card component for general information.
    
    Parameters:
    - title: card title (required)
    - content: main content or description (required)
    - icon: optional icon name like 'info', 'lightbulb', 'help' (optional)
    - variant: card style - 'default', 'success', 'warning', or 'error' (optional)
    
    Use this tool for general information, explanations, or when no specific component fits."""
    
    def _run(self, title: str, content: str, icon: str = None, 
             variant: str = "default") -> str:
        schema = InfoCardSchema(
            title=title,
            content=content,
            icon=icon,
            variant=variant
        )
        return json.dumps(schema.model_dump())
    
    async def _arun(self, title: str, content: str, icon: str = None, 
                    variant: str = "default") -> str:
        return self._run(title, content, icon, variant)


class UIAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        
        # Initialize UI component tools
        self.weather_tool = WeatherCardTool()
        self.chart_tool = ChartCardTool()
        self.table_tool = DataTableTool()
        self.info_tool = InfoCardTool()
        
        self.tools = [self.weather_tool, self.chart_tool, self.table_tool, self.info_tool]
        self.tool_node = ToolNode(self.tools)
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the LangGraph agent
        self.graph = self._build_graph()
        
        # Fallback for when no tool is used
        self.fallback_prompt = PromptTemplate(
            input_variables=["query", "answer"],
            template="""Based on this query and answer, provide a brief reasoning for why this response is appropriate:

Query: {query}
Answer: {answer}

Reasoning:"""
        )
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph agent workflow"""
        workflow = StateGraph(UIAgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("finalize", self._finalize_response)
        
        # Set the entrypoint
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": "finalize",
            },
        )
        
        # Add normal edge from tools to finalize
        workflow.add_edge("tools", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _call_model(self, state: UIAgentState) -> Dict[str, Any]:
        """Call the model with current state"""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: UIAgentState) -> str:
        """Determine if we should continue with tool calls or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        return "end"
    
    def _finalize_response(self, state: UIAgentState) -> Dict[str, Any]:
        """Process the final response and extract component data"""
        messages = state["messages"]
        query = state["query"]
        answer = state["answer"]
        
        # Look for tool results in messages
        for message in reversed(messages):
            if isinstance(message, ToolMessage):
                try:
                    component_data = json.loads(message.content)
                    reasoning = f"Selected {component_data.get('type', 'component')} based on query content"
                    return {
                        "component": component_data,
                        "reasoning": reasoning
                    }
                except json.JSONDecodeError:
                    continue
        
        # Fallback if no tool was used - create info card
        fallback_component = self.info_tool._run(
            title="Information",
            content=answer,
            variant="default"
        )
        
        reasoning_response = self.llm.invoke(
            self.fallback_prompt.format(query=query, answer=answer)
        )
        
        return {
            "component": json.loads(fallback_component),
            "reasoning": reasoning_response.content.strip()
        }
    
    def select_component(self, query: str, answer: str) -> Dict[str, Any]:
        """Select and create appropriate UI component"""
        system_message = """You are a UI Component Agent. Your job is to select the most appropriate UI component for the given query and answer.

Available tools:
- create_weather_card: For weather information
- create_chart_card: For data that can be visualized as charts
- create_data_table: For tabular/structured data
- create_info_card: For general information

Analyze the query and answer, then use the most appropriate tool to create the UI component.
If the content is about weather, use create_weather_card.
If the content can be visualized as data, use create_chart_card.
If the content is structured/tabular, use create_data_table.
For general information, use create_info_card."""
        
        initial_state = {
            "messages": [
                HumanMessage(content=f"System: {system_message}\n\nUser Query: {query}\nGenerated Answer: {answer}\n\nPlease select and create the appropriate UI component.")
            ],
            "query": query,
            "answer": answer,
            "component": {},
            "reasoning": ""
        }
        
        result = self.graph.invoke(initial_state)
        return {
            "component": result.get("component", {}),
            "reasoning": result.get("reasoning", "")
        }
    
    async def aselect_component(self, query: str, answer: str) -> Dict[str, Any]:
        """Async version of select_component"""
        system_message = """You are a UI Component Agent. Your job is to select the most appropriate UI component for the given query and answer.

Available tools:
- create_weather_card: For weather information
- create_chart_card: For data that can be visualized as charts
- create_data_table: For tabular/structured data
- create_info_card: For general information

Analyze the query and answer, then use the most appropriate tool to create the UI component.
If the content is about weather, use create_weather_card.
If the content can be visualized as data, use create_chart_card.
If the content is structured/tabular, use create_data_table.
For general information, use create_info_card."""
        
        initial_state = {
            "messages": [
                HumanMessage(content=f"System: {system_message}\n\nUser Query: {query}\nGenerated Answer: {answer}\n\nPlease select and create the appropriate UI component.")
            ],
            "query": query,
            "answer": answer,
            "component": {},
            "reasoning": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        return {
            "component": result.get("component", {}),
            "reasoning": result.get("reasoning", "")
        }