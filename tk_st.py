import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

import io

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
        st.image(st.session_state.image, use_container_width=False)

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
            st.image(st.session_state.image, caption="Model", use_container_width=False)
        except:
            st.warning("No model available")

    with (col2):
        try:
            img_array = np.array(st.session_state.image.convert("L")).astype(np.float32)

            # Calculate sinogram
            sinogram = calculate_sinogram(img_array, steps=180, span=120, num_rays=250, max_angle=180)
            sinogram = np.transpose(sinogram)
            st.session_state.sin = sinogram

            # Use 1st and 99th percentile to clip out extreme outliers
            vmin = np.percentile(sinogram, 1)
            vmax = np.percentile(sinogram, 99)

            # Plot with better contrast
            fig, ax = plt.subplots()
            ax.imshow(sinogram, cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax.axis('off')



            st.pyplot(fig)



            # sinogram = calculate_sinogram(st.session_state.image, steps=180, span=120, num_rays=250, max_angle=180)
            #
            # fig, ax = plt.subplots()
            # ax.imshow(sinogram, cmap="gray")
            # st.pyplot(fig)


            # sinogram = calculate_sinogram(st.session_state.image, steps=180, span=120, num_rays=250, max_angle=180)
            # st.image(sinogram, caption="Sinogram", use_container_width=False)

            # sinogram_img = Image.open("modele/sinogram.png")
            # st.image(sinogram_img, caption="Sinogram")
        except:
            st.warning("sinogram.png not found")

    with col3:
        try:
            # st.write("ser igor")
            img_array = np.array(st.session_state.image.convert("L")).astype(np.float32)

            # st.write("jas mati")

            # Calculate sinogram
            sinogram = calculate_sinogram(img_array, steps=180, span=120, num_rays=250, max_angle=180)
            reconstructed = reverse_radon_transform(img_array, sinogram, steps=180, span=120, num_rays=250, max_angle=180)

            # Use 1st and 99th percentile to clip out extreme outliers
            vmin = np.percentile(reconstructed, 1)
            vmax = np.percentile(reconstructed, 99)
            #
            # st.write("jan to pala")

            # Plot the reconstructed image
            fig2, ax2 = plt.subplots()
            ax2.imshow(reconstructed, cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax2.axis('off')

            # st.write("Reconstructed shape:")
            # st.write("Min:", np.min(reconstructed))
            # st.write("Max:", np.max(reconstructed))
            # st.write("Mean:", np.mean(reconstructed))
            #
            # # Show in Streamlit
            st.pyplot(fig2)


            # wynik_img = Image.open("modele/wynik.png")
            # st.image(wynik_img, caption="Wynik")
        except:
            st.warning("wynik.png not found")

    if st.button("Back to Main Page"):
        go_to_page("main")

    st.slider("Adjust Delta Alpha", min_value=0, max_value=180, step=st.session_state.get('alpha', 'Not Set'), key="alpha_slider_2")
