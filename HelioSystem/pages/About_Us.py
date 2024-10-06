import streamlit as st
from PIL import Image
 
st.set_page_config(layout="wide")
col1, col2 = st.columns(2)
with col1:
    st.image("HelioSystem/imagesheliosystem.png") #, width=1250
with col2:
    BackIsClicked = st.button("Back", use_container_width=True)
if BackIsClicked:
    st.switch_page("Home_Page.py")

 
st.header("The Mission")
st.text("""Our mission is to offer students, educators, and inquisitive individuals a thorough education on the solar system. This involves
investigating the planets, moons, and asteroids that make up the solar system, along with the intriguing phenomena found in our cosmic
vicinity. Our goal is to enhance knowledge of Near Earth Objects (NEOs) and Potentially Hazardous Asteroids (PHAs), providing current
details on their characteristics, trajectory, and potential impact on Earth. By employing an interactive ChatBot AI (ChatGPT -4o), we are
committed to responding to inquiries, explaining ideas, and leading students on an immersive, stimulating, and customized exploration of
the mysteries of the universe. Our aim is to make learning about the cosmos accessible, informative, and enjoyable for both students and
astronomy enthusiasts alike.
""")
 
st.header("The Team")
st.image("HelioSystem/imagesNoel.jpeg", width=200, caption="Noël Santiago Briand: French, born 5th May 2011. Coder, Designer")
st.image("HelioSystem/imagesEric.jpeg", width=200, caption="Eric Haber Florencio: Brazilian, born in the U.S.A. 18th October 2010. Coder, Designer")
st.image("HelioSystem/imagesLilian.jpeg", width=200, caption="Lilian Tillie Ronzon: French, born 8th November 2011. Coder, Presenter")
st.image("HelioSystem/imagesPablo.jpeg", width=200, caption="Pablo Almagro González: Spanish, born in China 11th July 2010. Designer, Coder and Organizer")
st.image("HelioSystem/imagesAndrew.jpeg", width=200, caption="Andrés Almagro González: Spanish, born in China 12th December 2011. Designer, Presenter")
 
st.header("Sources")
st.subheader("AI chatbot")
st.text("OpenAI API (ChatGPT -4o)")
st.subheader("Data")
st.text("""NASA. (n.d.). Small-body database query. NASA. https://ssd.jpl.nasa.gov/tools/sbdb_query.html
Pyephem. PyEphem Home Page - PyEphem home page. (n.d.). https://rhodesmill.org/pyephem/
O’Neil, D. A. (2017, April 14). Elliptical Orbit Simulator. https://nasa.github.io/mission-viz/RMarkdown/Elliptical_Orbit_Design.html  
NASA. (n.d.-a). Eyes on asteroids - NASA/JPL. NASA. https://eyes.nasa.gov/apps/asteroids/#/watch/
NASA. (n.d.-a). Approximate positions of the planets. NASA. https://ssd.jpl.nasa.gov/planets/approx_pos.html
AI, M. (n.d.). Mistral Ai: Frontier ai in your hands. Mistral AI | Frontier AI in your hands. https://mistral.ai/
Chatgpt. (n.d.-a). https://chatgpt.com/
""")