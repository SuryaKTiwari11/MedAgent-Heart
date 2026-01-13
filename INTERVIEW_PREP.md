# 🎯 Interview Preparation Guide - MedAgent-Heart

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Core Concepts](#core-concepts)
4. [Agent Workflow Logic](#agent-workflow-logic)
5. [Technical Deep Dive](#technical-deep-dive)
6. [Design Decisions](#design-decisions)
7. [Common Interview Questions](#common-interview-questions)

---

## Project Overview

### What is MedAgent-Heart?

MedAgent-Heart is an **intelligent RAG (Retrieval Augmented Generation) chatbot** designed to provide information about cardiac health, heart diseases, treatments, and prevention methods. It combines:

- **Document-based knowledge retrieval** (RAG)
- **Real-time web search** capabilities
- **LLM-powered response generation**

### Key Value Proposition

**Problem:** Medical information is scattered across documents and web sources. Users need accurate, contextual answers about heart health.

**Solution:** An intelligent agent that:

1. Searches uploaded medical documents first (authoritative sources)
2. Falls back to web search for latest information
3. Synthesizes comprehensive, accurate responses

### Tech Stack Justification

| Technology    | Why We Chose It                                                |
| ------------- | -------------------------------------------------------------- |
| **LangGraph** | Enables complex agent workflows with state management          |
| **FastAPI**   | Async, high-performance API with automatic documentation       |
| **Streamlit** | Rapid UI development with Python, no frontend expertise needed |
| **Groq**      | Ultra-fast LLM inference (2-5x faster than alternatives)       |
| **Pinecone**  | Managed vector database with excellent scalability             |
| **Tavily**    | Specialized for LLM applications, returns clean snippets       |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   STREAMLIT FRONTEND                         │
│  ┌────────────┬──────────────┬─────────────────────────┐    │
│  │ Chat UI    │ File Upload  │ Settings Panel          │    │
│  │ - Messages │ - PDF Upload │ - Web Search Toggle     │    │
│  │ - Trace    │ - Validation │ - Session Management    │    │
│  └────────────┴──────────────┴─────────────────────────┘    │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (HTTP/JSON)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             API ENDPOINTS                             │   │
│  │  POST /chat/           - Chat with agent              │   │
│  │  POST /upload-document/- Upload PDF                   │   │
│  │  GET  /health          - Health check                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            LANGGRAPH AGENT                            │   │
│  │  ┌──────────┬─────────┬──────────┬──────────┐        │   │
│  │  │ Router   │ RAG     │ Web      │ Answer   │        │   │
│  │  │ Node     │ Lookup  │ Search   │ Node     │        │   │
│  │  └──────────┴─────────┴──────────┴──────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
└────────┬───────────────┬────────────────┬──────────────────┘
         │               │                │
         ▼               ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   GROQ LLM  │  │  PINECONE   │  │   TAVILY    │
│             │  │             │  │             │
│ llama-3.3-  │  │ Vector DB   │  │ Web Search  │
│ 70b-        │  │ Embeddings  │  │ API         │
│ versatile   │  │ Search      │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Data Flow

1. **User Input** → Streamlit UI
2. **API Request** → FastAPI Backend
3. **Agent Execution** → LangGraph workflow
4. **Router Decision** → RAG or Web Search path
5. **Context Retrieval** → Pinecone/Tavily
6. **LLM Generation** → Groq LLM
7. **Response** → Back to user with trace

---

## Core Concepts

### 1. RAG (Retrieval Augmented Generation)

**What is it?**
RAG combines retrieval systems with generative AI to produce more accurate, grounded responses.

**Why RAG?**

- **Reduces hallucinations** - Grounds responses in real documents
- **Domain expertise** - Uses specialized medical knowledge
- **Up-to-date** - Can be updated by uploading new documents
- **Transparency** - Can trace which documents informed the answer

**Our Implementation:**

```python
# 1. Document Upload → Text Extraction
documents = PyPDFLoader(pdf_path).load()

# 2. Chunking → Break into manageable pieces
chunks = text_splitter.split_documents(documents)

# 3. Embedding → Convert to vectors
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Storage → Store in Pinecone
vectorstore.add_documents(chunks)

# 5. Retrieval → Semantic search
results = vectorstore.similarity_search(query, k=5)

# 6. Generation → LLM with context
response = llm.invoke([context, query])
```

### 2. Vector Embeddings

**Concept:**
Convert text into high-dimensional numerical vectors that capture semantic meaning.

**Example:**

```
"heart attack"     → [0.23, -0.45, 0.67, ..., 0.12]  (384 dimensions)
"cardiac arrest"   → [0.25, -0.43, 0.65, ..., 0.14]  (very similar!)
"car engine"       → [-0.67, 0.23, -0.12, ..., 0.89] (very different!)
```

**Why It Matters:**

- Enables **semantic search** (meaning-based, not keyword-based)
- "heart attack" and "myocardial infarction" are close in vector space
- Supports **contextual understanding**

**Our Choice - all-MiniLM-L6-v2:**

- **384 dimensions** - Good balance of quality and speed
- **Lightweight** - Fast inference
- **Multilingual** - Handles medical terminology

### 3. LangGraph Agent Workflow

**What is LangGraph?**
A framework for building **stateful, multi-actor applications** with LLMs using graphs.

**Key Concepts:**

#### State

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]      # Conversation history
    route: str                        # Current routing decision
    rag: str                          # RAG-retrieved content
    web: str                          # Web-searched content
    web_search_enabled: bool          # User preference
```

#### Nodes (Functions that process state)

```python
def router_node(state: AgentState) -> AgentState:
    """Decides where to route the query"""
    decision = llm.invoke("Should I use RAG or web search?")
    state["route"] = decision
    return state
```

#### Edges (Connections between nodes)

```python
# Conditional edge based on state
workflow.add_conditional_edges(
    "rag_lookup",
    lambda state: "answer" if state["route"] == "answer" else "web_search"
)
```

#### Why LangGraph vs Simple Chains?

| Feature              | Simple Chain | LangGraph                    |
| -------------------- | ------------ | ---------------------------- |
| **State Management** | Limited      | Full control                 |
| **Branching Logic**  | Difficult    | Native support               |
| **Debugging**        | Hard         | Built-in tracing             |
| **Flexibility**      | Low          | High                         |
| **Complexity**       | Simple       | Can handle complex workflows |

---

## Agent Workflow Logic

### Complete Flow Diagram

```
                    START
                      │
                      ▼
            ┌─────────────────┐
            │  ROUTER NODE    │◄──── User Query
            │                 │◄──── Web Search Setting
            └────────┬────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    Route = RAG            Route = Web
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  RAG LOOKUP NODE │    │  WEB SEARCH NODE │
│                  │    │                  │
│ 1. Query Pinecone│    │ 1. Query Tavily  │
│ 2. Get top-k docs│    │ 2. Get snippets  │
│ 3. Format context│    │ 3. Format context│
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       │
    ┌──────────┐                │
    │  JUDGE   │                │
    │          │                │
    │ Is RAG   │                │
    │ enough?  │                │
    └────┬─────┘                │
         │                      │
    ┌────┴────┐                │
    │         │                │
   Yes       No                │
    │         │                │
    │         └────────────────┘
    │                  │
    └──────────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ ANSWER NODE  │
        │              │
        │ 1. Get state │
        │ 2. Build msg │
        │ 3. Call LLM  │
        │ 4. Generate  │
        └──────┬───────┘
               │
               ▼
            RETURN
```

### Detailed Node Logic

#### 1. Router Node

**Purpose:** Determine initial retrieval strategy

**Logic:**

```python
def router_node(state: AgentState, config: RunnableConfig) -> AgentState:
    # Extract query from messages
    query = get_last_human_message(state["messages"])

    # Check user preference
    web_search_enabled = config["configurable"]["web_search_enabled"]

    # Prepare prompt for LLM
    system_prompt = """
    You are a routing agent. Decide if this query needs:
    - 'rag': Answer from internal medical documents
    - 'web': Latest information from web search

    Medical facts → rag
    Latest news/treatments → web
    """

    # Get LLM decision (structured output)
    result = router_llm.invoke([SystemMessage(system_prompt),
                                HumanMessage(query)])

    # Override if web search disabled
    if not web_search_enabled and result.route == "web":
        result.route = "rag"
        state["router_override_reason"] = "Web search disabled by user"

    state["route"] = result.route
    return state
```

**Example Decisions:**

- "What is coronary artery disease?" → **RAG** (factual, in docs)
- "Latest 2026 heart disease statistics?" → **Web** (current data)
- "How to prevent heart attacks?" → **RAG** (general knowledge)

#### 2. RAG Lookup Node

**Purpose:** Retrieve relevant information from uploaded documents

**Logic:**

```python
def rag_lookup_node(state: AgentState, config: RunnableConfig) -> AgentState:
    query = get_last_human_message(state["messages"])

    # Semantic search in Pinecone
    results = search_vectorstore(query, k=5)

    # Format retrieved chunks
    rag_content = "\n\n".join([doc.page_content for doc in results])
    state["rag"] = rag_content

    # Judge if content is sufficient
    judge_prompt = f"""
    Query: {query}
    Retrieved Content: {rag_content}

    Is this content sufficient to answer the query?
    """

    judgment = judge_llm.invoke(judge_prompt)

    if judgment.sufficient:
        state["route"] = "answer"  # Go to answer
    else:
        state["route"] = "web_search"  # Need more info

    return state
```

**Key Points:**

- Uses **cosine similarity** to find relevant chunks
- **k=5** means top 5 most relevant chunks
- **Judge LLM** evaluates quality - prevents hallucination
- Can route to web search if RAG insufficient

#### 3. Web Search Node

**Purpose:** Get latest information from the internet

**Logic:**

```python
def web_node(state: AgentState, config: RunnableConfig) -> AgentState:
    query = get_last_human_message(state["messages"])
    web_search_enabled = config["configurable"]["web_search_enabled"]

    if not web_search_enabled:
        state["web"] = "Web search disabled by user"
        state["route"] = "answer"
        return state

    # Use Tavily for web search
    search_tool = TavilySearchResults(max_results=3)
    results = search_tool.invoke(query)

    # Format snippets
    web_content = "\n\n".join([
        f"Title: {r['title']}\nContent: {r['content']}"
        for r in results
    ])

    state["web"] = web_content
    state["route"] = "answer"
    return state
```

**Why Tavily?**

- Returns **clean, LLM-ready snippets** (not raw HTML)
- **Fast** - optimized for AI applications
- **Relevant** - understands query intent

#### 4. Answer Node

**Purpose:** Generate final response using all gathered context

**Logic:**

```python
def answer_node(state: AgentState, config: RunnableConfig) -> AgentState:
    query = get_last_human_message(state["messages"])

    # Gather all available context
    context_parts = []

    if state.get("rag"):
        context_parts.append(f"From knowledge base:\n{state['rag']}")

    if state.get("web"):
        context_parts.append(f"From web search:\n{state['web']}")

    context = "\n\n".join(context_parts)

    # Build prompt
    system_prompt = """
    You are a cardiac health assistant. Use the provided context
    to answer the user's question accurately and comprehensively.

    If information is limited, acknowledge it.
    Focus on clarity and medical accuracy.
    """

    messages = [
        SystemMessage(system_prompt),
        HumanMessage(f"Context:\n{context}\n\nQuestion: {query}")
    ]

    # Generate response
    response = answer_llm.invoke(messages)

    # Add to conversation history
    state["messages"].append(AIMessage(content=response.content))

    return state
```

**Temperature Settings:**

- **Router/Judge LLM**: temp=0 (deterministic)
- **Answer LLM**: temp=0.7 (slightly creative, but controlled)

---

## Technical Deep Dive

### 1. Why FastAPI Over Flask?

| Feature            | FastAPI                     | Flask                  |
| ------------------ | --------------------------- | ---------------------- |
| **Performance**    | ⚡ Async, fast              | Slower (WSGI)          |
| **Type Safety**    | ✅ Pydantic models          | ❌ Manual validation   |
| **Documentation**  | ✅ Auto-generated (Swagger) | ❌ Manual              |
| **Async Support**  | ✅ Native                   | ⚠️ Requires extensions |
| **Learning Curve** | Medium                      | Easy                   |

**Our Use Case:**

- Need **async** for concurrent requests
- Want **automatic API docs** (/docs endpoint)
- Type safety with **Pydantic** reduces bugs

### 2. Session Management

**Challenge:** Maintain conversation context across requests

**Solution: Stateless API + LangGraph Checkpointing**

```python
# Frontend generates unique session ID
session_id = str(uuid.uuid4())  # "550e8400-e29b-41d4-a716-446655440000"

# Sent with every request
config = {
    "configurable": {
        "thread_id": session_id,
        "web_search_enabled": True
    }
}

# LangGraph uses MemorySaver to checkpoint state
memory = MemorySaver()
agent = workflow.compile(checkpointer=memory)

# State persists within session
agent.invoke(inputs, config=config)
```

**Benefits:**

- **Stateless API** - easier to scale
- **Session isolation** - multiple users don't interfere
- **Conversation memory** - agent remembers context

### 3. Document Processing Pipeline

**Step-by-step:**

```python
# 1. Upload (FastAPI receives file)
uploaded_file = UploadFile(...)

# 2. Temporary storage
with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
    tmp.write(await uploaded_file.read())

    # 3. PDF parsing
    loader = PyPDFLoader(tmp.name)
    documents = loader.load()  # List[Document]

    # 4. Text chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # ~200 words per chunk
        chunk_overlap=200,    # 20% overlap for context
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    # 5. Embedding generation
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 6. Upload to Pinecone
    for chunk in chunks:
        vector = embeddings_model.embed_query(chunk.page_content)
        index.upsert([(chunk_id, vector, {"text": chunk.page_content})])
```

**Why Chunking?**

- **LLM context limits** - Can't process entire book
- **Retrieval precision** - Smaller chunks = more relevant results
- **Overlap** - Preserves context across chunk boundaries

**Chunk Size Trade-offs:**

- **Too small** (100 chars): Loses context, too many chunks
- **Too large** (10000 chars): Less precise, slower retrieval
- **Sweet spot** (1000 chars): Good balance ✅

### 4. Vector Search Deep Dive

**How Similarity Search Works:**

```python
# 1. Query embedding
query = "What causes heart attacks?"
query_vector = embeddings.embed_query(query)  # 384-dimensional vector

# 2. Pinecone search (cosine similarity)
results = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True
)

# 3. Returns most similar chunks
# Similarity score: -1 (opposite) to 1 (identical)
# Typical good matches: 0.7+
```

**Cosine Similarity Formula:**

```
similarity = (A · B) / (||A|| × ||B||)

Where:
A, B = vectors
· = dot product
||·|| = magnitude
```

**Example:**

```
Query: "heart disease treatment"
Results:
1. "Treatment for coronary artery disease includes..." (score: 0.89)
2. "Managing heart disease with medication and..." (score: 0.85)
3. "Heart disease prevention strategies..." (score: 0.72)
4. "Different types of cardiovascular diseases..." (score: 0.68)
5. "Symptoms of heart failure include..." (score: 0.62)
```

---

## Design Decisions

### 1. Why Separate Backend and Frontend?

**Monolith Alternative:**

```python
# Everything in one Streamlit app
import streamlit as st
from langchain import ...

# Problem: Tightly coupled, hard to test, can't use API elsewhere
```

**Our Approach:**

```
Backend (FastAPI) ←→ Frontend (Streamlit)
     ↓
Can add: Mobile app, CLI, other clients
```

**Benefits:**

- **Separation of concerns** - UI vs business logic
- **API reusability** - Can build mobile app later
- **Independent scaling** - Scale API separately from UI
- **Testing** - Can test API without UI
- **Technology flexibility** - Can swap Streamlit for React later

### 2. Why Groq Over OpenAI?

| Feature           | Groq                     | OpenAI                     |
| ----------------- | ------------------------ | -------------------------- |
| **Speed**         | ⚡⚡⚡ 500+ tokens/sec   | 🐌 50-100 tokens/sec       |
| **Cost**          | 💰 Cheaper               | 💰💰 More expensive        |
| **Model Quality** | ✅ LLaMA 3.3 (excellent) | ✅ GPT-4 (slightly better) |
| **Availability**  | ✅ Good                  | ⚠️ Rate limits             |

**Our Use Case:**

- Speed matters for **real-time chat**
- LLaMA 3.3 70B is **good enough** for medical Q&A
- **Cost-effective** for production

### 3. Hybrid RAG + Web Search

**Why Not Just RAG?**

- Documents get **outdated**
- Latest research, statistics need **web search**

**Why Not Just Web Search?**

- Web has **noise**, unreliable sources
- Our documents are **curated**, authoritative

**Hybrid Approach:**

```
User Query
    ↓
Router decides based on query type
    ↓
Try RAG first (trusted sources)
    ↓
Judge if sufficient
    ↓
Fall back to web if needed
    ↓
Generate answer with best available context
```

**Example Flow:**

```
Query: "What is coronary artery disease?"
→ RAG (medical facts, well-documented)
→ Sufficient ✅
→ Answer from uploaded documents

Query: "Heart disease statistics in 2026?"
→ RAG (tries first)
→ Insufficient ❌ (outdated data)
→ Web Search (gets latest stats)
→ Answer from web sources
```

---

## Common Interview Questions

### Architecture & Design

**Q: Why did you choose this tech stack?**
**A:**

- **LangGraph**: Needed complex agent workflows with branching logic and state management
- **FastAPI**: Required async support for concurrent requests, automatic API docs, and type safety
- **Streamlit**: Rapid prototyping of interactive UI without frontend expertise
- **Groq**: 5x faster inference than alternatives, crucial for real-time chat
- **Pinecone**: Managed vector DB, handles scaling automatically, no ops overhead

**Q: How does your RAG system prevent hallucinations?**
**A:**

1. **Retrieval first**: Grounds answers in actual documents
2. **Judge LLM**: Evaluates if retrieved content is sufficient
3. **Source transparency**: Trace shows which sources were used
4. **Fallback mechanism**: Web search for missing information
5. **Temperature control**: Low temperature (0.7) for factual responses

**Q: How would you scale this system?**
**A:**

- **Backend**: Deploy multiple FastAPI instances behind load balancer
- **Database**: Pinecone already scales automatically (managed service)
- **Caching**: Add Redis for frequent queries
- **Async**: Already using async for I/O-bound operations
- **CDN**: Serve static assets from CDN
- **Monitoring**: Add Prometheus/Grafana for metrics

### Technical Implementation

**Q: Explain the LangGraph workflow.**
**A:**

```
1. Router Node: Analyzes query, decides RAG vs Web
2. RAG Lookup: Searches Pinecone vector store
3. Judge: Evaluates if RAG content is sufficient
4. Web Search: Falls back to Tavily if needed
5. Answer: Synthesizes response from available context

State flows through nodes, each adding information.
Conditional edges route based on state values.
MemorySaver checkpoints state for conversation continuity.
```

**Q: How do embeddings work in your system?**
**A:**

- Use **sentence-transformers/all-MiniLM-L6-v2**
- Converts text to 384-dimensional vectors
- Captures semantic meaning: "heart attack" ≈ "myocardial infarction"
- **Cosine similarity** finds nearest neighbors
- **Trade-off**: Smaller model (fast) vs larger model (more accurate)
- Good enough for our domain-specific use case

**Q: What's the purpose of the Judge LLM?**
**A:**
Prevents low-quality responses. If RAG retrieves irrelevant documents:

- **Without Judge**: Would generate answer from poor context → hallucination
- **With Judge**: Recognizes insufficiency → routes to web search → better answer

Example:

```
Query: "Latest 2026 heart disease cure"
RAG retrieves: General info about heart disease from 2020 PDF
Judge: "Insufficient - needs current information"
→ Routes to web search instead
```

### Problem Solving

**Q: How do you handle rate limits from external APIs?**
**A:**

- **Exponential backoff**: Retry with increasing delays
- **Circuit breaker**: Stop calling if service is down
- **Caching**: Cache common queries to reduce API calls
- **Queue system**: Use Celery for background processing
- **Multiple providers**: Fallback LLM providers

**Q: What if Pinecone goes down?**
**A:**

- **Fallback to web search**: Temporarily disable RAG path
- **Backup vector store**: Maintain local FAISS instance
- **Graceful degradation**: Show warning, still provide web-based answers
- **Monitoring**: Alert on Pinecone errors

**Q: How do you ensure data privacy?**
**A:**

- **Session isolation**: Each user has unique session_id
- **No logging of queries**: Only log errors, not user data
- **Temporary file handling**: Delete PDFs after processing
- **API key security**: Use environment variables, never commit
- **HTTPS**: Encrypt data in transit (in production)

### Testing & Debugging

**Q: How do you test the agent workflow?**
**A:**

1. **Unit tests**: Test individual nodes in isolation
2. **Integration tests**: Test full workflow end-to-end
3. **Mock external services**: Mock Groq, Pinecone, Tavily
4. **Trace inspection**: LangGraph provides execution trace
5. **Test queries**: Predefined queries with expected outcomes

Example:

```python
def test_router_decision():
    state = {"messages": [HumanMessage("What is heart disease?")]}
    result = router_node(state, config)
    assert result["route"] == "rag"  # Should choose RAG for factual query
```

**Q: How do you debug when the agent gives wrong answers?**
**A:**

1. **Check trace events**: See which path was taken
2. **Inspect retrieved context**: Was RAG content relevant?
3. **Review LLM prompts**: Are instructions clear?
4. **Test embeddings**: Check similarity scores
5. **Validate data**: Is source document accurate?

**Process:**

```
Wrong Answer
    ↓
Check trace → Which node failed?
    ↓
Router → Was routing decision correct?
RAG → Were retrieved docs relevant?
Judge → Did it correctly assess sufficiency?
Answer → Did LLM misinterpret context?
    ↓
Fix root cause
```

---

## Key Takeaways for Interview

### 1. Understanding the Problem

- **Medical information is fragmented** across documents and web
- Need **accuracy** (no hallucinations) and **recency** (latest info)
- **Hybrid approach** solves both problems

### 2. Technical Strengths

- **Agent-based architecture** allows complex decision-making
- **RAG** grounds responses in authoritative sources
- **Vector search** enables semantic understanding
- **Modular design** makes it maintainable and testable

### 3. Production Readiness

- **Error handling** at every layer
- **Logging and tracing** for debugging
- **Graceful degradation** when services fail
- **Scalable architecture** (stateless API, managed services)

### 4. Trade-offs You Made

- **Groq vs OpenAI**: Speed over slight quality advantage
- **Pinecone vs self-hosted**: Managed service over control
- **Streamlit vs React**: Development speed over customization
- **LangGraph vs custom**: Framework support over flexibility

### 5. Future Improvements

- **Multi-modal**: Support images (X-rays, ECGs)
- **Fine-tuning**: Custom model on medical data
- **Advanced RAG**: Re-ranking, hybrid search
- **Analytics**: Track query patterns, improve responses
- **Authentication**: User accounts, personalization

---

## Practice Questions

### Answer These Before Your Interview:

1. **Walk me through what happens when a user asks "What causes heart attacks?"**

2. **Why use vector embeddings instead of keyword search?**

3. **How does LangGraph differ from a simple if/else routing?**

4. **What happens if the RAG database has no relevant documents?**

5. **Explain the trade-off between chunk size and retrieval quality.**

6. **How would you add user authentication to this system?**

7. **What metrics would you track in production?**

8. **How do you prevent the LLM from hallucinating?**

9. **Explain the agent's decision-making process.**

10. **What would you do if response time becomes too slow?**

---

## Glossary

- **RAG**: Retrieval Augmented Generation
- **Embedding**: Vector representation of text
- **Vector Store**: Database optimized for similarity search
- **LLM**: Large Language Model
- **Agent**: Autonomous system that makes decisions
- **Node**: Function in agent workflow
- **State**: Data passed between nodes
- **Checkpoint**: Saved state for conversation continuity
- **Semantic Search**: Meaning-based search vs keyword
- **Hallucination**: LLM generating false information
- **Temperature**: Controls randomness in LLM output
- **Top-k**: Number of results to retrieve
- **Cosine Similarity**: Measure of vector similarity
- **Chunking**: Breaking documents into smaller pieces

---

**Good luck with your interview! 🚀**

_Remember: Understand the "why" behind every decision. Interviewers value reasoning over memorization._
