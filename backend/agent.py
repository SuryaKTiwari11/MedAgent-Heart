import os
from typing import List, Literal, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from config import GROQ_API_KEY, TAVILY_API_KEY

# Defer vectorstore import to avoid HuggingFace downloads at module load
# from vectorstore import get_retriever

# Set environment variables
if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Lazy initialization - models loaded on first use, not at import time
_tavily = None
_router_llm = None
_judge_llm = None
_answer_llm = None


def _get_tavily():
    """Lazy initialization of Tavily search."""
    global _tavily
    if _tavily is None:
        if not TAVILY_API_KEY:
            return None
        try:
            _tavily = TavilySearch(max_results=3, topic="general")
        except Exception as e:
            print(f"Warning: Could not initialize Tavily: {e}")
            return None
    return _tavily


def _get_router_llm():
    """Lazy initialization of router LLM."""
    global _router_llm
    if _router_llm is None:
        try:
            _router_llm = ChatGroq(
                model="llama-3.3-70b-versatile", temperature=0
            ).with_structured_output(RouteDecision)
        except Exception as e:
            print(f"Warning: Could not initialize router LLM: {e}")
            raise
    return _router_llm


def _get_judge_llm():
    """Lazy initialization of judge LLM."""
    global _judge_llm
    if _judge_llm is None:
        try:
            _judge_llm = ChatGroq(
                model="llama-3.3-70b-versatile", temperature=0
            ).with_structured_output(RagJudge)
        except Exception as e:
            print(f"Warning: Could not initialize judge LLM: {e}")
            raise
    return _judge_llm


def _get_answer_llm():
    """Lazy initialization of answer LLM."""
    global _answer_llm
    if _answer_llm is None:
        try:
            _answer_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
        except Exception as e:
            print(f"Warning: Could not initialize answer LLM: {e}")
            raise
    return _answer_llm


@tool
def web_search_tool(query: str) -> str:
    """Up-to-date web info via Tavily"""
    tavily = _get_tavily()
    if tavily is None:
        return "WEB_ERROR::Tavily API not configured"
    try:
        result = tavily.invoke({"query": query})
        if isinstance(result, dict) and "results" in result:
            formatted_results = []
            for item in result["results"]:
                title = item.get("title", "No title")
                content = item.get("content", "No content")
                url = item.get("url", "")
                formatted_results.append(
                    f"Title: {title}\nContent: {content}\nURL: {url}"
                )
            return (
                "\n\n".join(formatted_results)
                if formatted_results
                else "No results found"
            )
        else:
            return str(result)
    except Exception as e:
        return f"WEB_ERROR::{e}"


@tool
def rag_search_tool(query: str) -> str:
    """Top-K chunks from KB (empty string if none)"""
    try:
        # Lazy import to avoid HuggingFace downloads at startup
        from vectorstore import get_retriever

        retriever_instance = get_retriever()
        docs = retriever_instance.invoke(query, k=5)
        return "\n\n".join(d.page_content for d in docs) if docs else ""
    except Exception as e:
        return f"RAG_ERROR::{e}"


class RouteDecision(BaseModel):
    route: Literal["rag", "web", "answer", "end"]
    reply: str | None = Field(None, description="Filled only when route == 'end'")


class RagJudge(BaseModel):
    sufficient: bool = Field(
        ...,
        description="True if retrieved information is sufficient to answer the user's question, False otherwise.",
    )


class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    route: Literal["rag", "web", "answer", "end"]
    rag: str
    web: str
    web_search_enabled: bool
    initial_router_decision: str
    router_override_reason: str


def router_node(state: AgentState, config: RunnableConfig) -> AgentState:
    router_llm = _get_router_llm()
    query = next(
        (
            m.content
            for m in reversed(state.get("messages", []))
            if isinstance(m, HumanMessage)
        ),
        "",
    )
    web_search_enabled = config.get("configurable", {}).get("web_search_enabled", True)

    system_prompt = (
        "You are an intelligent routing agent designed to direct user queries to the most appropriate tool."
        "Your primary goal is to provide accurate and relevant information by selecting the best source."
        "Prioritize using the **internal knowledge base (RAG)** for factual information that is likely "
        "to be contained within pre-uploaded documents or for common, well-established facts."
    )

    if web_search_enabled:
        system_prompt += (
            "You **CAN** use web search for queries that require very current, real-time, or broad general knowledge "
            "that is unlikely to be in a specific, static knowledge base (e.g., today's news, live data, very recent events)."
            "\n\nChoose one of the following routes:"
            "\n- 'rag': For queries about specific entities, historical facts, product details, procedures, or any information that would typically be found in a curated document collection (e.g., 'What is X?', 'How does Y work?', 'Explain Z policy')."
            "\n- 'web': For queries about current events, live data, very recent news, or broad general knowledge that requires up-to-date internet access (e.g., 'Who won the election yesterday?', 'What is the weather in London?', 'Latest news on technology')."
        )
    else:
        system_prompt += (
            "**Web search is currently DISABLED.** You **MUST NOT** choose the 'web' route."
            "If a query would normally require web search, you should attempt to answer it using RAG (if applicable) or directly from your general knowledge."
            "\n\nChoose one of the following routes:"
            "\n- 'rag': For queries about specific entities, historical facts, product details, procedures, or any information that would typically be found in a curated document collection, AND for queries that would normally go to web search but web search is disabled."
            "\n- 'answer': For very simple, direct questions you can answer without any external lookup (e.g., 'What is your name?')."
        )

    system_prompt += (
        "\n- 'answer': For very simple, direct questions you can answer without any external lookup (e.g., 'What is your name?')."
        "\n- 'end': For pure greetings or small-talk where no factual answer is expected (e.g., 'Hi', 'How are you?'). If choosing 'end', you MUST provide a 'reply'."
        "\n\nExample routing decisions:"
        "\n- User: 'What are the treatment of diabetes?' -> Route: 'rag' (Factual knowledge, likely in KB)."
        "\n- User: 'What is the capital of France?' -> Route: 'rag' (Common knowledge, can be in KB or answered directly if LLM knows)."
        "\n- User: 'Who won the NBA finals last night?' -> Route: 'web' (Current event, requires live data)."
        "\n- User: 'How do I submit an expense report?' -> Route: 'rag' (Internal procedure)."
        "\n- User: 'Tell me about quantum computing.' -> Route: 'rag' (Foundational knowledge can be in KB. If KB is sparse, judge will route to web if enabled)."
        "\n- User: 'Hello there!' -> Route: 'end', reply='Hello! How can I assist you today?'"
    )

    messages = [("system", system_prompt), ("user", query)]

    result: RouteDecision = router_llm.invoke(messages)  # type: ignore

    initial_router_decision = result.route
    router_override_reason = None

    if not web_search_enabled and result.route == "web":
        result.route = "rag"
        router_override_reason = "Web search disabled by user; redirected to RAG."

    out = {
        "messages": state.get("messages", []),
        "route": result.route,
        "web_search_enabled": web_search_enabled,
    }
    if router_override_reason:
        out["initial_router_decision"] = initial_router_decision
        out["router_override_reason"] = router_override_reason

    if result.route == "end":
        out["messages"] = state.get("messages", []) + [
            AIMessage(content=result.reply or "Hello!")
        ]

    return out  # type: ignore


def rag_node(state: AgentState, config: RunnableConfig) -> AgentState:
    judge_llm = _get_judge_llm()
    query = next(
        (
            m.content
            for m in reversed(state.get("messages", []))
            if isinstance(m, HumanMessage)
        ),
        "",
    )
    web_search_enabled = config.get("configurable", {}).get("web_search_enabled", True)
    chunks = rag_search_tool.invoke(query)  # type: ignore

    if chunks.startswith("RAG_ERROR::"):
        next_route = "web" if web_search_enabled else "answer"
        return {**state, "rag": "", "route": next_route}

    judge_messages = [
        (
            "system",
            (
                "You are a judge evaluating if the **retrieved information** is **sufficient and relevant** "
                "to fully and accurately answer the user's question. "
                "Consider if the retrieved text directly addresses the question's core and provides enough detail."
                "If the information is incomplete, vague, outdated, or doesn't directly answer the question, it's NOT sufficient."
                "If it provides a clear, direct, and comprehensive answer, it IS sufficient."
                "If no relevant information was retrieved at all (e.g., 'No results found'), it is definitely NOT sufficient."
                '\n\nRespond ONLY with a JSON object: {"sufficient": true/false}'
                "\n\nExample 1: Question: 'What is the capital of France?' Retrieved: 'Paris is the capital of France.' -> {\"sufficient\": true}"
                "\nExample 2: Question: 'What are the symptoms of diabetes?' Retrieved: 'Diabetes is a chronic condition.' -> {\"sufficient\": false} (Doesn't answer symptoms)"
                "\nExample 3: Question: 'How to fix error X in software Y?' Retrieved: 'No relevant information found.' -> {\"sufficient\": false}"
            ),
        ),
        (
            "user",
            f"Question: {query}\n\nRetrieved info: {chunks}\n\nIs this sufficient to answer the question?",
        ),
    ]
    verdict: RagJudge = judge_llm.invoke(judge_messages)  # type: ignore

    if verdict.sufficient:
        next_route = "answer"
    else:
        next_route = "web" if web_search_enabled else "answer"

    return {
        **state,
        "rag": chunks,
        "route": next_route,
        "web_search_enabled": web_search_enabled,
    }


def web_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("\n--- Entering web_node ---")
    query = next(
        (
            m.content
            for m in reversed(state.get("messages", []))
            if isinstance(m, HumanMessage)
        ),
        "",
    )

    # Check if web search is actually enabled before performing it
    web_search_enabled = config.get("configurable", {}).get("web_search_enabled", True)
    print(f"Router received web search info : {web_search_enabled}")
    if not web_search_enabled:
        print(
            "Web search node entered but web search is disabled. Skipping actual search."
        )
        return {
            **state,
            "web": "Web search was disabled by the user.",
            "route": "answer",
        }

    print(f"Web search query: {query}")
    snippets = web_search_tool.invoke(query)  # type: ignore

    if snippets.startswith("WEB_ERROR::"):
        print(f"Web Error: {snippets}. Proceeding to answer with limited info.")
        return {**state, "web": "", "route": "answer"}

    print(f"Web snippets retrieved: {snippets[:200]}...")
    print("--- Exiting web_node ---")
    return {**state, "web": snippets, "route": "answer"}


# --- Node 4: final answer ---
def answer_node(state: AgentState) -> AgentState:
    answer_llm = _get_answer_llm()
    user_q = next(
        (
            m.content
            for m in reversed(state.get("messages", []))
            if isinstance(m, HumanMessage)
        ),
        "",
    )

    ctx_parts = []
    if state.get("rag"):
        ctx_parts.append("Knowledge Base Information:\n" + state.get("rag", ""))
    if state.get("web"):
        web_content = state.get("web", "")
        if web_content and not web_content.startswith("Web search was disabled"):
            ctx_parts.append("Web Search Results:\n" + web_content)

    context = "\n\n".join(ctx_parts)
    if not context.strip():
        context = "No external context was available for this query. Try to answer based on general knowledge if possible."

    prompt = f"""Please answer the user's question using the provided context.
If the context is empty or irrelevant, try to answer based on your general knowledge.

Question: {user_q}

Context:
{context}

Provide a helpful, accurate, and concise response based on the available information."""

    ans = answer_llm.invoke([HumanMessage(content=prompt)]).content
    return {**state, "messages": state.get("messages", []) + [AIMessage(content=ans)]}


def from_router(st: AgentState) -> Literal["rag", "web", "answer", "end"]:
    return st.get("route", "answer")  # type: ignore


def after_rag(st: AgentState) -> Literal["answer", "web"]:
    route = st.get("route", "answer")
    return route if route in ("answer", "web") else "answer"  # type: ignore


def after_web(_) -> Literal["answer"]:
    return "answer"


def build_agent():
    """Builds and compiles the LangGraph agent."""
    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("rag_lookup", rag_node)
    g.add_node("web_search", web_node)
    g.add_node("answer", answer_node)

    g.set_entry_point("router")

    g.add_conditional_edges(
        "router",
        from_router,
        {"rag": "rag_lookup", "web": "web_search", "answer": "answer", "end": END},
    )

    g.add_conditional_edges(
        "rag_lookup", after_rag, {"answer": "answer", "web": "web_search"}
    )

    g.add_edge("web_search", "answer")
    g.add_edge("answer", END)

    agent = g.compile(checkpointer=MemorySaver())
    return agent


rag_agent = build_agent()
