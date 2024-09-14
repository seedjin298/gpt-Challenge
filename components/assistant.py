import json
import streamlit as st
from openai import OpenAI

from components.assistant_tools import functions_map

assistant_id = "asst_SWfNqJyYIf3MoSLlsi9ZViJE"


def make_client(api_key):
    client = OpenAI(api_key=api_key)
    return client


def make_thread(client):
    if len(st.session_state["thread"]) == 0:
        thread = client.beta.threads.create()
        st.session_state["thread"].append(thread)
        return thread
    else:
        thread = st.session_state["thread"][0]
        return thread


def make_run(client, thread_id, question):
    for item in st.session_state["runs"]:
        if item["message"] == question:
            return item["run"]
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    run_object = {
        "message": question,
        "run": run,
    }
    st.session_state["runs"].append(run_object)
    return run


def get_run(client, run_id, thread_id):
    return client.beta.threads.runs.retrieve(
        run_id=run_id,
        thread_id=thread_id,
    )


def send_assistant_messages(client, thread_id, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=content
    )


def get_assistant_messages(client, thread_id, question):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages)
    messages.reverse()
    results = []
    result_index = 0
    for index, message in enumerate(messages):
        if message.role == "assistant":
            result_index = index
        result = message.content[0].text.value
        results.append(result)
    st.session_state["results"].append(
        {
            "message": question,
            "result": results[result_index],
        }
    )
    return results[result_index]


def get_tool_outputs(client, run_id, thread_id):
    run = get_run(client, run_id, thread_id)
    outputs = []
    for action in run.required_action.submit_tool_outputs.tool_calls:
        action_id = action.id
        function = action.function
        print(f"Calling function: {function.name} with arg {function.arguments}")
        outputs.append(
            {
                "output": functions_map[function.name](json.loads(function.arguments)),
                "tool_call_id": action_id,
            }
        )
    return outputs


def submit_tool_outputs(client, run_id, thread_id):
    outputs = get_tool_outputs(client, run_id, thread_id)
    return client.beta.threads.runs.submit_tool_outputs(
        run_id=run_id, thread_id=thread_id, tool_outputs=outputs
    )
