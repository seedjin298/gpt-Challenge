import streamlit as st

from components.check_api_key import get_api_key, is_api_key_valid
from components.chatbot import send_message, paint_history
from components.assistant import (
    make_client,
    make_thread,
    make_run,
    get_run,
    send_assistant_messages,
    get_assistant_messages,
    submit_tool_outputs,
)

st.set_page_config(
    page_title="OpenAI Assistants",
    page_icon="🖥️",
)

st.title("OpenAI Assistants")


def display_answer(thread_id, question):
    result = get_assistant_messages(client, thread_id, question)
    send_message(result, "ai")


def check_and_display_answer(question):
    for result in st.session_state["results"]:
        if result["message"] == question:
            is_already_answered = True
            send_message(result["result"], "ai")
            return is_already_answered


def check_in_progress(client, run_id, thread_id):
    run_status = get_run(client, run_id, thread_id).status
    while run_status == "in_progress":
        run_status = get_run(client, run_id, thread_id).status
        st.write(f"Status: {run_status}")
    return run_status


with st.sidebar:
    API_KEY = get_api_key()
    is_valid = False
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)

    st.link_button(
        "Go to Github Repo",
        "https://github.com/seedjin298/gpt-Challenge/blob/main/pages/04_AssistantGPT.py",
    )

    on = st.toggle("Show Code")
    if on:
        st.markdown(
            """
    import streamlit as st

from components.check_api_key import get_api_key, is_api_key_valid
from components.chatbot import send_message, paint_history
from components.assistant import (
    make_client,
    make_thread,
    make_run,
    get_run,
    send_assistant_messages,
    get_assistant_messages,
    submit_tool_outputs,
)

st.set_page_config(
    page_title='OpenAI Assistants',
    page_icon='🖥️',
)

st.title('OpenAI Assistants')


def display_answer(thread_id, question):
    result = get_assistant_messages(client, thread_id, question)
    send_message(result, 'ai')


def check_and_display_answer(question):
    for result in st.session_state['results']:
        if result['message'] == question:
            is_already_answered = True
            send_message(result['result'], 'ai')
            return is_already_answered


def check_in_progress(client, run_id, thread_id):
    run_status = get_run(client, run_id, thread_id).status
    while run_status == 'in_progress':
        run_status = get_run(client, run_id, thread_id).status
        # print(f'Status: {run_status}')
    return run_status


with st.sidebar:
    API_KEY = get_api_key()
    is_valid = False
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)

    st.link_button(
        'Go to Github Repo',
        'https://github.com/seedjin298/gpt-Challenge/blob/main/pages/04_AssistantGPT.py',
    )

    on = st.toggle('Show Code')
    if on:
        st.markdown(
            '
    

'
        )

st.markdown(
    '     
    Ask questions to the Assistant.
            
    The chatbot gives you answers by using DuckDuckGo and Wikipedia.
    
    Enter your OpenAI API Key to ask questions.
'
)

if is_valid:
    st.markdown('Started Testing')
    send_message('I'm ready! Ask away!', 'ai', save=False)
    paint_history()
    client = make_client(API_KEY)
    thread = make_thread(client)
    question = st.chat_input('Ask anything to your Assistant...')

    if question:
        is_already_answered = False
        send_message(question, 'human')

        is_already_answered = check_and_display_answer(question)
        if not is_already_answered:
            message = send_assistant_messages(client, thread.id, question)
            run = make_run(client, thread.id, question)

            run_status = check_in_progress(client, run.id, thread.id)
            if run_status == 'requires_action':
                while run_status == 'requires_action':
                    submit_tool_outputs(client, run.id, thread.id)
                    run_status = check_in_progress(client, run.id, thread.id)

            if run_status == 'completed':
                display_answer(thread.id, question)

else:
    st.session_state['messages'] = []
    st.session_state['thread'] = []
    st.session_state['runs'] = []
    st.session_state['results'] = []

"""
        )

st.markdown(
    """     
    Ask questions to the Assistant.
            
    The chatbot gives you answers by using DuckDuckGo and Wikipedia.
    
    Enter your OpenAI API Key to ask questions.
"""
)

if is_valid:
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    client = make_client(API_KEY)
    thread = make_thread(client)
    question = st.chat_input("Ask anything to your Assistant...")

    if question:
        is_already_answered = False
        send_message(question, "human")
        st.write("send message human")
        is_already_answered = check_and_display_answer(question)
        if not is_already_answered:
            st.write("starting assistant")
            message = send_assistant_messages(client, thread.id, question)
            st.write("finish message")
            run = make_run(client, thread.id, question)
            st.write("finish run")
            run_status = check_in_progress(client, run.id, thread.id)
            st.write("finish run_status")
            while run_status != "completed":
                st.write("starting spinner")
                with st.spinner("Waiting for Assistant to answer..."):
                    st.write("inside spinner")
                    if run_status == "requires_action":
                        while run_status == "requires_action":
                            submit_tool_outputs(client, run.id, thread.id)
                            run_status = check_in_progress(client, run.id, thread.id)

            if run_status == "completed":
                display_answer(thread.id, question)

else:
    st.session_state["messages"] = []
    st.session_state["thread"] = []
    st.session_state["runs"] = []
    st.session_state["results"] = []
