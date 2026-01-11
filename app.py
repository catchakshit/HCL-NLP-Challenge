import streamlit as st
from rag import answer_question
from agent import get_agent_response
import fitz
import json
import os

# ---------- Page Config ----------
st.set_page_config(
    page_title="HCL Copilot",
    layout="wide"
)

# ---------- Custom CSS (Notion-style Enterprise) ----------
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #0E1117;
    color: #E5E7EB;
}

/* Global text */
html, body {
    color: #E5E7EB;
}

/* Constrain content width */
.block-container {
    max-width: 1200px;
}

/* Headers */
h1 {
    color: #FFFFFF;
    font-weight: 700;
    font-size: 2.1rem;
    margin-bottom: 0.2rem;
}

h2 {
    color: #9CA3AF;
    font-weight: 500;
    font-size: 1.1rem;
}

h3 {
    color: #E5E7EB;
    font-weight: 600;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0B0F14;
    border-right: 1px solid #1F2933;
}

section[data-testid="stSidebar"] * {
    color: #9CA3AF;
}

/* Buttons */
.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 6px;
    border: none;
    padding: 0.4em 1em;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #1D4ED8;
}

/* Inputs */
textarea, input {
    background-color: #020617;
    color: #E5E7EB;
    border-radius: 6px;
    border: 1px solid #1F2933;
}

/* Code blocks */
pre {
    background-color: #020617;
    color: #7DD3FC;
    border-radius: 6px;
    border: 1px solid #1F2933;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #9CA3AF;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF;
    border-bottom: 2px solid #2563EB;
    font-weight: 600;
}

/* Remove boxes */
div[data-testid="stVerticalBlock"] > div {
    background: transparent;
    border: none;
    box-shadow: none;
}

/* Subtle separators */
hr {
    border: 1px solid #1F2933;
}

/* Alerts */
.stAlert {
    background-color: #020617;
    border: 1px solid #1F2933;
}

/* Right panel subtle divider */
div[data-testid="column"]:nth-child(2) {
    border-left: 1px solid #1F2933;
    padding-left: 24px;
}
            
/* Right panel subtle background */
div[data-testid="column"]:nth-child(2) {
    background-color: rgba(255,255,255,0.02);
    padding: 16px;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)



# ---------- Header ----------
col_logo, col_title = st.columns([1, 5])



with col_title:
    st.markdown("# HCL Copilot")
    st.markdown("<div style='color:#9CA3AF; margin-top:-8px; margin-bottom:12px;'>Enterprise AI Assistant for Digital Workplace</div>", unsafe_allow_html=True)
    st.markdown("---")

# ---------- Sidebar ----------
with st.sidebar:
    if os.path.exists("assets/hcl_logo.png"):
        st.image("assets/hcl_logo.png", width=120)
    st.markdown("## HCL Copilot")
    st.markdown("Agentic Enterprise Assistant")

    st.markdown("""
    **Capabilities**
    - Document Question Answering (RAG)
    - Source-grounded answers
    - Agentic planning & action generation
    - IT / HR workflow automation
    """)

    st.markdown("---")

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_action = None
        st.session_state.last_sources = []

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_action" not in st.session_state:
    st.session_state.last_action = None

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "Copilot",
    "Architecture",
    "Demo",
    "About"
])

# =========================
# TAB 1: COPILOT
# =========================
with tab1:
    col_chat, col_side = st.columns([2, 1])

    with col_chat:
        st.markdown("### Conversation")
        if len(st.session_state.messages) == 0:
            st.markdown(
        "<div style='color:#9CA3AF; margin-bottom:20px;'>"
        "Try asking things like:<br>"
        "• What is the revenue growth?<br>"
        "• What are the key risks mentioned?<br>"
        "• I cannot access VPN and Jira"
        "</div>",
        unsafe_allow_html=True
    )


        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

        user_input = st.chat_input("Ask a question or enter a command...")

    with col_side:
        st.markdown("### Agent Output")
    action_box = st.container()

    st.markdown("---")

    st.markdown("### Sources")
    sources_box = st.container()

    st.markdown("---")

    st.markdown("### System Reasoning")
    reasoning_box = st.container()


    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner("Processing request..."):
            agent_result = get_agent_response(user_input)

            if agent_result.get("type") == "plan_and_act":
                plan = agent_result.get("plan", [])
                actions = agent_result.get("actions", [])

                assistant_text = "The system has generated a plan and the corresponding actions."

                st.session_state.messages.append({"role": "assistant", "content": assistant_text})
                st.chat_message("assistant").write(assistant_text)

                reasoning_box.markdown("**Planned Steps:**")
                for i, step in enumerate(plan, 1):
                    reasoning_box.markdown(f"{i}. {step}")

                action_box.code(json.dumps(actions, indent=2), language="json")

                st.session_state.last_action = actions
                st.session_state.last_sources = []

                sources_box.write("—")

                st.download_button(
                    "Download Action JSON",
                    json.dumps(actions, indent=2),
                    file_name="actions.json"
                )

            else:
                answer, pages = answer_question(user_input)

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.chat_message("assistant").write(answer)

                st.session_state.last_action = None
                st.session_state.last_sources = pages

                action_box.write("No action generated for this request.")

                if pages:
                    sources_box.markdown("**Referenced Pages:**")
                    for p in pages:
                        sources_box.markdown(f"- Page {p}")
                else:
                    sources_box.write("No sources available.")

                reasoning_box.info("The system classified this as an information query and used the document knowledge base.")

    # PDF Preview
    if st.session_state.last_sources:
        st.markdown("---")
        st.markdown("### Document Preview")

        try:
            doc = fitz.open("data/hcl.pdf")
            page_num = st.selectbox("Select page to preview:", st.session_state.last_sources)
            page = doc[page_num - 1]
            pix = page.get_pixmap()
            st.image(pix.tobytes("png"))
        except:
            st.warning("Unable to load document preview.")

# =========================
# TAB 2: ARCHITECTURE
# =========================
with tab2:
    st.markdown("### System Architecture")

    st.markdown("""
    **High-Level Flow**

    1. User submits a query in the Copilot interface  
    2. The system classifies it as:
       - Information query, or  
       - Action command  

    **For Information Queries:**
    - Relevant content is retrieved from the vector database  
    - The LLM generates an answer using only retrieved context  
    - Source pages are shown as citations  

    **For Action Commands:**
    - The agent creates a step-by-step plan  
    - The plan is converted into structured JSON actions  
    """)

    st.markdown("### Components")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("""
        **Frontend**
        - Streamlit Web Application

        **AI Layer**
        - Groq LLM (LLaMA 3.1)
        - LangChain Orchestration
        """)

    with colB:
        st.markdown("""
        **Knowledge Layer**
        - HCL Annual Report PDF
        - BGE Embeddings
        - FAISS Vector Database

        **Agent Layer**
        - Planning Module
        - Function Calling (JSON)
        """)

# =========================
# TAB 3: DEMO
# =========================
with tab3:
    st.markdown("### Demo Scenarios")

    demo_questions = [
        "What is the revenue growth?",
        "What are the key risks mentioned?",
        "What is the company strategy?",
        "Schedule a meeting with HR tomorrow at 3pm",
        "I cannot access VPN and Jira"
    ]

    for q in demo_questions:
        if st.button(q):
            st.session_state.messages.append({"role": "user", "content": q})
            st.experimental_rerun()

# =========================
# TAB 4: ABOUT
# =========================
with tab4:
    st.markdown("### About HCL Copilot")

    st.markdown("""
    **HCL Copilot** is an Agentic Enterprise Assistant built for the HCLTech NLP Challenge.

    **Key Features**
    - Retrieval-Augmented Generation (RAG)
    - Source-grounded document Q&A
    - Agentic planning and action generation
    - Enterprise workflow automation simulation

    **Technology Stack**
    - Python, Streamlit
    - LangChain
    - Groq LLM
    - FAISS Vector Database
    - HuggingFace Embeddings
    - PyMuPDF
    """)
