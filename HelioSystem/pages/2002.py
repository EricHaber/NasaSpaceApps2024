import streamlit as st
import numpy as np
import random
import time
from openai import OpenAI
from stpyvista import stpyvista



client = OpenAI()



global pureResponse
def response_generator(AllMessages):
    global pureResponse
    GPTresponse = client.chat.completions.create(
        model="gpt-4o-mini",
        messages= AllMessages
    )
    pureResponse = str(GPTresponse.choices[0].message.content)
    response = "Space Bot: " + str(GPTresponse.choices[0].message.content)
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.set_page_config(layout="wide")

SmallObject = "the 2002 AA69 asteroid"

PageName= f""" # {SmallObject} Info Page"""
col1, col2= st.columns([1,1])
with col1:
    st.write(PageName)
with col2:
    isClicked = st.button("Back", use_container_width=True)

if isClicked :
    st.switch_page("pages/Solar_System_Model.py")



if not "AllMessages" in st.session_state:
    st.session_state.AllMessages=[{"role": "system", "content": f"You are a knowledgeable astronomer and should briefly answer any of the users questions about {SmallObject}."}]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


st.image("HelioSystem/images/HalleysComet.jpeg", width = 750)


with st.chat_message("assistant"):
    st.markdown(f"Space Bot: Hello 👋 do you have any questions about {SmallObject}?")

# Accept user input
if prompt := st.chat_input("Type a question"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": f"User: {prompt}"})
    st.session_state.AllMessages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(f"User: {prompt}")

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(st.session_state.AllMessages))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.AllMessages.append({"role": "assistant", "content": pureResponse})
    print(st.session_state.AllMessages)
