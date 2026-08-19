"""
⚡ NOVA – Smart Action Agent
"Ask. Decide. Act."
Fresh, Clean, High-Contrast Lemon-Yellow UI with High Readability.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from agent import NovaAgent, TOOL_DISPLAY_NAMES

# Load environment variables from .env
load_dotenv(override=True)

# Page Setup — Full width, no sidebar
st.set_page_config(
    page_title="NOVA ⚡ Smart Action Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# High-Contrast Lemon Yellow Theme CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    /* Hide sidebar completely */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Lemon Yellow Canvas & Global Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FEF9C3 !important; /* Fresh Lemon Yellow */
        color: #0F172A !important;
    }

    code, pre, .mono-badge {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Limit for clean centered layout */
    .block-container {
        max-width: 960px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #FEF08A 0%, #FEF9C3 50%, #FFFFFF 100%);
        border: 2px solid #FDE047;
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 6px 24px rgba(202, 138, 4, 0.08);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #4338CA 0%, #D97706 50%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .hero-tagline {
        font-size: 1rem;
        font-weight: 700;
        color: #A16207;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .hero-desc {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 14px;
    }

    /* Friendly Status Pills */
    .status-ribbon {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
    }
    .cute-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: #FFFFFF;
        border: 1.5px solid #FDE047;
        color: #713F12;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .cute-pill.green {
        background: #ECFDF5;
        border-color: #A7F3D0;
        color: #047857;
    }
    .cute-pill.amber {
        background: #FEF3C7;
        border-color: #FCD34D;
        color: #92400E;
    }

    /* Cute Tool Cards on Lemon Canvas */
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }
    .tool-card-box {
        background: #FFFFFF;
        border: 1.5px solid #FEF08A;
        border-radius: 16px;
        padding: 14px 16px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 10px rgba(234, 179, 8, 0.05);
    }
    .tool-card-box:hover {
        border-color: #EAB308;
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(234, 179, 8, 0.15);
    }
    .tool-card-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #0F172A;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .tool-card-desc {
        font-size: 0.8rem;
        color: #475569;
        line-height: 1.35;
    }

    /* Agent Activity Card */
    .activity-card {
        background: #FEFCE8;
        border: 1.5px solid #FDE047;
        border-left: 5px solid #EAB308;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(234, 179, 8, 0.08);
    }
    .activity-title {
        font-weight: 700;
        font-size: 0.78rem;
        color: #A16207;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .activity-badge-group {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    .badge-item {
        background: #FFFFFF;
        border: 1px solid #FDE047;
        color: #854D0E;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 3px 10px;
        border-radius: 6px;
    }
    .badge-warn {
        background: #FFF1F2;
        border-color: #FECDD3;
        color: #9F1239;
    }

    /* Buttons Styling */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        border: 1.5px solid #FDE047 !important;
        background: #FFFFFF !important;
        color: #713F12 !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 4px rgba(234, 179, 8, 0.08) !important;
    }
    div.stButton > button:hover {
        border-color: #EAB308 !important;
        color: #854D0E !important;
        background: #FEF08A !important;
        transform: translateY(-1px) !important;
    }

    /* =======================================================
       CRITICAL FIX: High-Contrast Dark Text in Chat Bubbles
       ======================================================= */
    div[data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #FEF08A !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03) !important;
    }
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] span, 
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3,
    div[data-testid="stChatMessage"] h4,
    div[data-testid="stChatMessage"] strong,
    div[data-testid="stChatMessage"] em,
    div[data-testid="stChatMessage"] .stMarkdown {
        color: #0F172A !important; /* Bold, solid readable dark slate */
    }
    div[data-testid="stChatMessage"] code {
        color: #92400E !important;
        background-color: #FEF3C7 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }

    /* Expander text color inside chat */
    .streamlit-expanderHeader, [data-testid="stExpander"] * {
        color: #334155 !important;
    }

    /* =======================================================
       CRITICAL FIX: Chat Input Background & Text Visibility
       ======================================================= */
    div[data-testid="stBottom"],
    div[data-testid="stBottomBlockContainer"],
    .stBottomBlockContainer,
    footer {
        background-color: #FEF9C3 !important; /* Lemon yellow bottom canvas */
    }
    header[data-testid="stHeader"] {
        background-color: #FEF9C3 !important;
    }
    
    /* Outer Box */
    div[data-testid="stChatInput"],
    div[data-testid="stChatInput"] > div,
    div[data-testid="stChatInput"] > div > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    .stChatInput,
    .stChatInput > div {
        background-color: #FFFFFF !important; /* Force pure white background */
        border: 2px solid #FDE047 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 16px rgba(202, 138, 4, 0.12) !important;
    }

    div[data-testid="stChatInput"]:focus-within,
    div[data-baseweb="base-input"]:focus-within {
        border-color: #EAB308 !important;
        box-shadow: 0 4px 20px rgba(202, 138, 4, 0.25) !important;
    }

    /* Inner Textarea / Typed text */
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] input,
    div[data-baseweb="base-input"] textarea,
    div[data-baseweb="base-input"] input,
    .stChatInput textarea,
    .stChatInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important; /* Solid readable dark text */
        -webkit-text-fill-color: #0F172A !important;
        caret-color: #0F172A !important; /* Dark cursor */
        font-size: 0.98rem !important;
        font-weight: 600 !important;
    }

    /* Placeholder text */
    div[data-testid="stChatInput"] textarea::placeholder,
    div[data-testid="stChatInput"] input::placeholder,
    .stChatInput textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
        font-weight: 400 !important;
    }

    /* Send arrow button */
    div[data-testid="stChatInput"] button {
        background-color: #FEF08A !important;
        color: #854D0E !important;
        border: 1px solid #FDE047 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] button:hover {
        background-color: #FDE047 !important;
        color: #713F12 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Top Navigation Bar (Clean & Compact)
top_col1, top_col2, top_col3 = st.columns([3, 1.5, 1])

with top_col1:
    st.markdown("### ⚡ **NOVA** <span style='font-size: 0.9rem; color: #A16207; font-weight: 600;'>Smart Action Agent</span>", unsafe_allow_html=True)

with top_col2:
    selected_model = st.selectbox(
        "Model",
        options=["gemini-3.5-flash-lite", "gemini-3.7-flash"],
        index=0,
        label_visibility="collapsed",
    )

with top_col3:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

# Action Agent Hero Banner
st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-title">⚡ NOVA ✨ Smart Action Agent</div>
        <div class="hero-tagline">"Ask. Decide. Act."</div>
        <div class="hero-desc">
            An intelligent AI action agent powered by Google Gemini. Give any natural-language request — NOVA evaluates tool requirements, executes real Python code in the background, and gives you clear, grounded answers!
        </div>
        <div class="status-ribbon">
            <span class="cute-pill green">🟢 Status: Online & Ready</span>
            <span class="cute-pill amber">⚡ Engine: {selected_model}</span>
            <span class="cute-pill">🛡️ Safe AST Sandbox</span>
            <span class="cute-pill">🧪 22/22 Tests Passing</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4 Cute Tool Cards
st.markdown(
    """
    <div class="cards-grid">
        <div class="tool-card-box">
            <div class="tool-card-title">🧮 Math Wizard</div>
            <div class="tool-card-desc">Safely calculates math, percentages & algebraic expressions via AST.</div>
        </div>
        <div class="tool-card-box">
            <div class="tool-card-title">🌤️ Sky Radar</div>
            <div class="tool-card-desc">Live weather forecasts & temperature around the globe via Open-Meteo.</div>
        </div>
        <div class="tool-card-box">
            <div class="tool-card-title">📝 Word Craft</div>
            <div class="tool-card-desc">Word & character counting, case changes, and text flipping.</div>
        </div>
        <div class="tool-card-box">
            <div class="tool-card-title">🐙 Repo Explorer</div>
            <div class="tool-card-desc">Live GitHub public repository stars, forks, language & metadata.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Quick Demo Prompts
st.markdown("##### 🚀 **Try a Demo Prompt:**")
prompt_cols = st.columns(4)

with prompt_cols[0]:
    if st.button("🌤️ Weather in Mumbai", use_container_width=True):
        st.session_state.pending_prompt = "What's the weather in Mumbai right now?"
        st.rerun()

with prompt_cols[1]:
    if st.button("🧮 25% of 840", use_container_width=True):
        st.session_state.pending_prompt = "Calculate 25% of 840"
        st.rerun()

with prompt_cols[2]:
    if st.button("📝 Word Counter", use_container_width=True):
        st.session_state.pending_prompt = "Count the words in this sentence and reverse the word Python"
        st.rerun()

with prompt_cols[3]:
    if st.button("🐙 google/gemini-api", use_container_width=True):
        st.session_state.pending_prompt = "Tell me about google/gemini-api repository stats"
        st.rerun()

# Edge Cases Expander
with st.expander("🧪 **Test Edge Cases (Graceful Error Handling)**", expanded=False):
    edge_cols = st.columns(3)
    with edge_cols[0]:
        if st.button("⚠️ Division by Zero (10 / 0)", use_container_width=True):
            st.session_state.pending_prompt = "Calculate 10 / 0"
            st.rerun()
    with edge_cols[1]:
        if st.button("⚠️ Unknown City Lookup", use_container_width=True):
            st.session_state.pending_prompt = "What is the weather in xyzabcunknowncity?"
            st.rerun()
    with edge_cols[2]:
        if st.button("⚠️ Nonexistent GitHub Repo", use_container_width=True):
            st.session_state.pending_prompt = "Tell me about abcxyz/not-a-real-repository"
            st.rerun()

st.divider()

# Chat Log
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="⚡"):
            tool_used = message.get("tool_used")
            status = message.get("status", "Completed")

            if tool_used:
                tool_display = message.get("tool_display_name", tool_used)
                is_ok = status == "Completed"
                badge_class = "badge-item" if is_ok else "badge-item badge-warn"
                status_text = "✓ Completed (200 OK)" if is_ok else "⚠️ Handled Exception"

                st.markdown(
                    f"""
                    <div class="activity-card">
                        <div class="activity-title">⚙️ Agent Activity</div>
                        <div class="activity-badge-group">
                            <span class="{badge_class}"><b>Tool Selected:</b> {tool_display}</span>
                            <span class="{badge_class}"><b>Status:</b> {status_text}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                tool_result = message.get("tool_result")
                tool_args = message.get("tool_args")
                if tool_result is not None:
                    with st.expander("🔍 View Raw Tool Execution Data", expanded=False):
                        if tool_args:
                            st.markdown(f"**Arguments passed:** `{tool_args}`")
                        st.json(tool_result)

            st.markdown(message["content"])

# User Chat Input
user_input = st.chat_input("Ask NOVA anything (e.g., 'What is 45 * 8?', 'Weather in Tokyo', 'Reverse Python')...")

active_prompt = None
if st.session_state.pending_prompt:
    active_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif user_input:
    active_prompt = user_input

if active_prompt:
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(active_prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("🤖 NOVA is thinking and executing tool..."):
            agent = NovaAgent(model=selected_model)
            agent_result = agent.run(
                user_message=active_prompt,
                conversation_history=st.session_state.messages[:-1],
            )

        tool_used = agent_result.get("tool_used")
        tool_display = agent_result.get("tool_display_name")
        tool_args = agent_result.get("tool_args")
        tool_result = agent_result.get("tool_result")
        status = agent_result.get("status", "Completed")
        final_text = agent_result.get("response", "")

        if tool_used:
            is_ok = status == "Completed"
            badge_class = "badge-item" if is_ok else "badge-item badge-warn"
            status_text = "✓ Completed (200 OK)" if is_ok else "⚠️ Handled Exception"

            st.markdown(
                f"""
                <div class="activity-card">
                    <div class="activity-title">⚙️ Agent Activity</div>
                    <div class="activity-badge-group">
                        <span class="{badge_class}"><b>Tool Selected:</b> {tool_display}</span>
                        <span class="{badge_class}"><b>Status:</b> {status_text}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if tool_result is not None:
                with st.expander("🔍 View Raw Tool Execution Data", expanded=False):
                    if tool_args:
                        st.markdown(f"**Arguments passed:** `{tool_args}`")
                    st.json(tool_result)

        st.markdown(final_text)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_text,
                "tool_used": tool_used,
                "tool_display_name": tool_display,
                "tool_args": tool_args,
                "tool_result": tool_result,
                "status": status,
            }
        )
