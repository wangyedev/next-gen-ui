from langchain.schema import HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List
import json

from .dynamic_tool_generator import DynamicToolGenerator


class DynamicUIAgent:
    """
    UI Agent that uses dynamically generated tools from schemas.
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools = []
        self.agent_executor = None

    def initialize_tools(self, schemas: List[Dict[str, Any]]):
        """
        Initialize the agent with tools generated from schemas.
        """
        self.tools = DynamicToolGenerator.create_tools_from_schemas(schemas)
        self._create_agent()

    def _create_agent(self):
        """
        Create the tool-calling agent with dynamic tools.
        """
        if not self.tools:
            # Create fallback tool if no schemas provided
            self.tools = [self._create_fallback_tool()]

        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=3
        )

    def _get_system_prompt(self) -> str:
        """
        Generate system prompt based on available tools.
        """
        tool_descriptions = []
        for tool in self.tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")

        available_tools = "\\n".join(tool_descriptions)

        return f"""You are a UI Component Selection Agent. Your job is to analyze a user query and corresponding answer, then select the most appropriate UI component to render the response.

Available UI Components:
{available_tools}

Instructions:
1. Analyze the user query and the generated answer
2. Select the most appropriate component based on the content type and structure
3. Extract relevant data from the answer to populate the component
4. Use the component's tool with appropriate parameters
5. Provide reasoning for your component selection

Guidelines:
- For weather information: Use weather-related components
- For data visualization needs: Use chart components  
- For tabular data: Use table components
- For general information: Use info card components
- Extract specific values (numbers, dates, lists) from the answer text
- Make reasonable assumptions for missing optional parameters
- Ensure all required parameters are provided

Always call exactly one tool to create the appropriate component."""

    def _create_fallback_tool(self):
        """
        Create a fallback info card tool when no schemas are available.
        """
        from langchain.tools import Tool

        def fallback_info_card(title: str, content: str, **kwargs) -> str:
            return json.dumps({
                "component": {
                    "type": "info_card",
                    "title": title,
                    "content": content,
                    "variant": "default"
                },
                "reasoning": "Used fallback info card component"
            })

        return Tool(
            name="create_info_card",
            description="Create an information card component for general content",
            func=fallback_info_card
        )

    def select_component(self, query: str, answer: str) -> Dict[str, Any]:
        """
        Select and configure the most appropriate UI component.
        """
        try:
            if not self.agent_executor:
                return self._fallback_info_card(answer, "Agent not initialized")

            # Prepare input for the agent
            input_text = f"""
User Query: "{query}"

Generated Answer: "{answer}"

Please select the most appropriate UI component and configure it with the relevant data from the answer.
"""

            # Execute the agent
            result = self.agent_executor.invoke({"input": input_text})
            
            # Parse the result
            if result and "output" in result:
                try:
                    # Try to parse JSON response
                    response_data = json.loads(result["output"])
                    return {
                        "component": response_data.get("component", {}),
                        "reasoning": response_data.get("reasoning", "Component selected by agent")
                    }
                except json.JSONDecodeError:
                    # If not JSON, treat as reasoning text
                    return self._fallback_info_card(answer, result["output"])
            
            return self._fallback_info_card(answer, "No component selected")

        except Exception as e:
            print(f"Dynamic UI Agent error: {e}")
            return self._fallback_info_card(answer, f"Error in component selection: {str(e)}")

    def _fallback_info_card(self, content: str, reasoning: str = "Fallback component") -> Dict[str, Any]:
        """
        Create a fallback info card component.
        """
        return {
            "component": {
                "type": "info_card",
                "title": "Response",
                "content": content,
                "variant": "default"
            },
            "reasoning": reasoning
        }

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        """
        return [tool.name for tool in self.tools]

    def get_tool_count(self) -> int:
        """
        Get the number of available tools.
        """
        return len(self.tools)