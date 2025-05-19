import streamlit as st
from modules.crawler import crawl_help_site
from modules.vector_store import create_or_load_vector_store
from modules.qa_engine import QAEngine
from streamlit_chat import message

st.set_page_config(page_title="AI Helpdesk Agent", page_icon="🤖", layout="wide")

# Session states for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_engine" not in st.session_state:
    st.session_state.qa_engine = None

def initialize_agent():
    with st.spinner("Crawling and indexing the help site..."):
        docs = crawl_help_site(st.session_state["help_url"])
        if not docs:
            st.error("No documentation found.")
            return
        vector_store = create_or_load_vector_store(docs)
        st.session_state.qa_engine = QAEngine(vector_store)
        st.success("Agent is ready! Start chatting.")

# Sidebar setup
st.sidebar.title("🧠 Help Site Configuration")
st.sidebar.markdown("Enter a base URL to crawl and ask questions.")

help_url_input = st.sidebar.text_input("Help Website URL", placeholder="https://example.com/help")

if st.sidebar.button("🔍 Start Crawling"):
    if help_url_input:
        st.session_state["help_url"] = help_url_input
        initialize_agent()
    else:
        st.sidebar.error("Please enter a valid URL.")

# Main UI
st.title("🤖 AI Helpdesk Assistant")
st.markdown("Ask questions based on the help documentation crawled from the provided URL.")

if st.session_state.qa_engine:
    user_input = st.text_input("💬 Ask your question:", placeholder="Type your question here...", key="user_input")
    if st.button("Send"):
        if user_input:
            # Display user message
            st.session_state.messages.append({"role": "user", "text": user_input})

            # Get the answer
            answer, sources = st.session_state.qa_engine.answer_question(user_input)

            source_str = ""
            if sources:
                source_str = "\n\n📚 **Sources:**\n" + "\n".join(f"- [{src}]({src})" for src in sources)

            full_response = answer + source_str
            st.session_state.messages.append({"role": "bot", "text": full_response})
        else:
            st.warning("Please type a question.")

    # Chat history rendering
    for i, msg in enumerate(st.session_state.messages):
        is_user = msg["role"] == "user"
        message(
            msg["text"],
            is_user=is_user,
            key=str(i),
            avatar_style="thumbs" if is_user else "bottts",
            seed="user" if is_user else "bot"
        )
else:
    st.info("Please crawl a help site to activate the assistant.")
