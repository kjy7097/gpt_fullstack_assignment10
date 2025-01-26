import streamlit as st

from tool_functions import *
import os
from utils import *
import base64

st.title("Web Search Assistant")
st.markdown(
    """
### Please ask anything to search in the Web. (DuckDuckGo is not working because of HTTP exception...)
"""
)

with st.sidebar:
    st.page_link(
        page="https://github.com/kjy7097/gpt_fullstack_assignment10.git",
        label="Click! to go Github Repo.",
    )
    with st.form("api_form"):
        col1, col2 = st.columns(2)
        api_key = col1.text_input(
            "Enter OpenAI API Key....",
        )
        col2.form_submit_button("Apply")

    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.cache_data.clear()


if api_key:
    util = Util()
    util.create_assistant()
    keyword = st.text_input("Search keyword", placeholder="Example : Tesla")
    if keyword:
        util.create_or_get_thread(keyword)
        util.send_keyword(keyword)
        with open(f"files/{keyword}.txt", "rb") as f:
            st.download_button(f"Summary of {keyword}", f, file_name=f"{keyword}.txt")
        user_message = st.chat_input(f"Ask anything about {keyword}...")
        if user_message:
            util.send_message("user", user_message)
        messages = util.get_messages()
        for message in messages[1:]:
            with st.chat_message(message["role"]):
                st.markdown(message["message"])
