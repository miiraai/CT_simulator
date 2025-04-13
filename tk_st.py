from time import sleep

import numpy as np
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import pydicom
import datetime

import io

from obliczenia import *

@st.cache_data
def compute_sinogram(img, steps, span, num_rays, max_angle, intermediate=False):
    return calculate_sinogram(img, steps, span, num_rays, max_angle, intermediate)


@st.cache_data
def compute_reconstruction(img, sinogram, steps, span, num_rays, max_angle, intermediate=False):
    return reverse_radon_transform(img, sinogram, steps, span, num_rays, max_angle, intermediate)

@st.cache_data
def compute_filter(sin):
    kernel = create_shepp_logan_kernel(9)
    return filter_sinogram(sin, kernel)


def save_as_dicom(image_array, filename, patient_name, patient_id, study_date, comments):
    # Normalize to uint16 if needed
    if image_array.dtype != "uint16":
        image_array = (image_array / image_array.max() * 65535).astype("uint16")

    if len(image_array.shape) != 2:
        raise ValueError("Image must be 2D grayscale.")

    # Create file meta
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.ImplementationClassUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    # Create main dataset
    dt = datetime.datetime.now()
    ds = pydicom.FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Core DICOM identifiers
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()

    # Patient & study info
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.StudyDate = study_date.strftime("%Y%m%d")
    ds.StudyTime = dt.strftime("%H%M%S")
    ds.ContentDate = ds.StudyDate
    ds.ContentTime = ds.StudyTime
    ds.Modality = "CT"
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.ImageComments = comments

    # Image description
    ds.Rows, ds.Columns = image_array.shape
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelSpacing = [1.0, 1.0]
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0  # Unsigned
    ds.PixelData = image_array.tobytes()

    # Windowing (for proper display)
    ds.WindowCenter = int(image_array.max() / 2)
    ds.WindowWidth = int(image_array.max())
    ds.RescaleIntercept = 0
    ds.RescaleSlope = 1

    # Optional: extra tags for viewer compatibility
    ds.Manufacturer = "CT Simulator"
    ds.SliceThickness = 1
    ds.KVP = 120
    ds.BodyPartExamined = "HEAD"

    # Save file
    ds.save_as(filename)


st.set_page_config(layout="wide")
st.title("CT Simulator")

if "page" not in st.session_state:
    st.session_state.page = "main"


def go_to_page(page_name):
    st.session_state.page = page_name

global x
x = False

global it
it = False

global anim
anim = False

global fil
fil = False


if st.session_state.page == "main":
    st.title("CT Simulator - Main Page")

    uploaded_file = st.file_uploader("Browse Files", type=["png", "jpg", "dcm", "bmp"])

    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        st.session_state.uploaded_file = uploaded_file

        if file_type == "dcm":
            x = True
            dcm = pydicom.dcmread(uploaded_file)
            pixel_array = dcm.pixel_array

            st.session_state.name = dcm.get('PatientName', 'Unknown')

            image_8bit = ((pixel_array - np.min(pixel_array)) / (np.ptp(pixel_array)) * 255.0).astype(np.uint8)
            image = Image.fromarray(image_8bit)

        else:
            x = False
            image = Image.open(uploaded_file)

        st.session_state.image = image

    if "image" in st.session_state:
        st.image(st.session_state.image, use_container_width=False)

    fil = st.checkbox("Show filter", value=False)

    if st.button("Go to the simulation"):
        if 'image' not in st.session_state:
            st.write(":red[Select a file]")
        else:
            if fil:
                go_to_page("second")
            elif not x:
                go_to_page("first")
            else:
                go_to_page("third")

    vals = [1, 2, 3, 4, 5, 6, 9, 10, 12, 15, 18, 20, 30, 36, 45, 60, 90, 180]

    st.session_state.alpha = st.select_slider("Delta Alpha (α)", options=vals)
    st.session_state.n = st.slider("Number of Detectors (n)", min_value=20, max_value=500, value=250)
    st.session_state.l = st.slider("Detector Spread (l)", min_value=1, max_value=500, value=120)

    # st.markdown(f"**Delta Alpha:** {st.session_state.get('alpha', 'Not Set')}")
    # st.markdown(f"**n:** {st.session_state.get('n', 'Not Set')}")
    # st.markdown(f"**l:** {st.session_state.get('l', 'Not Set')}")

elif st.session_state.page == "first":
    st.title("Simulation")

    st.markdown(f"**Delta Alpha:** {st.session_state.get('alpha', 'Not Set')}, **n:** {st.session_state.get('n', 'Not Set')}, **l:** {st.session_state.get('l', 'Not Set')}")

    steps = 180 // st.session_state.alpha
    st.session_state.step = st.slider("step", min_value=1, max_value=steps, value=steps)

    if st.button("show animation"):
        anim = True

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image(st.session_state.image, caption="Model", use_container_width=True)
    with col2:
        img_array = np.array(st.session_state.image.convert("L")).astype(np.float32)

        with st.spinner("Obliczanie sinogramu..."):
            sinogram = compute_sinogram(img_array, steps=steps, span=st.session_state.get('l', '120'),
                                        num_rays=st.session_state.get('n', '250'), max_angle=180, intermediate=True)

        sin = np.transpose(sinogram[steps - 1])

        vmin = np.percentile(sin, 1)
        vmax = np.percentile(sin, 99)

        if anim == False:
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.imshow(np.transpose(sinogram[st.session_state.get("step", 0) - 1]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax.axis('off')

            st.pyplot(fig, use_container_width=True)

        elif anim == True:
            placeholder = st.empty()
            for i in range(steps):
                fig, ax = plt.subplots(figsize=(2, 2))
                ax.imshow(np.transpose(sinogram[i]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
                ax.axis('off')

                placeholder.pyplot(fig, use_container_width=True)
                sleep(1/steps)


    with col3:
        with st.spinner("Obliczanie rekonstrukcji..."):
            reconstructed = compute_reconstruction(img_array, sinogram[steps - 1], steps=steps, span=st.session_state.get('l', '120'),
                                                   num_rays=st.session_state.get('n', '250'), max_angle=180, intermediate=True)

        vmin = np.percentile(reconstructed, 1)
        vmax = np.percentile(reconstructed, 99)

        if anim == False:
            fig2, ax2 = plt.subplots(figsize=(2, 2))
            ax2.imshow(reconstructed[st.session_state.get("step", 0) - 1], cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax2.axis('off')

            st.pyplot(fig2, use_container_width=True)

        else:
            placeholder = st.empty()
            for i in range(steps):
                fig, ax = plt.subplots(figsize=(2, 2))
                ax.imshow(reconstructed[i], cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
                ax.axis('off')

                placeholder.pyplot(fig, use_container_width=True)
                sleep(1/steps)

            anim = False

    st.success("Proces zakończony!")

    kernel = create_shepp_logan_kernel(9)

    patient_name = st.text_input("Patient Name")
    patient_id = st.text_input("Patient ID")
    study_date = st.date_input("Study Date", value=datetime.date.today())
    comments = st.text_input("Comments")

    image_array = (reconstructed / np.max(reconstructed) * 65535).astype(np.uint16)

    if st.button("Save DICOM"):
        save_as_dicom(image_array, "zapisane_dicom.dcm", patient_name, patient_id, study_date, comments)

    if st.button("Back to Main Page"):
        go_to_page("main")

elif st.session_state.page == "third":
    st.title("Simulation")

    st.markdown(f"**Delta Alpha:** {st.session_state.get('alpha', 'Not Set')}, **n:** {st.session_state.get('n', 'Not Set')}, **l:** {st.session_state.get('l', 'Not Set')}")

    steps = 180 // st.session_state.alpha
    st.session_state.step = st.slider("step", min_value=1, max_value=steps, value=steps)

    if st.button("show animation"):
        anim = True

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image(st.session_state.image, caption="Model", use_container_width=True)
    with col2:
        img_array = np.array(st.session_state.image.convert("L")).astype(np.float32)

        with st.spinner("Obliczanie sinogramu..."):
            sinogram = compute_sinogram(img_array, steps=steps, span=st.session_state.get('l', '120'),
                                        num_rays=st.session_state.get('n', '250'), max_angle=180, intermediate=True)

        sin = np.transpose(sinogram[steps - 1])

        vmin = np.percentile(sin, 1)
        vmax = np.percentile(sin, 99)

        if anim == False:
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.imshow(np.transpose(sinogram[st.session_state.get("step", 0) - 1]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax.axis('off')

            st.pyplot(fig, use_container_width=True)

        elif anim == True:
            placeholder = st.empty()
            for i in range(steps):
                fig, ax = plt.subplots(figsize=(2, 2))
                ax.imshow(np.transpose(sinogram[i]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
                ax.axis('off')

                placeholder.pyplot(fig, use_container_width=True)
                sleep(1/steps)


    with col3:
        with st.spinner("Obliczanie rekonstrukcji..."):
            reconstructed = compute_reconstruction(img_array, sinogram[steps - 1], steps=steps, span=st.session_state.get('l', '120'),
                                                   num_rays=st.session_state.get('n', '250'), max_angle=180, intermediate=True)

        vmin = np.percentile(reconstructed, 1)
        vmax = np.percentile(reconstructed, 99)

        if anim == False:
            fig2, ax2 = plt.subplots(figsize=(2, 2))
            ax2.imshow(reconstructed[st.session_state.get("step", 0) - 1], cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax2.axis('off')

            st.pyplot(fig2, use_container_width=True)

        else:
            placeholder = st.empty()
            for i in range(steps):
                fig, ax = plt.subplots(figsize=(2, 2))
                ax.imshow(reconstructed[i], cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
                ax.axis('off')

                placeholder.pyplot(fig, use_container_width=True)
                sleep(1/steps)

            anim = False

    st.success("Proces zakończony!")

    kernel = create_shepp_logan_kernel(9)

    # ds = pydicom.dcmread(st.session_state.get("uploaded_file", None))
    # # ds = st.session_state.get("ds", 1)
    # print(ds)

    c1, c2 = st.columns(2)

    with c1:

        patient_name = st.text_input("Patient Name")
        patient_id = st.text_input("Patient ID")
        study_date = st.date_input("Study Date", value=datetime.date.today())
        comments = st.text_input("Comments")

        image_array = (reconstructed / np.max(reconstructed) * 65535).astype(np.uint16)

        if st.button("Save DICOM"):
            save_as_dicom(image_array, "zapisane_dicom.dcm", patient_name, patient_id, study_date, comments)
    with c2:
        st.write(st.session_state.get("name", None))

    if st.button("Back to Main Page"):
        go_to_page("main")

elif st.session_state.page == "second":
    st.title("Simulation")

    st.write("filtr")

    st.markdown(f"**Delta Alpha:** {st.session_state.get('alpha', 'Not Set')}, **n:** {st.session_state.get('n', 'Not Set')}, **l:** {st.session_state.get('l', 'Not Set')}")

    st.image(st.session_state.image, caption="Model", use_container_width=False)
    col1, col2 = st.columns(2)

    with col1:
        img_array = np.array(st.session_state.image.convert("L")).astype(np.float32)

        steps = 180 // st.session_state.alpha

        with st.spinner("Obliczanie sinogramu..."):
            sinogram = compute_sinogram(img_array, steps=steps, span=st.session_state.get('l', '120'),
                                        num_rays=st.session_state.get('n', '250'), max_angle=180, intermediate=True)

        sin = np.transpose(sinogram[steps - 1])

        vmin = np.percentile(sin, 1)
        vmax = np.percentile(sin, 99)

        # st.session_state.step = int(st.session_state.get("step", "Not Set") - 1)
        # st.write(st.session_state.get())

        # st.session_state.step = st.slider("step", min_value=1, max_value=steps, value=steps)
        #
        # if st.button("show animation"):
        #     anim = True

        if anim == False:
            # st.write(anim)
            fig, ax = plt.subplots(figsize=(2, 2))
            # st.write(st.session_state.get("step", 0) - 1)
            ax.imshow(np.transpose(sinogram[st.session_state.get("step", 0) - 1]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
            ax.axis('off')

            # st.session_state.step = st.session_state.get("step", "Not Set") - 1

            st.pyplot(fig, use_container_width=False)

        elif anim == True:
            placeholder = st.empty()  # Create a placeholder
            for i in range(steps):
                # st.write("anim", anim)
                fig, ax = plt.subplots(figsize=(2, 2))
                # st.write(st.session_state.get("step", 0) - 1)
                ax.imshow(np.transpose(sinogram[i]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
                ax.axis('off')

                placeholder.pyplot(fig, use_container_width=False)
                sleep(1/steps)

            anim = False

            # st.session_state.step = st.session_state.get("step", "Not Set") - 1
    with col2:
        img_array = np.array(st.session_state.image.convert("L")).astype(np.float32)

        steps = 180 // st.session_state.alpha

        with st.spinner("Obliczanie sinogramu z filtrem..."):
            filtr_sin = compute_filter(sinogram[-1])

        vmin = np.percentile(filtr_sin, 1)
        vmax = np.percentile(filtr_sin, 99)

        # st.session_state.step = int(st.session_state.get("step", "Not Set") - 1)
        # st.write(st.session_state.get())

        # st.session_state.step = st.slider("step", min_value=1, max_value=steps, value=steps)

        # if st.button("show animation"):
        #     anim = True

        # if anim == False:
        #     st.write(anim)
        fig, ax = plt.subplots(figsize=(2, 2))
            # st.write(st.session_state.get("step", 0) - 1)
        ax.imshow(np.transpose(filtr_sin), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
        ax.axis('off')

            # st.session_state.step = st.session_state.get("step", "Not Set") - 1

        st.pyplot(fig, use_container_width=False)

        # elif anim == True:
        #     placeholder = st.empty()  # Create a placeholder
        #     for i in range(steps):
        #         # st.write("anim", anim)
        #         fig, ax = plt.subplots(figsize=(2, 2))
        #         # st.write(st.session_state.get("step", 0) - 1)
        #         ax.imshow(np.transpose(sinogram[i]), cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
        #         ax.axis('off')
        #
        #         placeholder.pyplot(fig, use_container_width=True)
        #         sleep(1/steps)
        #
        #     anim = False

            # st.session_state.step = st.session_state.get("step", "Not Set") - 1

    cl1, cl2 = st.columns(2)
    with cl1:
        with st.spinner("Obliczanie rekonstrukcji..."):
            reconstructed = compute_reconstruction(img_array, sinogram[steps - 1], steps=steps, span=st.session_state.get('l', '120'),
                                                   num_rays=st.session_state.get('n', '250'), max_angle=180)

        vmin = np.percentile(reconstructed, 1)
        vmax = np.percentile(reconstructed, 99)

        fig2, ax2 = plt.subplots(figsize=(2, 2))
        ax2.imshow(reconstructed, cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
        ax2.axis('off')

        st.pyplot(fig2, use_container_width=False)

    with cl2:
        with st.spinner("Obliczanie rekonstrukcji z filtrem..."):
            filtr_reconstructed = compute_reconstruction(img_array, filtr_sin, steps=steps, span=st.session_state.get('l', '120'),
                                                   num_rays=st.session_state.get('n', '250'), max_angle=180)

        vmin = np.percentile(filtr_reconstructed, 1)
        vmax = np.percentile(filtr_reconstructed, 99)

        fig2, ax2 = plt.subplots(figsize=(2, 2))
        ax2.imshow(filtr_reconstructed, cmap="gray", aspect='auto', vmin=vmin, vmax=vmax)
        ax2.axis('off')

        st.pyplot(fig2, use_container_width=False)

    st.success("Proces zakończony!")

    kernel = create_shepp_logan_kernel(9)


    # if st.button("Show iterative simulation"):
    #     pass

    patient_name = st.text_input("Patient Name")
    patient_id = st.text_input("Patient ID")
    study_date = st.date_input("Study Date", value=datetime.date.today())
    comments = st.text_input("Comments")

    image_array = (reconstructed / np.max(reconstructed) * 65535).astype(np.uint16)

    if st.button("Save DICOM"):
        save_as_dicom(image_array, "zapisane_dicom.dcm", patient_name, patient_id, study_date, comments)

    if st.button("Back to Main Page"):
        go_to_page("main")



