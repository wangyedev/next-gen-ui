from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional
import json

from schemas.components import ComponentSchema


class RouterAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.categories = {
            "data_display": {
                "description": "Components for displaying data in tables, lists, cards, etc.",
                "keywords": ["table", "list", "display", "show", "view", "data", "information", "users", "records", "items"]
            },
            "data_visualization": {
                "description": "Components for charts, graphs, and visual data representation",
                "keywords": ["chart", "graph", "visualization", "plot", "bar", "line", "pie", "statistics", "analytics", "metrics"]
            },
            "content": {
                "description": "Components for general content display, information cards, text",
                "keywords": ["info", "content", "text", "description", "explanation", "about", "details", "summary"]
            },
            "general": {
                "description": "General purpose components that don't fit other categories",
                "keywords": ["general", "misc", "other", "custom", "generic"]
            }
        }

    def route_query(self, query: str, answer: str, available_schemas: List[Dict[str, Any]]) -> str:
        """
        Analyze the query and answer to determine the best component category.
        Returns the category name that should handle this request.
        """
        try:
            # First, try rule-based routing for common patterns
            category = self._rule_based_routing(query, answer)
            if category:
                return category

            # Fallback to LLM-based routing for complex cases
            return self._llm_based_routing(query, answer, available_schemas)
        
        except Exception as e:
            print(f"Router error: {e}")
            # Default fallback
            return "content"

    def _rule_based_routing(self, query: str, answer: str) -> Optional[str]:
        """
        Use simple keyword matching to route common queries quickly.
        """
        combined_text = f"{query} {answer}".lower()
        
        # Weather queries are always data_display
        if any(word in combined_text for word in ["weather", "temperature", "humidity", "wind"]):
            return "data_display"
        
        # Chart/visualization keywords
        chart_keywords = ["chart", "graph", "plot", "visualization", "bar", "line", "pie", "statistics"]
        if any(word in combined_text for word in chart_keywords):
            return "data_visualization"
        
        # Table/data display keywords
        table_keywords = ["table", "list", "display", "show", "data", "users", "records", "rows", "columns"]
        if any(word in combined_text for word in table_keywords):
            return "data_display"
        
        # Information/content keywords
        info_keywords = ["explain", "information", "about", "description", "what is", "tell me"]
        if any(word in combined_text for word in info_keywords):
            return "content"
        
        return None

    def _llm_based_routing(self, query: str, answer: str, available_schemas: List[Dict[str, Any]]) -> str:
        """
        Use LLM to determine the best category when rule-based routing fails.
        """
        # Get available categories from schemas
        schema_categories = set()
        for schema in available_schemas:
            if "category" in schema:
                schema_categories.add(schema["category"])
        
        # Use predefined categories as fallback
        categories_info = []
        for cat, info in self.categories.items():
            if cat in schema_categories or len(schema_categories) == 0:
                categories_info.append(f"- {cat}: {info['description']}")
        
        prompt = f"""
You are a component category router. Your job is to analyze a user query and corresponding answer, then select the most appropriate UI component category.

Available categories:
{chr(10).join(categories_info)}

User Query: "{query}"
Generated Answer: "{answer}"

Based on the query and answer, which category would be most appropriate for rendering this response?

Respond with ONLY the category name (e.g., "data_visualization", "data_display", "content", or "general").
"""

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            # Extract category from response
            category = response.content.strip().lower()
            
            # Validate that it's a known category
            if category in self.categories:
                return category
            
            # Try to find partial match
            for cat in self.categories.keys():
                if cat in category or category in cat:
                    return cat
                    
        except Exception as e:
            print(f"LLM routing error: {e}")
        
        # Ultimate fallback
        return "content"

    def get_category_schemas(self, category: str, all_schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter schemas by category for the UI Agent.
        """
        return [
            schema for schema in all_schemas 
            if schema.get("category", "general") == category
        ]

    def get_routing_explanation(self, query: str, selected_category: str) -> str:
        """
        Generate an explanation for why a particular category was selected.
        """
        category_info = self.categories.get(selected_category, {})
        description = category_info.get("description", "Unknown category")
        
        return f"Routed to '{selected_category}' category: {description}"