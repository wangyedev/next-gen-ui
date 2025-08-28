from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from enum import Enum


class ComponentType(str, Enum):
    WEATHER_CARD = "weather_card"
    CHART_CARD = "chart_card"
    DATA_TABLE = "data_table"
    INFO_CARD = "info_card"


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"


class WeatherCardSchema(BaseModel):
    type: Literal[ComponentType.WEATHER_CARD] = ComponentType.WEATHER_CARD
    location: str = Field(description="Location name (e.g., 'Paris, France')")
    temperature: float = Field(description="Current temperature in Celsius")
    condition: str = Field(description="Weather condition (e.g., 'Sunny', 'Cloudy')")
    humidity: Optional[int] = Field(None, description="Humidity percentage")
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")
    icon: Optional[str] = Field(None, description="Weather icon identifier")


class ChartDataPoint(BaseModel):
    label: str = Field(description="Data point label")
    value: Union[int, float] = Field(description="Data point value")
    color: Optional[str] = Field(None, description="Optional color for this data point")


class ChartCardSchema(BaseModel):
    type: Literal[ComponentType.CHART_CARD] = ComponentType.CHART_CARD
    title: str = Field(description="Chart title")
    chart_type: ChartType = Field(description="Type of chart to render")
    data: List[ChartDataPoint] = Field(description="Chart data points")
    x_axis_label: Optional[str] = Field(None, description="X-axis label")
    y_axis_label: Optional[str] = Field(None, description="Y-axis label")


class TableColumn(BaseModel):
    key: str = Field(description="Column identifier")
    label: str = Field(description="Column display name")
    sortable: bool = Field(default=True, description="Whether column is sortable")


class TableRow(BaseModel):
    data: dict = Field(description="Row data as key-value pairs")


class DataTableSchema(BaseModel):
    type: Literal[ComponentType.DATA_TABLE] = ComponentType.DATA_TABLE
    title: str = Field(description="Table title")
    columns: List[TableColumn] = Field(description="Table columns definition")
    rows: List[TableRow] = Field(description="Table rows data")
    searchable: bool = Field(default=True, description="Whether table is searchable")


class InfoCardSchema(BaseModel):
    type: Literal[ComponentType.INFO_CARD] = ComponentType.INFO_CARD
    title: str = Field(description="Card title")
    content: str = Field(description="Card content/description")
    icon: Optional[str] = Field(None, description="Optional icon identifier")
    variant: Optional[Literal["default", "success", "warning", "error"]] = Field(
        "default", description="Card variant for styling"
    )


ComponentSchema = Union[WeatherCardSchema, ChartCardSchema, DataTableSchema, InfoCardSchema]


class AgentResponse(BaseModel):
    answer: str = Field(description="Natural language answer from the Answer Agent")
    component: Optional[ComponentSchema] = Field(
        None, description="Selected UI component with structured data"
    )
    reasoning: Optional[str] = Field(
        None, description="UI Agent's reasoning for component selection"
    )