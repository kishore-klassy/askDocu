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
    try:
        with st.spinner("Crawling and indexing the help site..."):
            docs = crawl_help_site(st.session_state["help_url"])
            if not docs:
                st.error("No documentation found. Please check the URL and try again.")
                return
            vector_store = create_or_load_vector_store(docs)
            st.session_state.qa_engine = QAEngine(vector_store)
            st.success(f"Agent is ready! Indexed {len(docs)} pages. Start chatting.")
    except ValueError as e:
        st.error(f"Configuration error: {str(e)}")
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.session_state.qa_engine = None

# Sidebar setup
st.sidebar.title("🧠 Help Site Configuration")
st.sidebar.markdown("Enter a base URL to crawl and ask questions.")

help_url_input = st.sidebar.text_input("Help Website URL", placeholder="https://example.com/help")

if st.sidebar.button("🔍 Start Crawling"):
    if help_url_input and help_url_input.strip():
        # Basic URL validation
        if not (help_url_input.startswith('http://') or help_url_input.startswith('https://')):
            st.sidebar.error("Please enter a valid URL starting with http:// or https://")
        else:
            st.session_state["help_url"] = help_url_input.strip()
            initialize_agent()
    else:
        st.sidebar.error("Please enter a valid URL.")

# Main UI
st.title("🤖 AI Helpdesk Assistant")
st.markdown("Ask questions based on the help documentation crawled from the provided URL.")

if st.session_state.qa_engine:
    user_input = st.text_input("💬 Ask your question:", placeholder="Type your question here...", key="user_input")
    if st.button("Send"):
        if user_input and user_input.strip():
            # Display user message
            st.session_state.messages.append({"role": "user", "text": user_input.strip()})

            try:
                # Get the answer
                answer, sources = st.session_state.qa_engine.answer_question(user_input.strip())

                source_str = ""
                if sources:
                    source_str = "\n\n📚 **Sources:**\n" + "\n".join(f"- [{src}]({src})" for src in sources)

                full_response = answer + source_str
                st.session_state.messages.append({"role": "bot", "text": full_response})
            except Exception as e:
                error_msg = f"Error processing your question: {str(e)}"
                st.session_state.messages.append({"role": "bot", "text": error_msg})
                st.error(error_msg)
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
