import streamlit as st
import numpy as np
import random
import time
from openai import OpenAI
import pyvista as pv
from pyvista import examples
from stpyvista import stpyvista




st.write("""
# Solar system model""")


st.write("""
# insert solar system model here
""")

st.slider('year', min_value=1900, max_value=2100, value= 2024)
st.slider('week', min_value=1, max_value=52, value= 40)
