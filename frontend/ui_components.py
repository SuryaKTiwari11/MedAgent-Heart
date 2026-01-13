# rag_agent_app/frontend/ui_components.py

import streamlit as st
from backendApi import upload_document_to_backend, chat_with_backend_agent
from session_manager import init_session_state  # Import to access session state


def apply_custom_css():
    """Apply custom CSS styling with the color palette."""
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main app styling */
        .stApp {
            background: linear-gradient(135deg, #17191c 0%, #2f3137 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Header styling */
        h1 {
            color: #00eaff !important;
            font-weight: 700 !important;
            text-shadow: 0 0 20px rgba(0, 234, 255, 0.3);
            padding: 1rem 0;
        }
        
        h2, h3 {
            color: #66f2ff !important;
            font-weight: 600 !important;
        }
        
        /* Card-like containers */
        .stExpander {
            background-color: #2f3137 !important;
            border: 1px solid #464a53 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* File uploader */
        .stFileUploader {
            background-color: #2f3137;
            border: 2px dashed #00eaff;
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #00eaff 0%, #00bbcc 100%);
            color: #17191c;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 2rem;
            box-shadow: 0 4px 12px rgba(0, 234, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #33eeff 0%, #00eaff 100%);
            box-shadow: 0 6px 20px rgba(0, 234, 255, 0.5);
            transform: translateY(-2px);
        }
        
        /* Checkbox */
        .stCheckbox {
            color: #c8cad0 !important;
        }
        
        /* Chat messages */
        .stChatMessage {
            background-color: #2f3137 !important;
            border-radius: 12px !important;
            border-left: 4px solid #00eaff !important;
            margin: 0.5rem 0;
            padding: 1rem !important;
        }
        
        /* Chat input */
        .stChatInputContainer {
            background-color: #2f3137;
            border-radius: 12px;
            border: 1px solid #464a53;
        }
        
        /* Success messages */
        .stSuccess {
            background-color: rgba(0, 234, 255, 0.1);
            color: #66f2ff;
            border-left: 4px solid #00eaff;
            border-radius: 8px;
        }
        
        /* Warning messages */
        .stWarning {
            background-color: rgba(249, 198, 57, 0.1);
            color: #fad46b;
            border-left: 4px solid #f7b708;
            border-radius: 8px;
        }
        
        /* Error messages */
        .stError {
            background-color: rgba(247, 60, 8, 0.1);
            color: #fa8a6b;
            border-left: 4px solid #f73c08;
            border-radius: 8px;
        }
        
        /* Info messages */
        .stInfo {
            background-color: rgba(0, 234, 255, 0.1);
            color: #66f2ff;
            border-left: 4px solid #00eaff;
            border-radius: 8px;
        }
        
        /* Markdown text */
        .stMarkdown {
            color: #c8cad0;
        }
        
        /* Divider */
        hr {
            border-color: #464a53 !important;
            opacity: 0.3;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #00eaff !important;
        }
        
        /* Subheader in expander */
        .stExpander h3 {
            color: #00eaff !important;
        }
        
        /* JSON display */
        .stJson {
            background-color: #17191c;
            border: 1px solid #464a53;
            border-radius: 8px;
        }
        
        /* Text area and input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #2f3137;
            color: #e3e5e8;
            border: 1px solid #464a53;
            border-radius: 8px;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #2f3137;
        }
        
        /* Code blocks */
        code {
            background-color: #17191c;
            color: #00eaff;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
        }
        
        /* Accent gradient for headers */
        .gradient-text {
            background: linear-gradient(135deg, #00eaff 0%, #f7b708 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def display_header():
    """Renders the main title and introductory markdown."""
    st.set_page_config(page_title="MedAgent-Heart 🫀", layout="wide", page_icon="🫀")

    # Apply custom CSS
    apply_custom_css()

    # Header with gradient and icon
    st.markdown(
        """
        <h1 style='text-align: center;'>
            🫀 MedAgent-Heart
        </h1>
        <p style='text-align: center; color: #9195a1; font-size: 1.1rem; margin-bottom: 2rem;'>
            Your AI-powered cardiac health assistant. Ask questions about heart diseases, treatments, and prevention.
        </p>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_document_upload_section(fastapi_base_url: str):
    """
    Renders the UI for uploading PDF documents to the knowledge base.
    Handles file upload and API call to the backend.
    """
    st.markdown(
        """
        <h2 style='margin-top: 2rem;'>
            📄 Upload Medical Documents
        </h2>
        <p style='color: #9195a1; margin-bottom: 1rem;'>
            Enhance the knowledge base by uploading medical research papers or documents (PDF format only)
        </p>
    """,
        unsafe_allow_html=True,
    )

    with st.expander("📤 Upload New Document", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose a PDF file", type="pdf", key="pdf_uploader"
        )

        if st.button("📤 Upload PDF", key="upload_pdf_button"):
            if uploaded_file is not None:
                with st.spinner(f"📊 Processing {uploaded_file.name}..."):
                    try:
                        upload_data = upload_document_to_backend(
                            fastapi_base_url, uploaded_file
                        )
                        st.success(
                            f"✅ PDF '{upload_data.get('filename')}' uploaded successfully! Processed {upload_data.get('processed_chunks')} chunks."
                        )
                    except Exception as e:
                        st.error(f"❌ An error occurred during upload: {e}")
            else:
                st.warning("⚠️ Please upload a PDF file before clicking 'Upload PDF'.")
    st.markdown("---")


def render_agent_settings_section():
    """
    Renders the section for agent settings, including the web search toggle.
    Updates the 'web_search_enabled' flag in session state.
    """
    st.markdown(
        """
        <h2 style='margin-top: 2rem;'>
            ⚙️ Agent Configuration
        </h2>
        <p style='color: #9195a1; margin-bottom: 1rem;'>
            Customize how the agent retrieves information
        </p>
    """,
        unsafe_allow_html=True,
    )

    # Checkbox with better styling
    st.session_state.web_search_enabled = st.checkbox(
        "🌐 Enable Web Search",
        value=st.session_state.web_search_enabled,
        help="When enabled, the agent can search the web if the knowledge base doesn't have sufficient information. When disabled, it will only use uploaded documents.",
    )

    if st.session_state.web_search_enabled:
        st.info(
            "🌐 Web search is **enabled** - Agent can search online for latest information"
        )
    else:
        st.warning(
            "📚 Web search is **disabled** - Agent will only use uploaded documents"
        )

    st.markdown("---")


def display_chat_history():
    """Displays all messages currently in the session state chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def display_trace_events(trace_events: list):
    """
    Renders the detailed agent workflow trace in an expandable section.
    Uses icons and conditional styling for better readability.
    """
    if trace_events:
        with st.expander("🔬 Agent Workflow Trace", expanded=False):
            st.markdown(
                """
                <p style='color: #9195a1; margin-bottom: 1rem;'>
                    See how the agent processed your query step-by-step
                </p>
            """,
                unsafe_allow_html=True,
            )

            for event in trace_events:
                icon_map = {
                    "router": "🔀",
                    "rag_lookup": "📚",
                    "web_search": "🌐",
                    "answer": "💬",
                    "__end__": "✅",
                }
                icon = icon_map.get(event["node_name"], "⚙️")

                st.markdown(
                    f"""
                    <div style='background-color: #17191c; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #00eaff;'>
                        <h4 style='color: #00eaff; margin: 0;'>{icon} Step {event['step']}: {event['node_name'].replace('_', ' ').title()}</h4>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                st.write(f"**Description:** {event['description']}")

                if (
                    event["node_name"] == "rag_lookup"
                    and "sufficiency_verdict" in event["details"]
                ):
                    verdict = event["details"]["sufficiency_verdict"]
                    if verdict == "Sufficient":
                        st.success(
                            f"📚 **RAG Verdict:** {verdict} - Relevant information found in knowledge base"
                        )
                    else:
                        st.warning(
                            f"📭 **RAG Verdict:** {verdict} - Insufficient information in knowledge base. Searching the web..."
                        )

                    if "retrieved_content_summary" in event["details"]:
                        st.markdown(
                            f"**Retrieved Content:** `{event['details']['retrieved_content_summary']}`"
                        )
                elif (
                    event["node_name"] == "web_search"
                    and "retrieved_content_summary" in event["details"]
                ):
                    st.markdown(
                        f"**🌐 Web Search Results:** `{event['details']['retrieved_content_summary']}`"
                    )
                elif (
                    event["node_name"] == "router"
                    and "router_override_reason" in event["details"]
                ):
                    st.info(
                        f"🔀 **Router Override:** {event['details']['router_override_reason']}"
                    )
                    st.json(
                        {
                            "initial_decision": event["details"]["initial_decision"],
                            "final_decision": event["details"]["final_decision"],
                        }
                    )
                elif event["details"]:
                    st.json(event["details"])

                st.markdown(
                    "<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True
                )
