from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(description="User's natural language query")
    context: str = Field(default="", description="Optional context for the query")


class QueryResponse(BaseModel):
    answer: str = Field(description="Natural language response")
    component: dict = Field(description="Structured component data")
    reasoning: str = Field(description="Agent reasoning for component selection")
    success: bool = Field(description="Whether the query was processed successfully")
    error: str = Field(default="", description="Error message if any")