from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from typing import Dict, Any, List, Optional
import json
import re
from schemas.components import (
    ComponentSchema, 
    WeatherCardSchema, 
    ChartCardSchema, 
    DataTableSchema, 
    InfoCardSchema,
    ComponentType,
    ChartType,
    ChartDataPoint,
    TableColumn,
    TableRow
)


class UIComponentTool(BaseTool):
    name: str
    description: str
    component_type: ComponentType
    
    def _run(self, **kwargs) -> dict:
        return self._create_component(**kwargs)
    
    async def _arun(self, **kwargs) -> dict:
        return self._create_component(**kwargs)
    
    def _create_component(self, **kwargs) -> dict:
        raise NotImplementedError


class WeatherCardTool(UIComponentTool):
    name: str = "create_weather_card"
    description: str = "Create a weather card component for displaying weather information"
    component_type: ComponentType = ComponentType.WEATHER_CARD
    
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
    
    def _create_component(self, location: str, temperature, condition: str, 
                         humidity=None, wind_speed=None, icon: str = None) -> dict:
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
        return schema.model_dump()


class ChartCardTool(UIComponentTool):
    name: str = "create_chart_card"
    description: str = "Create a chart card component for displaying data visualizations"
    component_type: ComponentType = ComponentType.CHART_CARD
    
    def _create_component(self, title: str, chart_type: str, data: List[dict], 
                         x_axis_label: str = None, y_axis_label: str = None) -> dict:
        chart_data = [ChartDataPoint(**point) for point in data]
        schema = ChartCardSchema(
            title=title,
            chart_type=ChartType(chart_type),
            data=chart_data,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label
        )
        return schema.model_dump()


class DataTableTool(UIComponentTool):
    name: str = "create_data_table"
    description: str = "Create a data table component for displaying tabular data"
    component_type: ComponentType = ComponentType.DATA_TABLE
    
    def _create_component(self, title: str, columns: List[dict], rows: List[dict], 
                         searchable: bool = True) -> dict:
        table_columns = [TableColumn(**col) for col in columns]
        table_rows = [TableRow(data=row) for row in rows]
        schema = DataTableSchema(
            title=title,
            columns=table_columns,
            rows=table_rows,
            searchable=searchable
        )
        return schema.model_dump()


class InfoCardTool(UIComponentTool):
    name: str = "create_info_card"
    description: str = "Create an info card component for displaying general information"
    component_type: ComponentType = ComponentType.INFO_CARD
    
    def _create_component(self, title: str, content: str, icon: str = None, 
                         variant: str = "default") -> dict:
        schema = InfoCardSchema(
            title=title,
            content=content,
            icon=icon,
            variant=variant
        )
        return schema.model_dump()


class UIComponentParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"component": None, "reasoning": text}
        except json.JSONDecodeError:
            return {"component": None, "reasoning": text}


class UIAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.parser = UIComponentParser()
        self.tools = {
            "weather_card": WeatherCardTool(),
            "chart_card": ChartCardTool(),
            "data_table": DataTableTool(),
            "info_card": InfoCardTool(),
        }
        
        self.prompt = PromptTemplate(
            input_variables=["answer", "query"],
            template="""You are a UI Component Agent responsible for selecting and structuring data for appropriate UI components based on user queries and answers.

User Query: {query}
Generated Answer: {answer}

Available Components:
1. WeatherCard - For weather-related information (location, temperature, condition, humidity, wind_speed, icon)
2. ChartCard - For data visualization (title, chart_type: bar/line/pie/area, data points with label/value, axis labels)
3. DataTable - For tabular data (title, columns with key/label, rows with data, searchable)
4. InfoCard - For general information (title, content, icon, variant: default/success/warning/error)

Analyze the query and answer to determine the most appropriate component. Extract and structure the relevant data according to the component's schema.

Guidelines:
- Use WeatherCard for weather queries
  * temperature: provide as a number (e.g., 20.5, not "20°C")
  * humidity: provide as an integer percentage (e.g., 65, not "65%")
  * wind_speed: provide as a number (e.g., 12.5, not "12 km/h")
  * condition: text description (e.g., "Sunny", "Cloudy", "Rainy")
  * icon: simple keyword (e.g., "sunny", "cloudy", "rainy")
- Use ChartCard for data that can be visualized (numbers, comparisons, trends)
- Use DataTable for structured data with multiple rows/columns
- Use InfoCard for general information, definitions, or simple facts

Respond with a JSON object containing:
{{
  "component_type": "weather_card|chart_card|data_table|info_card",
  "component_data": {{
    // Component-specific data according to schema
  }},
  "reasoning": "Brief explanation of why this component was selected"
}}

If no specific component is appropriate, respond with:
{{
  "component_type": "info_card",
  "component_data": {{
    "title": "Information",
    "content": "{answer}",
    "variant": "default"
  }},
  "reasoning": "General information response"
}}

Response:"""
        )
    
    def select_component(self, query: str, answer: str) -> Dict[str, Any]:
        formatted_prompt = self.prompt.format(query=query, answer=answer)
        response = self.llm.invoke(formatted_prompt)
        result = self.parser.parse(response.content)
        
        if "component_type" in result and "component_data" in result:
            component_type = result["component_type"]
            component_data = result["component_data"]
            
            if component_type in self.tools:
                tool = self.tools[component_type]
                try:
                    component = tool._create_component(**component_data)
                    return {
                        "component": component,
                        "reasoning": result.get("reasoning", "")
                    }
                except Exception as e:
                    return self._fallback_info_card(answer, f"Error creating component: {str(e)}")
        
        return self._fallback_info_card(answer, "Could not determine appropriate component")
    
    def _fallback_info_card(self, answer: str, reasoning: str) -> Dict[str, Any]:
        fallback_tool = self.tools["info_card"]
        component = fallback_tool._create_component(
            title="Information",
            content=answer,
            variant="default"
        )
        return {
            "component": component,
            "reasoning": reasoning
        }
    
    async def aselect_component(self, query: str, answer: str) -> Dict[str, Any]:
        formatted_prompt = self.prompt.format(query=query, answer=answer)
        response = await self.llm.ainvoke(formatted_prompt)
        result = self.parser.parse(response.content)
        
        if "component_type" in result and "component_data" in result:
            component_type = result["component_type"]
            component_data = result["component_data"]
            
            if component_type in self.tools:
                tool = self.tools[component_type]
                try:
                    component = tool._create_component(**component_data)
                    return {
                        "component": component,
                        "reasoning": result.get("reasoning", "")
                    }
                except Exception as e:
                    return self._fallback_info_card(answer, f"Error creating component: {str(e)}")
        
        return self._fallback_info_card(answer, "Could not determine appropriate component")