import streamlit as st
import logging

from langchain.document_loaders import SitemapLoader
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from fake_useragent import UserAgent

from components.check_api_key import get_api_key, is_api_key_valid
from components.chatbot import ChatCallbackHandler, send_message, paint_history

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# initialize a UserAgent object
ua = UserAgent()

st.set_page_config(
    page_title="SiteGPT",
    page_icon="🖥️",
)

st.title("SiteGPT")

answers_prompt = ChatPromptTemplate.from_template(
    """
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.

    Then, give a score to the answer between 0 and 5.
    If the answer answers the user question the score should be high, else it should be low.
    Make sure to always include the answer's score even if it's 0.
    Context: {context}

    Examples:

    Question: How far away is the moon?
    Answer: The moon is 384,400 km away.
    Score: 5

    Question: How far away is the sun?
    Answer: I don't know
    Score: 0

    Your turn!
    Question: {question}
"""
)


def get_answers(inputs):
    docs = inputs["docs"]
    question = inputs["question"]

    llm.streaming = False
    llm.callbacks = None
    answers_chain = answers_prompt | llm
    return {
        "question": question,
        "answers": [
            {
                "answer": answers_chain.invoke(
                    {
                        "question": question,
                        "context": doc.page_content,
                    }
                ).content,
                "source": doc.metadata["source"],
                "date": doc.metadata["lastmod"],
            }
            for doc in docs
        ],
    }


choose_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Use ONLY the following pre-existing answers to answer the user's question.
            Use only the answer that have the highest score (more helpful) and favor the most recent ones.
            Cite sources and return the sources of the answers as they are, do not change them.
            
            Make sure to line break between answer and source.
            Do not put the date when answering the user's question.

            Answer only one time.

            Answers: {answers}
            """,
        ),
        ("human", "{question}"),
    ]
)


def chooses_answer(inputs):
    print(inputs)
    answers = inputs["answers"]
    question = inputs["question"]

    llm.streaming = True
    llm.callbacks = [ChatCallbackHandler()]
    choose_chain = choose_prompt | llm

    condensed = "\n\n".join(
        f"{answer['answer']}\nSource:{answer['source']}\nDate:{answer['date']}\n"
        for answer in answers
    )
    return choose_chain.invoke(
        {
            "question": question,
            "answers": condensed,
        }
    )


def parse_page(soup):
    print(soup)
    header = soup.find("header")
    footer = soup.find("footer")
    sidebar = soup.find("div", class_="sidebar-content")
    right_sidebar = soup.find("div", class_="right-sidebar astro-67yu43on")
    if header:
        header.decompose()
    if footer:
        footer.decompose()
    if sidebar:
        sidebar.decompose()
    if right_sidebar:
        sidebar.decompose()
    return str(soup.get_text()).replace("\n", "").replace("\t", "")


@st.cache_data(show_spinner="Loading website...")
def load_website(url):
    try:
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000,
            chunk_overlap=200,
        )
        loader = SitemapLoader(
            url,
            filter_urls=[
                r"^(.*\/ai-gateway\/).*",
                r"^(.*\/vectorize\/).*",
                r"^(.*\/worker-ai\/).*",
            ],
            parsing_function=parse_page,
        )
        loader.requests_per_second = 2

        # set a realistic user agent
        loader.headers = {"User-Agent": ua.random}

        docs = loader.load_and_split(text_splitter=splitter)
        logging.debug(f"Loaded documents: {docs}")

        embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
        vector_store = FAISS.from_documents(docs, embeddings)
        return vector_store.as_retriever()
    except Exception as e:
        logging.error(f"Error loading sitemap: {e}")
        return []


def save_history(message, answer):
    st.session_state["history"].append({"question": message, "answer": answer})


def check_history(message):
    histories = st.session_state["history"]
    temp = []
    for history in histories:
        temp.append({"input": history["question"], "output": history["answer"]})
    docs = [
        Document(page_content=f"input:{item['input']}\noutput:{item['output']}")
        for item in temp
    ]
    try:
        vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
        found_docs = vector_store.similarity_search(message)
        candidate = found_docs[0].page_content.split("\n")[1]
        return candidate.replace("output:", "")
    except IndexError:
        return None


with st.sidebar:
    API_KEY = get_api_key()
    is_valid = False
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)

    st.link_button(
        "Go to Github Repo",
        "https://github.com/seedjin298/gpt-Challenge/blob/main/pages/03_SiteGPT.py",
    )

llm = ChatOpenAI(
    temperature=0.1,
    openai_api_key=API_KEY,
)

st.markdown(
    """     
    Ask questions about the content of Cloudflare's documentation.
            
    The chatbot gives you answers about AI Gateway, Cloudflare Vectorize, and Workers AI.
    
    Enter your OpenAI API Key to ask questions.
"""
)

if is_valid:
    xml = "https://developers.cloudflare.com/sitemap-0.xml"
    retriever = load_website(xml)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    message = st.chat_input("Ask anything about Cloudflare...")

    if message:
        send_message(message, "human")
        is_answered = check_history(message)
        if is_answered:
            send_message(is_answered, "ai")
        else:
            chain = (
                {
                    "docs": retriever,
                    "question": RunnablePassthrough(),
                }
                | RunnableLambda(get_answers)
                | RunnableLambda(chooses_answer)
            )
            with st.chat_message("ai"):
                request = chain.invoke(message).content.replace("$", "\$")
                save_history(message, request)

else:
    st.session_state["messages"] = []
    st.session_state["history"] = []
