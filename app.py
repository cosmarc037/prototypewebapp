import streamlit as st
import os
from research_engine import PEResearchEngine

# Page configuration
st.set_page_config(
    page_title="PE Research Chatbot",
    page_icon="🏢",
    layout="wide"
)

# Initialize the research engine
@st.cache_resource
def get_research_engine():
    return PEResearchEngine()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "research_engine" not in st.session_state:
    st.session_state.research_engine = get_research_engine()

# App title and description
st.title("🏢 Private Equity Research Chatbot")
st.markdown("**Professional AI-powered company analysis for Private Equity research**")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about any company (e.g., 'Tell me about Tesla' or 'Who are Apple's competitors?')"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Researching company information..."):
            try:
                response = st.session_state.research_engine.analyze_company(prompt, st.session_state.messages)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"**Error:** {str(e)}\n\nPlease try again or rephrase your question."
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Sidebar with instructions and controls
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    **Ask questions like:**
    - "Tell me about [Company Name]"
    - "Who are Tesla's competitors?"
    - "What are Apple's financial highlights?"
    - "Analyze Microsoft's market position"
    - "PE opportunities in the EV sector"
    
    **Features:**
    - Real-time company research
    - Financial data analysis
    - Competitor identification
    - Market opportunity assessment
    - PE-focused insights
    """)
    
    st.header("🔧 Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.header("ℹ️ About")
    st.markdown("""
    This chatbot provides comprehensive company analysis 
    for Private Equity research using real-time data 
    from multiple sources.
    
    **Data Sources:**
    - Financial APIs
    - Web scraping
    - Market databases
    - AI analysis
    """)

# Footer
st.markdown("---")
st.markdown("*Private Equity Research Chatbot - Professional company analysis at your fingertips*")
