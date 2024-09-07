import streamlit as st
import openai


def get_api_key():
    API_KEY = st.text_input("Please Enter Your OpenAI API Key", type="password")
    return API_KEY


def is_api_key_valid(api_key):
    try:
        openai.api_key = api_key
        openai.Model.list()
    except openai.error.AuthenticationError:
        st.write("Invalid OpenAI API Key")
        st.write("Please Enter Valid API Key")
        return False
    else:
        st.write("Valid OpenAI API Key")
        return True
