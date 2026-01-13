# rag_agent_app/frontend/session_manager.py

import streamlit as st
import uuid


def init_session_state():
    """
    Initializes necessary variables in Streamlit's session state.
    This ensures data persists across reruns of the Streamlit app.
    """
    # Initialize chat message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize a unique session ID for LangGraph checkpointing and conversation tracking
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        # Add an initial greeting from the assistant for a fresh conversation
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": """👋 **Welcome to MedAgent-Heart!**

I'm your AI-powered cardiac health assistant. I can help you with:

🫀 **Heart Disease Information** - Learn about different types of heart conditions
💊 **Treatment Options** - Understand available treatments and medications  
🛡️ **Prevention Strategies** - Get advice on preventing heart disease
⚠️ **Symptoms & Diagnosis** - Identify warning signs and diagnostic procedures

**Try asking:**
- "What are the main types of heart diseases?"
- "How can I prevent heart disease?"
- "What are the symptoms of a heart attack?"
- "What treatments are available for coronary artery disease?"

Feel free to ask me anything about heart health! 💙""",
            }
        )

    # Initialize the web search enabled flag, defaulting to True
    if "web_search_enabled" not in st.session_state:
        st.session_state.web_search_enabled = True
