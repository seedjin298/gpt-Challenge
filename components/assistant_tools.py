# from langchain.tools import DuckDuckGoSearchRun
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.tools import DuckDuckGoSearchResults
from openai import OpenAI


def make_client(api_key):
    client = OpenAI(api_key=api_key)
    return client


def make_assistant(client):
    assistant = client.beta.assistants.create(
        name="Researcher Assistant",
        instructions="You help users do research using DuckDuckGo and Wikipedia.",
        model="gpt-4o",
        tools=functions,
    )
    return assistant


def DuckDuckGoSearchTool(inputs):
    query = inputs["query"]
    ddg = DuckDuckGoSearchResults()
    return ddg.run(query)


def WikipediaSearchTool(inputs):
    query = inputs["query"]
    wikipedia = WikipediaRetriever(top_k_results=3)
    return wikipedia.run(query)


functions_map = {
    "DuckDuckGoSearchTool": DuckDuckGoSearchTool,
    "WikipediaSearchTool": WikipediaSearchTool,
}


functions = [
    {
        "type": "function",
        "function": {
            "name": "DuckDuckGoSearchTool",
            "description": "Use this tool to search by using DuckDuckGo. It takes a query as an argument.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query you will search for.Example query: Research about the XZ backdoor",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "WikipediaSearchTool",
            "description": "Use this tool to search by using Wikipedia. It takes a query as an argument.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query you will search for.Example query: Research about the XZ backdoor",
                    },
                },
                "required": ["query"],
            },
        },
    },
]
