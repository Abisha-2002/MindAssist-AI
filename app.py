"""
MindAssist AI - Main Streamlit Application
Complete Agentic AI system with Router, Orchestrator, RAG, and Reflection
"""
import streamlit as st
import sys
import importlib

# Force reload of model_clients to pick up changes
if 'utils.model_clients' in sys.modules:
    importlib.reload(sys.modules['utils.model_clients'])

from agents.router import route_query
from agents.orchestrator import Orchestrator
from agents.research_agent import ResearchAgent
from agents.reflection_agent import ReflectionAgent
from agents.search_tool import SearchTool  # NEW
from rag.loader import get_vector_store, evaluate_retrieval
from utils.model_clients import MODELS

# Page Configuration
st.set_page_config(
    page_title="MindAssist AI - Research Assistant",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    .agent-status {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .final-answer {
        background: #d4edda;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .web-search-box {
        background: #cce5ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🧠 MindAssist AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Agentic Research Assistant for Depression Risk Prediction (FYP Topic)</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Show database status
    st.subheader("📚 Database Status")
    with st.spinner("Checking vector database..."):
        vectordb = get_vector_store()
        if vectordb:
            count = vectordb._collection.count() if hasattr(vectordb, '_collection') else "Unknown"
            st.success(f"✅ Vector DB Active ({count} chunks)")
        else:
            st.warning("⚠️ No vector database found. Add PDFs to data/pdfs/")
    
    # Model information
    st.subheader("🤖 Active Models")
    st.info(f"**Router:** {MODELS['router']} (Groq) - Fast/Free")
    st.info(f"**Reasoning:** {MODELS['reasoning']} (OpenRouter) - Free")
    
    # Agent status
    st.subheader("🔷 Agent Pipeline")
    st.markdown("""
    1. 🎯 **Router** - Intent Classification
    2. 📋 **Orchestrator** - Task Planning
    3. 🔍 **Research Agent** - RAG Retrieval (Tool)
    4. 🌐 **Search Tool** - Web Search (NEW!)
    5. ✅ **Reflection Agent** - Validation
    """)
    
    # Clear cache button
    if st.button("🔄 Clear Cache & Reload"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Ask Your Research Question")
    
    # Query input
    user_query = st.text_area(
        "Enter your question about depression, mental health, or research papers:",
        height=100,
        placeholder="e.g., What are the latest machine learning techniques for predicting depression using PHQ-9?"
    )
    
    # Example queries - UPDATED with web search examples
    with st.expander("💡 Example Queries"):
        st.markdown("**📚 RAG / Knowledge Base Queries:**")
        example_queries_rag = [
            "Explain PHQ-9 scoring and interpretation",
            "What is the prevalence of depression in Sri Lanka?",
            "How does DASS-21 differ from PHQ-9?",
            "What is the Beck Depression Inventory?"
        ]
        for q in example_queries_rag:
            if st.button(q, key=f"rag_{q[:15]}"):
                user_query = q
                st.rerun()
        
        st.markdown("**🌐 Web Search Queries (Real-time):**")
        example_queries_web = [
            "Latest depression research 2024",
            "Recent AI breakthroughs in mental health",
            "Current mental health statistics worldwide",
            "New treatments for depression 2024"
        ]
        for q in example_queries_web:
            if st.button(q, key=f"web_{q[:15]}"):
                user_query = q
                st.rerun()
    
    # Run button
    run_button = st.button("🚀 Run Agentic Workflow", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 System Status")
    status_placeholder = st.empty()

# Main processing
if run_button and user_query:
    with st.spinner("🧠 Agents are processing your query..."):
        try:
            # --- Step 1: Router Agent (Groq - Fast) ---
            status_placeholder.info("🔄 Step 1: Router Agent (Llama 3.1 - Groq)")
            intent_data = route_query(user_query)
            
            if "error" in intent_data:
                st.error(f"❌ Router error: {intent_data['error']}")
                st.stop()
            
            intent = intent_data.get("intent", "literature_search")
            confidence = intent_data.get("confidence", 0.5)
            
            st.info(f"📌 **Intent:** {intent.upper()} (Confidence: {confidence:.2f})")
            
            # --- Step 2: Orchestrator (Planning) ---
            status_placeholder.info("📋 Step 2: Orchestrator - Planning tasks")
            orchestrator = Orchestrator(user_query, intent)
            plan = orchestrator.create_plan()
            
            # Show plan
            with st.expander("📋 Task Decomposition Plan"):
                for step in plan:
                    st.write(f"**Step {step['step']}:** {step['task']} → {step['worker']}")
                    st.json(step['params'])
            
            # --- Step 3: Execute based on intent ---
            if intent == "web_search":
                # Use Web Search
                status_placeholder.info("🌐 Step 3: Search Tool - Searching the web")
                search_tool = SearchTool()
                
                # Orchestrator sends message to SearchTool
                task_msg = orchestrator.send_message(
                    "SearchTool",
                    {"query": user_query}
                )
                
                rag_result = search_tool.execute_task(task_msg)
                
                # Show web search results
                with st.expander("🌐 Web Search Results"):
                    if rag_result.get("status") == "success":
                        chunks = rag_result.get("retrieved_chunks", [])
                        if chunks:
                            for i, chunk in enumerate(chunks[:5]):
                                st.write(f"**Result {i+1}** (Score: {chunk.get('relevance_score', 'N/A')})")
                                st.write(f"**Title:** {chunk.get('title', 'Unknown')}")
                                st.write(f"**Link:** {chunk.get('link', '#')}")
                                st.caption(chunk.get('snippet', '')[:300] + "...")
                                st.divider()
                        else:
                            st.warning("No web results found.")
                    else:
                        st.error(rag_result.get("error", "Unknown error"))
            else:
                # Use RAG
                status_placeholder.info("🔍 Step 3: Research Agent - Retrieving from RAG")
                research_agent = ResearchAgent()
                
                # Orchestrator sends message to Research Agent
                task_msg = orchestrator.send_message(
                    "ResearchAgent",
                    {"task": "rag_search", "query": user_query, "k": 5}
                )
                
                rag_result = research_agent.execute_task(task_msg)
                
                # Show retrieval results
                with st.expander("📚 Retrieved RAG Chunks"):
                    if rag_result.get("status") == "success":
                        chunks = rag_result.get("retrieved_chunks", [])
                        if chunks:
                            for i, chunk in enumerate(chunks[:3]):
                                st.write(f"**Chunk {i+1}** (Score: {chunk.get('relevance_score', 'N/A')})")
                                st.write(f"Source: {chunk.get('source', 'Unknown')}")
                                st.caption(chunk.get('content', '')[:300] + "...")
                                st.divider()
                        else:
                            st.warning("No chunks retrieved.")
                    else:
                        st.error(rag_result.get("error", "Unknown error"))
            
            # --- Step 4: Reflection Agent (Free Model) ---
            status_placeholder.info(f"✅ Step 4: Reflection Agent ({MODELS['reasoning']})")
            reflection_agent = ReflectionAgent()
            final_result = reflection_agent.reflect_and_synthesize(user_query, rag_result)
            
            # --- Step 5: Final Output ---
            status_placeholder.success("✅ Workflow Complete!")
            
            st.markdown("---")
            st.markdown("### 🎯 Final Answer (Validated by Reflection Agent)")
            
            # Display final answer in appropriate box
            if final_result.get("is_valid", False):
                st.markdown(f"""
                <div class="final-answer">
                    <p style="font-size: 1.1rem;">{final_result.get('final_answer', 'No answer generated.')}</p>
                    <p style="font-size: 0.8rem; color: #666; margin-top: 10px;">
                        ✅ Validated | Sources used: {len(final_result.get('sources_used', []))}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Check if this is a web search response
                if "web search" in str(final_result.get('final_answer', '')).lower():
                    st.markdown(f"""
                    <div class="web-search-box">
                        <p style="font-size: 1.1rem;">{final_result.get('final_answer', 'Could not generate answer.')}</p>
                        <p style="font-size: 0.8rem; color: #004085; margin-top: 5px;">
                            🌐 Retrieved from web search | {final_result.get('reflection_note', '')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="warning-box">
                        <p>⚠️ {final_result.get('final_answer', 'Could not generate answer.')}</p>
                        <p style="font-size: 0.8rem; color: #856404; margin-top: 5px;">
                            {final_result.get('reflection_note', 'Reflection agent flagged this response.')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show complete agent communication
            with st.expander("📨 Agent-to-Agent Communication Log"):
                st.json(orchestrator.state["messages"])
                st.json(orchestrator.state["execution_results"])
            
        except Exception as e:
            st.error(f"❌ System Error: {str(e)}")
            st.info("💡 Please check your API keys in `.streamlit/secrets.toml` and ensure PDFs are in `data/pdfs/`.")
            st.stop()

elif run_button and not user_query:
    st.warning("⚠️ Please enter a query before running.")

# Footer
st.markdown("---")
st.caption("MindAssist AI | FYP: Depression Risk Prediction | Agentic AI Assignment | Created By Wesly Jeyananthan Abisha")#   S t r e a m l i t   U I   F e a t u r e   B r a n c h  
 