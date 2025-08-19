from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Dict, Any, List, TypedDict, Annotated
import operator
import re
import random
import json


class AnswerOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text.strip()


class AgentState(TypedDict):
    messages: Annotated[List[Any], operator.add]
    query: str
    final_answer: str


class MockWeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get current weather information for any city"
    
    def _run(self, city: str) -> str:
        """Generate mock weather data for a city"""
        conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear", "Overcast"]
        icons = ["sunny", "cloudy", "cloudy", "rainy", "sunny", "cloudy"]
        
        condition = random.choice(conditions)
        icon = icons[conditions.index(condition)]
        temperature = random.randint(-5, 35)
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 25)
        
        weather_data = {
            "location": city,
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "icon": icon
        }
        
        return f"Current weather in {city}: {temperature}°C, {condition}. Humidity: {humidity}%, Wind: {wind_speed} km/h"
    
    async def _arun(self, city: str) -> str:
        return self._run(city)


class AnswerAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.parser = AnswerOutputParser()
        
        # Initialize mock weather tool
        self.weather_tool = MockWeatherTool()
        self.tools = [self.weather_tool]
        self.tool_node = ToolNode(self.tools)
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the LangGraph agent
        self.graph = self._build_graph()
        
        # Fallback prompt for direct responses
        self.fallback_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""You are a helpful assistant that provides clear, informative answers to user questions.

User Query: {query}
Context: {context}

Please provide a comprehensive answer to the user's question. Be factual, helpful, and concise.
If the query is about weather, include relevant details like temperature, conditions, etc.
If the query is about data analysis, explain trends and insights.
If the query is general information, provide accurate and useful details.

Answer:"""
        )
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self.tool_node)
        
        # Set the entrypoint
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        
        # Add normal edge from tools to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _call_model(self, state: AgentState) -> Dict[str, Any]:
        """Call the model with current state"""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue with tool calls or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        return "end"
    
    def _should_use_weather_tool(self, query: str) -> bool:
        """Determine if a query requires weather information"""
        weather_indicators = ["weather", "temperature", "forecast", "climate", "rain", "snow", "sunny", "cloudy"]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in weather_indicators)
    
    def generate_answer(self, query: str, context: str = "") -> str:
        try:
            # Check if weather information is needed
            if self._should_use_weather_tool(query):
                # Use LangGraph agent with weather tool
                system_message = """You are a helpful assistant that can get weather information for any city.

When a user asks about weather, use the get_weather tool to get current weather data.
After getting weather information, provide a comprehensive and friendly response."""
                
                initial_state = {
                    "messages": [
                        HumanMessage(content=f"System: {system_message}\n\nUser Query: {query}")
                    ],
                    "query": query,
                    "final_answer": ""
                }
                
                result = self.graph.invoke(initial_state)
                final_message = result["messages"][-1]
                
                if hasattr(final_message, 'content') and final_message.content:
                    return self.parser.parse(final_message.content)
            
            # Direct LLM response for general queries
            formatted_prompt = self.fallback_prompt.format(query=query, context=context)
            response = self.llm.invoke(formatted_prompt)
            return self.parser.parse(response.content)
            
        except Exception:
            # If anything fails, use fallback prompt
            formatted_prompt = self.fallback_prompt.format(query=query, context=context)
            response = self.llm.invoke(formatted_prompt)
            return self.parser.parse(response.content)
    
    async def agenerate_answer(self, query: str, context: str = "") -> str:
        try:
            # Check if weather information is needed
            if self._should_use_weather_tool(query):
                # Use LangGraph agent with weather tool
                system_message = """You are a helpful assistant that can get weather information for any city.

When a user asks about weather, use the get_weather tool to get current weather data.
After getting weather information, provide a comprehensive and friendly response."""
                
                initial_state = {
                    "messages": [
                        HumanMessage(content=f"System: {system_message}\n\nUser Query: {query}")
                    ],
                    "query": query,
                    "final_answer": ""
                }
                
                result = await self.graph.ainvoke(initial_state)
                final_message = result["messages"][-1]
                
                if hasattr(final_message, 'content') and final_message.content:
                    return self.parser.parse(final_message.content)
            
            # Direct LLM response for general queries
            formatted_prompt = self.fallback_prompt.format(query=query, context=context)
            response = await self.llm.ainvoke(formatted_prompt)
            return self.parser.parse(response.content)
            
        except Exception:
            # If anything fails, use fallback prompt
            formatted_prompt = self.fallback_prompt.format(query=query, context=context)
            response = await self.llm.ainvoke(formatted_prompt)
            return self.parser.parse(response.content)