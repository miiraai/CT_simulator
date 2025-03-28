import streamlit as st
from PIL import Image

from obliczenia import *

st.set_page_config(layout="wide")
st.title("CT Simulator")

if "page" not in st.session_state:
    st.session_state.page = "main"


def go_to_page(page_name):
    st.session_state.page = page_name


if st.session_state.page == "main":
    st.title("CT Simulator - Main Page")

    uploaded_file = st.file_uploader("Browse Files", type=["png"])

    # if uploaded_file:
        # image = Image.open(uploaded_file)
        # st.image(image, caption="Uploaded Image", use_container_width =True)

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        image = Image.open(uploaded_file)
        st.session_state.image = image  # Save opened image too
        # st.image(image, caption="Uploaded Image", use_container_width=True)

    if "image" in st.session_state:
        st.image(st.session_state.image, caption="Chosen image", use_container_width=False)

    if st.button("Go to first Page"):
        go_to_page("first")

    st.session_state.alpha = st.slider("Delta Alpha (α)", min_value=5, max_value=180, step=5)
    st.session_state.n = st.slider("Number of Detectors (n)", min_value=0, max_value=180)
    st.session_state.l = st.slider("Detector Spread (l)", min_value=0, max_value=180)

    if st.button("Show Values"):
        st.write("Values for alpha:")
        for i in range(0, 180, st.session_state.get('alpha', 'Not Set')):
            st.text(f"alpha = {i}")
        st.write("n =", st.session_state.get('n', 'Not Set'))
        st.write("l =", st.session_state.get('l', 'Not Set'))

    # st.subheader("Simulation Output")
    #
    # if uploaded_file:
    #     st.image(image, caption="Original Image", width=300)

    st.markdown(f"**Delta Alpha:** {st.session_state.get('alpha', 'Not Set')}")
    st.markdown(f"**n:** {st.session_state.get('n', 'Not Set')}")
    st.markdown(f"**l:** {st.session_state.get('l', 'Not Set')}")

elif st.session_state.page == "first":
    st.title("First Page")

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            model_img = Image.open("modele/model.png")
            st.image(model_img, caption="Model")
        except:
            st.warning("model.png not found")

    with col2:
        try:
            sinogram_img = Image.open("modele/sinogram.png")
            st.image(sinogram_img, caption="Sinogram")
        except:
            st.warning("sinogram.png not found")

    with col3:
        try:
            wynik_img = Image.open("modele/wynik.png")
            st.image(wynik_img, caption="Wynik")
        except:
            st.warning("wynik.png not found")

    if st.button("Back to Main Page"):
        go_to_page("main")

    st.slider("Adjust Delta Alpha", min_value=0, max_value=180, step=st.session_state.get('alpha', 'Not Set'), key="alpha_slider_2")
