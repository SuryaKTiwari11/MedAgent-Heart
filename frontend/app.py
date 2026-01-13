# rag_agent_app/frontend/app.py

import streamlit as st
from config import FRONTEND_CONFIG
from session_manager import init_session_state
from ui_components import (
    display_header,
    render_document_upload_section,
    render_agent_settings_section,
    display_chat_history,
    display_trace_events,
)
from backendApi import chat_with_backend_agent


def main():
    """Main function to run the Streamlit application."""

    # Initialize session state variables
    init_session_state()

    # Get FastAPI base URL from config
    fastapi_base_url = FRONTEND_CONFIG["FASTAPI_BASE_URL"]

    # Render UI sections
    display_header()
    render_document_upload_section(fastapi_base_url)
    render_agent_settings_section()

    st.markdown(
        """
        <h2 style='margin-top: 2rem;'>
            💬 Chat Interface
        </h2>
        <p style='color: #9195a1; margin-bottom: 1rem;'>
            Ask questions about heart diseases, treatments, symptoms, and prevention
        </p>
    """,
        unsafe_allow_html=True,
    )

    display_chat_history()

    # User input field
    if prompt := st.chat_input(
        "💭 Ask me about heart health, diseases, treatments, or prevention..."
    ):
        # Add user's message to chat history and display immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant's response and trace
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                try:
                    # Call the backend API for chat
                    agent_response, trace_events = chat_with_backend_agent(
                        fastapi_base_url,
                        st.session_state.session_id,
                        prompt,
                        st.session_state.web_search_enabled,
                    )

                    # Display the agent's final response
                    st.markdown(agent_response)
                    # Add the agent's response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": agent_response}
                    )

                    # Display the workflow trace
                    display_trace_events(trace_events)

                except requests.exceptions.ConnectionError:
                    st.error(
                        "❌ Could not connect to the backend server. Please ensure it's running on port 8000."
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "❌ Error: Could not connect to the backend server.",
                        }
                    )
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Request error: {e}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"❌ Error: {e}"}
                    )
                except json.JSONDecodeError:
                    st.error("❌ Received an invalid response from the backend.")
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "❌ Error: Invalid response from backend.",
                        }
                    )
                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"❌ Unexpected Error: {e}"}
                    )

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid #464a53;'>
            <p style='color: #757b8a; font-size: 0.9rem;'>
                🫀 <strong>MedAgent-Heart</strong> | Powered by LangGraph + Groq + Pinecone<br>
                <span style='color: #5e626e; font-size: 0.8rem;'>
                    AI-powered cardiac health information system | Always consult healthcare professionals
                </span>
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
