import openai.error
import streamlit as st
import openai

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

from components.get_file import embed_file
from components.format_docs import format_docs
from components.check_api_key import get_api_key, is_api_key_valid

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
)


class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)


def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.
            
            Context: {context}
            """,
        ),
        ("human", "{question}"),
    ]
)


st.title("Streamlit is 🔥")

st.markdown(
    """
    Welcome!
                
    Use this chatbot to ask questions to an AI about your files!

    Upload your files and API key on the sidebar.
"""
)

with st.sidebar:
    is_file = False
    API_KEY = get_api_key()
    is_valid = is_api_key_valid(API_KEY)
    if API_KEY:
        if is_valid:
            file = st.file_uploader(
                "Upload a .txt .pdf or .docx file",
                type=["pdf", "txt", "docx"],
                disabled=not is_valid,
            )
            if file:
                is_file = True

    st.link_button(
        "Go to Github Repo",
        "https://github.com/seedjin298/gpt-Challenge/blob/main/app.py",
    )

if is_file:
    retriever = embed_file(file, "files", API_KEY)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    message = st.chat_input("Ask anything about your file...")
    if message:
        send_message(message, "human")
        chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | ChatOpenAI(
                temperature=0.1,
                streaming=True,
                callbacks=[
                    ChatCallbackHandler(),
                ],
                openai_api_key=API_KEY,
            )
        )
        with st.chat_message("ai"):
            chain.invoke(message)
else:
    st.session_state["messages"] = []
