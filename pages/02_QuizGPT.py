import json
import streamlit as st

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.retrievers import WikipediaRetriever

from components.get_file import split_file
from components.format_docs import format_docs
from components.check_api_key import get_api_key, is_api_key_valid


st.set_page_config(
    page_title="QuizGPT",
    page_icon="❓",
)

st.title("QuizGPT")


questions_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a helpful assistant that is role playing as a teacher.
         
    Based ONLY on the following context make 10 (TEN) questions to test the user's knowledge about the text.
    
    Each question should have 4 answers, three of them must be incorrect and one must be correct.

    The user has chosen the difficulty level as given below.

    For **easy** difficulty, provide simple, straightforward questions. 
    For **hard** difficulty, provide challenging questions that require deeper knowledge.
         
    Use (o) to signal the correct answer.
         
    Easy Question examples:
         
    Question: What is the output of the following python code: `print(2 + 3)`?
    Answers: 23|6|9|5(o)
         
    Question: Which of the following is a data type in Python?
    Answers: Car|Tuple(o)|House|Button

    Hard Question examples:
         
    Question: Which Python module is used to create a server-side socket connection that accepts multiple clients?
    Answers: socket|socket|asyncio(o)|http.server
         
    Question: Which of the following Python functions is used to return the memory address of an object?
    Answers: id(o)|hash|memoryview|getattr
         
    After making questions and answers, format them into JSON format.

    Example Output:
     
    ```json
    {{ "questions": [
            {{
                "question": "What is the output of the following python code: `print(2 + 3)`?",
                "answers": [
                        {{
                            "answer": "23",
                            "correct": false
                        }},
                        {{
                            "answer": "6",
                            "correct": false
                        }},
                        {{
                            "answer": "9",
                            "correct": false
                        }},
                        {{
                            "answer": "5",
                            "correct": true
                        }},
                ]
            }},
                        {{
                "question": "Which of the following is a data type in Python?",
                "answers": [
                        {{
                            "answer": "Car",
                            "correct": false
                        }},
                        {{
                            "answer": "Tuple",
                            "correct": true
                        }},
                        {{
                            "answer": "House",
                            "correct": false
                        }},
                        {{
                            "answer": "Button",
                            "correct": false
                        }},
                ]
            }},
        ]
     }}
    ```
    
    Your turn!
         
    Context: {context}
    Difficulty: {difficulty}
""",
        )
    ]
)


function = {
    "name": "create_quiz",
    "description": "function that takes a list of 10 questions and answers and returns a quiz",
    "parameters": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                        },
                        "answers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "answer": {
                                        "type": "string",
                                    },
                                    "correct": {
                                        "type": "boolean",
                                    },
                                },
                                "required": ["answer", "correct"],
                            },
                        },
                    },
                    "required": ["question", "answers"],
                },
            }
        },
        "required": ["questions"],
    },
}


@st.cache_data(show_spinner="Making Quiz...")
def run_quiz_chain(_docs, difficulty, topic):
    chain = questions_prompt | llm
    response = chain.invoke({"context": format_docs(_docs), "difficulty": difficulty})
    response = response.additional_kwargs["function_call"]["arguments"]
    return json.loads(response)["questions"]


@st.cache_data(show_spinner="Searching Wikipedia...")
def wiki_search(term):
    retriever = WikipediaRetriever(top_k_results=5)
    docs = retriever.get_relevant_documents(term)
    return docs


def get_docs():
    choice = st.selectbox(
        "Choose what you want to use.",
        (
            "File",
            "Wikipidia Article",
        ),
    )
    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx, .txt or .pdf file",
            type=["pdf", "txt", "docx"],
        )
        if file:
            docs = split_file(file, "quiz_files")
            return docs
    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            docs = wiki_search(topic)
            return docs


with st.sidebar:
    docs = None
    topic = None
    choice = None
    difficulty = None
    API_KEY = get_api_key()
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)
        if is_valid:
            choice = st.selectbox(
                "Choose what you want to use.",
                (
                    "File",
                    "Wikipedia Article",
                ),
            )
            if choice == "File":
                file = st.file_uploader(
                    "Upload a .docx, .txt or .pdf file",
                    type=["pdf", "txt", "docx"],
                )
                if file:
                    docs = split_file(file, "quiz_files")
            else:
                topic = st.text_input("Search Wikipedia...")
                if topic:
                    docs = wiki_search(topic)
    if docs:
        difficulty = st.selectbox(
            "Choose the difficulty for the quiz.",
            (
                "Easy",
                "Hard",
            ),
        )
        start = st.button("Generate Quiz")
        if start:
            st.session_state["quiz_start"] = True

    st.link_button(
        "Go to Github Repo",
        "https://github.com/seedjin298/gpt-Challenge/blob/main/pages/02_QuizGPT.py",
    )


llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-3.5-turbo-1106",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    api_key=API_KEY,
).bind(
    function_call={
        "name": "create_quiz",
    },
    functions=[
        function,
    ],
)

if "correct_count" not in st.session_state:
    st.session_state["correct_count"] = 0

if "quiz_start" not in st.session_state:
    st.session_state["quiz_start"] = False


if not st.session_state["quiz_start"]:
    st.markdown(
        """
    Welcome to QuizGPT.
                
    I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
                
    Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    response = run_quiz_chain(docs, difficulty, topic if topic else file.name)

    with st.form("questions_form"):
        for num, question in enumerate(response):
            st.write(question["question"])
            value = st.radio(
                "Select an option.",
                [answer["answer"] for answer in question["answers"]],
                index=None,
                key=num,
                disabled=(st.session_state["correct_count"] == 10),
            )
            if {"answer": value, "correct": True} in question["answers"]:
                st.success(f"Correct! {value} is the Answer!")
                st.session_state["correct_count"] += 1
            elif value is not None:
                st.error(f"Wrong, {value} is not the Answer")

        button = st.form_submit_button(
            "Submit Quiz",
            disabled=(st.session_state["correct_count"] == 10),
        )

        if button and st.session_state["correct_count"] != 10:
            st.header(f"Your score is: {st.session_state['correct_count']}/10")
            st.subheader("Correct the Wrong Answers and Submit Again")
            st.session_state["correct_count"] = 0
    if st.session_state["correct_count"] == 10:
        st.session_state["correct_count"] = 0
        st.session_state["quiz_start"] = False
        st.balloons()
        st.header("Congratulation! You Finished the Quiz!")
        st.subheader("Upload New File or Search New Keyword for Next Quiz!")
