import streamlit as st
import os
from research_engine import PEResearchEngine

# Page configuration
st.set_page_config(
    page_title="PE Research AI",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit elements for clean interface
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 1rem;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    header {visibility: hidden;}
    .css-18e3th9 {padding-top: 0rem;}
    .css-1d391kg {padding-top: 1rem;}
    .element-container iframe {
        background-color: transparent;
    }
    .stChatMessage {
        background-color: transparent;
    }
    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    #MainMenu {
        visibility: hidden;
        height: 0%;
    }
    header {
        visibility: hidden;
        height: 0%;
    }
    footer {
        visibility: hidden;
        height: 0%;
    }
    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize the research engine
@st.cache_resource
def get_research_engine():
    return PEResearchEngine()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "research_engine" not in st.session_state:
    st.session_state.research_engine = get_research_engine()

# Welcome section - only show if no messages exist
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #FD5108; font-size: 2.5rem; font-weight: 600; margin-bottom: 0.5rem;">
            🏢 PE Research AI
        </h1>
        <p style="color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;">
            Professional AI-powered company analysis for Private Equity research
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example prompts
    st.markdown("### Try asking about:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Tell me about Tesla", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Tell me about Tesla"})
            st.rerun()
            
        if st.button("🏭 Analyze Apple's market position", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Analyze Apple's market position"})
            st.rerun()
    
    with col2:
        if st.button("🔍 Who are Microsoft's competitors?", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Who are Microsoft's competitors?"})
            st.rerun()
            
        if st.button("💰 PE opportunities in Netflix", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What are the PE opportunities in Netflix?"})
            st.rerun()

# Chat interface
else:
    # App title for chat mode
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem;">
        <h2 style="color: #FD5108; font-size: 1.5rem; font-weight: 600; margin: 0;">
            🏢 PE Research AI
        </h2>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about any company for PE research analysis..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing company data..."):
            try:
                response = st.session_state.research_engine.analyze_company(prompt, st.session_state.messages)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"**Research Error:** {str(e)}\n\nPlease try again with a different company name or rephrase your question."
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Clear chat button (only show when there are messages)
if st.session_state.messages:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Start New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()