import streamlit as st

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.chat_models import ChatOpenAI

from components.get_file import embed_file
from components.format_docs import format_docs
from components.check_api_key import get_api_key, is_api_key_valid
from components.chatbot import ChatCallbackHandler, send_message, paint_history

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
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
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)
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
