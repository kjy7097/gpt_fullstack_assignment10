from langchain.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.document_loaders import WebBaseLoader
import os


def wikipedia_tool(inputs):
    wk = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wk.run(inputs["query"])


def duckduckgo_tool(inputs):
    ddg = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper())
    return ddg.run(inputs["query"])


def scrap_tool(inputs):
    loader = WebBaseLoader(inputs["weblink"])
    return loader.load()[0].page_content


def file_save_tool(inputs):
    if not os.path.exists("files"):
        os.mkdir("files")
    with open(f"files/{inputs['file_path']}", "w", encoding="utf-8") as f:
        f.write(inputs["text"])
    return ""


functions = [
    {
        "type": "function",
        "function": {
            "name": "wikipedia_tool",
            "description": "Use this tool to search keywords in Wikipedia. It takes a query as an argument. Example query: Tesla",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query you will search for",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "duckduckgo_tool",
            "description": "Use this tool to search keywords in DuckDuckGo. It takes a query as an argument. Example query: Tesla",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query you will search for",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrap_tool",
            "description": "Use this tool to scrap the website. It takes a weblink as an argument.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weblink": {
                        "type": "string",
                        "description": "a link of website",
                    },
                },
                "required": ["weblink"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_save_tool",
            "description": "Use this tool to save input text. It takes content text and file path as arguments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The content to save.",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "The file path",
                    },
                },
                "required": ["text", "file_path"],
            },
        },
    },
]
