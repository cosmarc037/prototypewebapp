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

# Handle example queries
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
else:
    prompt = None

# Chat input
if prompt or (prompt := st.chat_input("Ask about any company (e.g., 'Tell me about Tesla' or 'Who are Apple's competitors?')")):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔍 Extracting company name...")
            progress_bar.progress(20)
            
            status_text.text("📊 Gathering financial data...")
            progress_bar.progress(40)
            
            status_text.text("🌐 Collecting market intelligence...")
            progress_bar.progress(60)
            
            status_text.text("🤖 Analyzing with AI...")
            progress_bar.progress(80)
            try:
                response = st.session_state.research_engine.analyze_company(prompt, st.session_state.messages)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"**Research Error:** {str(e)}\n\n**Suggestions:**\n- Try using a well-known company name (e.g., 'Apple', 'Tesla')\n- Check spelling and use full company names\n- Ensure the company is publicly traded\n- Try rephrasing your question"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


# Export functionality
    st.header("📥 Export")
    if st.session_state.messages:
        # Prepare export data
        export_data = []
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                export_data.append(f"**Analysis:**\n{msg['content']}\n\n---\n\n")
        
        if export_data:
            export_text = "".join(export_data)
            st.download_button(
                label="Download Research Report",
                data=export_text,
                file_name=f"pe_research_report_{int(time.time())}.md",
                mime="text/markdown"
            )


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
    
    st.header("🚀 Quick Examples")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Analyze Apple", key="apple_btn"):
            st.session_state.example_query = "Tell me about Apple"
        if st.button("🚗 Tesla Analysis", key="tesla_btn"):
            st.session_state.example_query = "Analyze Tesla's market position"
    
    with col2:
        if st.button("💻 Microsoft Research", key="msft_btn"):
            st.session_state.example_query = "Research Microsoft"
        if st.button("🏪 Amazon Overview", key="amzn_btn"):
            st.session_state.example_query = "Tell me about Amazon"
    
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
