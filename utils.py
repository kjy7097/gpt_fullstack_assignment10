import json
from tool_functions import *
import streamlit as st
from openai import OpenAI
import time


class Util:
    def __init__(self):
        self.client = OpenAI()

    def create_assistant(self):
        assistants = list(
            filter(
                lambda x: x.name == "Web Search Assistant",
                self.client.beta.assistants.list().data,
            )
        )
        if len(assistants) > 0:
            for assistant in assistants:
                self.client.beta.assistants.delete(assistant.id)
        self.assistant = self.client.beta.assistants.create(
            name="Web Search Assistant",
            instructions="""
            You are a helpful researcher.
            You will search the keyword in wikipedia or duckduck go.
            Example:
              keyword:Apple
            if you run duckduckgo tool, you have to scrap the first web page.
            You will summurize the results and save them to [search keyword].txt file.
            Example:
              Apple.txt,

            If user ask something about the keyword, just answer based on the your response without file saving.
            """,
            tools=functions,
            model="gpt-4o-mini",
        )

    def create_or_get_assistant(self):
        assistants = list(
            filter(
                lambda x: x.name == "Web Search Assistant",
                self.client.beta.assistants.list().data,
            )
        )
        if len(assistants) > 0:
            self.assistant = assistants[0]
        else:
            self.create_assistant()

    @st.cache_data
    def create_thread(_self, keyword):
        return _self.client.beta.threads.create()

    def create_or_get_thread(self, keyword):
        self.thread = self.create_thread(keyword)

    def create_run(self):
        if not "run" in st.session_state:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
        else:
            self.run = st.session_state["run"]

    def get_run(self):
        return self.client.beta.threads.runs.retrieve(
            run_id=self.run.id,
            thread_id=self.thread.id,
        )

    @st.cache_data(show_spinner="In progress...")
    def send_keyword(_self, keyword):
        _self.client.beta.threads.messages.create(
            thread_id=_self.thread.id,
            role="user",
            content=f"keyword:{keyword}",
        )
        _self.create_run()
        while _self.get_run().status != "completed":
            while _self.get_run().status == "in_progress":
                time.sleep(0.1)
            if _self.get_run().status == "requires_action":
                _self.submit_tool_outputs()
            time.sleep(0.1)

    def send_message(_self, role, content):
        _self.client.beta.threads.messages.create(
            thread_id=_self.thread.id,
            role=role,
            content=content,
        )
        _self.create_run()
        with st.spinner("In progress..."):
            while _self.get_run().status != "completed":
                while _self.get_run().status == "in_progress":
                    time.sleep(0.1)
                if _self.get_run().status == "requires_action":
                    _self.submit_tool_outputs()
                time.sleep(0.1)

    def get_messages(self):
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id,
        )
        messages = list(messages)
        messages.reverse()
        message_list = []
        for message in messages:
            message_list.append(
                {
                    "role": "human" if message.role == "user" else "ai",
                    "message": message.content[0].text.value,
                }
            )
        return message_list

    def get_tool_outputs(self):
        run = self.get_run()
        outputs = []
        for action in run.required_action.submit_tool_outputs.tool_calls:
            action_id = action.id
            function = action.function
            print(f"Calling function: {function.name}")
            output = globals()[function.name](json.loads(function.arguments))
            outputs.append(
                {
                    "output": output,
                    "tool_call_id": action_id,
                }
            )
        return outputs

    def submit_tool_outputs(self):
        outputs = self.get_tool_outputs()
        return self.client.beta.threads.runs.submit_tool_outputs(
            run_id=self.run.id,
            thread_id=self.thread.id,
            tool_outputs=outputs,
        )
