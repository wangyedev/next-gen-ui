from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel
import os
from langchain_google_genai import ChatGoogleGenerativeAI

from .answer_agent import AnswerAgent
from .ui_agent import UIAgent
from schemas.components import AgentResponse


class GraphState(TypedDict):
    query: str
    context: str
    answer: str
    component: Optional[Dict[str, Any]]
    reasoning: str
    messages: List[BaseMessage]
    error: Optional[str]


class MultiAgentGraph:
    def __init__(self, google_api_key: Optional[str] = None):
        if not google_api_key:
            google_api_key = os.getenv("GOOGLE_API_KEY")

        if not google_api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable."
            )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", temperature=0.7, google_api_key=google_api_key
        )

        self.answer_agent = AnswerAgent(self.llm)
        self.ui_agent = UIAgent(self.llm)

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(GraphState)

        workflow.add_node("answer_agent", self._answer_node)
        workflow.add_node("ui_agent", self._ui_node)
        workflow.add_node("finalize", self._finalize_node)

        workflow.set_entry_point("answer_agent")

        workflow.add_edge("answer_agent", "ui_agent")
        workflow.add_edge("ui_agent", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _answer_node(self, state: GraphState) -> GraphState:
        try:
            query = state["query"]
            context = state.get("context", "")

            answer = self.answer_agent.generate_answer(query, context)

            state["answer"] = answer
            state["messages"].append(HumanMessage(content=query))
            state["messages"].append(AIMessage(content=answer))

        except Exception as e:
            state["error"] = f"Answer Agent Error: {str(e)}"
            state["answer"] = (
                "I apologize, but I encountered an error while processing your query."
            )

        return state

    def _ui_node(self, state: GraphState) -> GraphState:
        try:
            query = state["query"]
            answer = state["answer"]

            if state.get("error"):
                ui_result = self.ui_agent._fallback_info_card(
                    answer, "Error occurred in previous step"
                )
            else:
                ui_result = self.ui_agent.select_component(query, answer)

            state["component"] = ui_result["component"]
            state["reasoning"] = ui_result["reasoning"]

        except Exception as e:
            state["error"] = f"UI Agent Error: {str(e)}"
            fallback_result = self.ui_agent._fallback_info_card(
                state["answer"], f"UI selection failed: {str(e)}"
            )
            state["component"] = fallback_result["component"]
            state["reasoning"] = fallback_result["reasoning"]

        return state

    def _finalize_node(self, state: GraphState) -> GraphState:
        return state

    def process_query(self, query: str, context: str = "") -> AgentResponse:
        initial_state = GraphState(
            query=query,
            context=context,
            answer="",
            component=None,
            reasoning="",
            messages=[],
            error=None,
        )

        result = self.graph.invoke(initial_state)

        return AgentResponse(
            answer=result["answer"],
            component=result["component"],
            reasoning=result.get("reasoning", ""),
        )

    async def aprocess_query(self, query: str, context: str = "") -> AgentResponse:
        initial_state = GraphState(
            query=query,
            context=context,
            answer="",
            component=None,
            reasoning="",
            messages=[],
            error=None,
        )

        result = await self.graph.ainvoke(initial_state)

        return AgentResponse(
            answer=result["answer"],
            component=result["component"],
            reasoning=result.get("reasoning", ""),
        )
