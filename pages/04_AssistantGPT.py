import streamlit as st
import time

from components.check_api_key import get_api_key, is_api_key_valid
from components.chatbot import send_message, paint_history
from components.assistant_tools import make_assistant
from components.assistant import (
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
    result = get_assistant_messages(thread_id, question)
    send_message(result, "ai")


def check_and_display_answer(question):
    for result in st.session_state["results"]:
        if result["message"] == question:
            is_already_answered = True
            send_message(result["result"], "ai")
            return is_already_answered


with st.sidebar:
    API_KEY = get_api_key()
    is_valid = False
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)

    st.link_button(
        "Go to Github Repo",
        "https://github.com/seedjin298/gpt-Challenge/blob/main/pages/04_AssistantGPT.py",
    )

    option = st.radio(
        "check the file for revealing code",
        ("04_AssistantGPT.py", "assistant_tools.py", "assistant.py"),
    )

    if option == "04_AssistantGPT.py":
        st.markdown(
            """
    import streamlit as st
import time

from components.check_api_key import get_api_key, is_api_key_valid
from components.chatbot import send_message, paint_history
from components.assistant_tools import make_assistant
from components.assistant import (
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
    result = get_assistant_messages(thread_id, question)
    send_message(result, 'ai')


def check_and_display_answer(question):
    for result in st.session_state['results']:
        if result['message'] == question:
            is_already_answered = True
            send_message(result['result'], 'ai')
            return is_already_answered


with st.sidebar:
    API_KEY = get_api_key()
    is_valid = False
    if API_KEY:
        is_valid = is_api_key_valid(API_KEY)

    st.link_button(
        'Go to Github Repo',
        'https://github.com/seedjin298/gpt-Challenge/blob/main/pages/04_AssistantGPT.py',
    )

    option = st.radio(
        'check the file for revealing code',
        ('04_AssistantGPT.py', 'assistant_tools.py', 'assistant.py'),
    )

    if option == '04_AssistantGPT.py':
        st.markdown('
    
')

st.markdown(
    '     
    Ask questions to the Assistant.
            
    The chatbot gives you answers by using DuckDuckGo and Wikipedia.
    
    Enter your OpenAI API Key to ask questions.
'
)

if is_valid:
    send_message('I'm ready! Ask away!', 'ai', save=False)
    paint_history()
    assistant = make_assistant(API_KEY)
    thread = make_thread()
    question = st.chat_input('Ask anything to your Assistant...')

    if question:
        is_already_answered = False
        send_message(question, 'human')
        is_already_answered = check_and_display_answer(question)
        if not is_already_answered:
            message = send_assistant_messages(thread.id, question)
            run = make_run(assistant.id, thread.id, question)
            run_status = get_run(run.id, thread.id).status
            while run_status != 'completed':
                with st.spinner('Waiting for Assistant to Answer...'):
                    run_status = get_run(run.id, thread.id).status
                    time.sleep(1)
                    if run_status == 'requires_action':
                        while run_status == 'requires_action':
                            submit_tool_outputs(run.id, thread.id)
                            time.sleep(1)
                            run_status = get_run(run.id, thread.id).status

            if run_status == 'completed':
                display_answer(thread.id, question)

else:
    st.session_state['client'] = []
    st.session_state['messages'] = []
    st.session_state['thread'] = []
    st.session_state['runs'] = []
    st.session_state['results'] = []

"""
        )
    if option == "assistant_tools.py":
        st.markdown(
            """
    # from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.utilities import WikipediaAPIWrapper
import openai as client


def make_assistant(api_key):
    client.api_key = api_key
    assistant = client.beta.assistants.create(
        name='Researcher Assistant',
        instructions='You help users do research using DuckDuckGo and Wikipedia.',
        model='gpt-4o',
        tools=functions,
    )
    return assistant


def DuckDuckGoSearchTool(inputs):
    query = inputs['query']
    ddg = DuckDuckGoSearchRun()
    return ddg.run(query)


def WikipediaSearchTool(inputs):
    query = inputs['query']
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.invoke(query)


functions_map = {
    'DuckDuckGoSearchTool': DuckDuckGoSearchTool,
    'WikipediaSearchTool': WikipediaSearchTool,
}


functions = [
    {
        'type': 'function',
        'function': {
            'name': 'DuckDuckGoSearchTool',
            'description': 'Use this tool to search by using DuckDuckGo. It takes a query as an argument.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The query you will search for.Example query: Research about the XZ backdoor',
                    }
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'WikipediaSearchTool',
            'description': 'Use this tool to search by using Wikipedia. It takes a query as an argument.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The query you will search for.Example query: Research about the XZ backdoor',
                    },
                },
                'required': ['query'],
            },
        },
    },
]

"""
        )
    if option == "assistant.py":
        st.markdown(
            """
    import json
import streamlit as st
import openai as client

from components.assistant_tools import functions_map


def make_thread():
    if len(st.session_state['thread']) == 0:
        thread = client.beta.threads.create()
        st.session_state['thread'].append(thread)
        return thread
    else:
        thread = st.session_state['thread'][0]
        return thread


def make_run(assistant_id, thread_id, question):
    for item in st.session_state['runs']:
        if item['message'] == question:
            return item['run']
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    run_object = {
        'message': question,
        'run': run,
    }
    st.session_state['runs'].append(run_object)
    return run


def get_run(run_id, thread_id):
    return client.beta.threads.runs.retrieve(
        run_id=run_id,
        thread_id=thread_id,
    )


def send_assistant_messages(thread_id, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id, role='user', content=content
    )


def get_assistant_messages(thread_id, question):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages)
    messages.reverse()
    results = []
    result_index = 0
    for index, message in enumerate(messages):
        if message.role == 'assistant':
            result_index = index
        result = message.content[0].text.value
        results.append(result)
    st.session_state['results'].append(
        {
            'message': question,
            'result': results[result_index],
        }
    )
    return results[result_index]


def get_tool_outputs(run_id, thread_id):
    run = get_run(run_id, thread_id)
    outputs = []
    for action in run.required_action.submit_tool_outputs.tool_calls:
        action_id = action.id
        function = action.function
        print(f'Calling function: {function.name} with arg {function.arguments}')
        outputs.append(
            {
                'output': functions_map[function.name](json.loads(function.arguments)),
                'tool_call_id': action_id,
            }
        )
    return outputs


def submit_tool_outputs(run_id, thread_id):
    outputs = get_tool_outputs(run_id, thread_id)
    return client.beta.threads.runs.submit_tool_outputs(
        run_id=run_id, thread_id=thread_id, tool_outputs=outputs
    )

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
    assistant = make_assistant(API_KEY)
    thread = make_thread()
    question = st.chat_input("Ask anything to your Assistant...")

    if question:
        is_already_answered = False
        send_message(question, "human")
        is_already_answered = check_and_display_answer(question)
        if not is_already_answered:
            message = send_assistant_messages(thread.id, question)
            run = make_run(assistant.id, thread.id, question)
            run_status = get_run(run.id, thread.id).status
            while run_status != "completed":
                with st.spinner("Waiting for Assistant to Answer..."):
                    run_status = get_run(run.id, thread.id).status
                    time.sleep(1)
                    if run_status == "requires_action":
                        while run_status == "requires_action":
                            submit_tool_outputs(run.id, thread.id)
                            time.sleep(1)
                            run_status = get_run(run.id, thread.id).status

            if run_status == "completed":
                display_answer(thread.id, question)

else:
    st.session_state["client"] = []
    st.session_state["messages"] = []
    st.session_state["thread"] = []
    st.session_state["runs"] = []
    st.session_state["results"] = []
