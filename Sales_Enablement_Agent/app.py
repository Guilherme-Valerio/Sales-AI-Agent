import streamlit as st
import vertexai
from vertexai import agent_engines
import os

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_RESOURCE_NAME = "projects/243890394709/locations/us-central1/reasoningEngines/5895314166809362432"

st.set_page_config(page_title="Sales Intelligence Agent", page_icon="💼")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    if st.button("Reset Conversation", help="Clear history and start a new session"):
        st.session_state.messages = []
        if "agent_session_id" in st.session_state:
            del st.session_state.agent_session_id
        st.rerun()
    
    st.info("The Reset button clears the agent's memory and the chat UI.")

st.title("💼 Sales Lead Agent")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)
remote_app = agent_engines.get(AGENT_RESOURCE_NAME)

# Persistent Session Logic
if "agent_session_id" not in st.session_state:
    session = remote_app.create_session(user_id="gui_web_user")
    st.session_state.agent_session_id = session["id"]

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("How can I help with your leads today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        status_placeholder = st.status("Agent is thinking...", expanded=False)
        full_response = ""
        
        try:
            responses = remote_app.stream_query(
                user_id="gui_web_user", 
                session_id=st.session_state.agent_session_id,
                message=prompt
            )
            
            for event in responses:
                if "content" in event:
                    parts = event["content"].get("parts", [])
                    for part in parts:
                        if "text" in part:
                            full_response += part["text"]
                            response_placeholder.markdown(full_response + "▌")
                        
                        elif "function_call" in part:
                            fn = part["function_call"]
                            status_placeholder.write(f"🛠️ Calling Tool: `{fn['name']}`")
                        
                        elif "function_response" in part:
                            status_placeholder.write("✅ Tool execution complete.")

            response_placeholder.markdown(full_response)
            status_placeholder.update(label="Response complete!", state="complete", expanded=False)
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for Quota/Rate Limit issues
            if "429" in error_msg or "Resource has been exhausted" in error_msg:
                st.warning("⚠️ **API Quota Exceeded (Error 429)**")
                full_response = (
                    "The system is currently handling too many requests. "
                    "Please wait about 10-20 seconds before trying again. "
                    "If this persists, we may need to increase the project's Vertex AI quotas."
                )
            else:
                # General error handling
                st.error(f"❌ **Agent Error:** {error_msg}")
                full_response = (
                    "I encountered an unexpected issue. You can try clicking "
                    "'Reset Conversation' in the sidebar to start a clean session."
                )
            
            # Ensure the placeholder shows the final status message
            response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
