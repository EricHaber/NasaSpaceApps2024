import streamlit as st
import numpy as np
import random
import time
from openai import OpenAI
import pyvista as pv
from pyvista import examples
from stpyvista import stpyvista
import json




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



if not "AllMessages" in st.session_state:
    st.session_state.AllMessages=[{"role": "system", "content": "You are a knowledgeable astronomer and should briefly answer any of the users questions about the moon."}]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.set_page_config(layout="wide")

client = OpenAI()



PageName= """
# Asteroid Model"""
st.write(PageName)

light = pv.Light()
light.set_direction_angle(30, -20) 

mars = examples.planets.load_moon(radius=3397.2)
mars_texture = examples.planets.download_moon_surface(texture=True)
mars.translate((-30000.0, 0.0, 0.0), inplace=True)

plotter = pv.Plotter(lighting="none")

cubemap = examples.download_cubemap_space_16k()
#_ = plotter.add_actor(cubemap.to_skybox())
plotter.set_environment_texture(cubemap, True) 
plotter.add_light(light)
plotter.add_mesh(mars, texture=mars_texture, smooth_shading=True)
plotter.view_isometric()
plotter.background_color = 'black'

stpyvista(plotter)


with st.chat_message("assistant"):
    st.markdown("Space Bot: Hello 👋 do you have any questions about the Moon?")

# Accept user input
if prompt := st.chat_input("What is up?"):
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