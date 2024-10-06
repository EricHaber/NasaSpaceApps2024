import streamlit as st
from PIL import Image
st.set_page_config(layout="wide")
 
st.title("Welcome to...")
col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')

with col2:
    st.image("d:/Documents/Coding/NasaSpaceApps2024/images/heliosystemwide.png") #, width=1000

with col3:
    st.write(' ')

# ChatGPT: reate a container for the buttons to ensure they stay under the title
button_container = st.container()
 
with button_container:
    # ChatGPT: Add buttons immediately after the title
    col1, col2 = st.columns([1, 1])
    with col1:
        ModelIsClicked=st.button("Model",use_container_width=True)
    with col2:
        AboutUsIsClicked = st.button("About us",use_container_width=True)
    if ModelIsClicked:
        st.switch_page("pages/Solar_System_Model.py")
    elif AboutUsIsClicked:
        st.switch_page("pages/About_Us.py")