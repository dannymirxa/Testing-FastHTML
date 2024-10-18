import streamlit as st
import requests
from PIL import Image
import os
from requests.auth import HTTPBasicAuth

# Function for the Image Uploader page
def image_uploader():
    st.title("Image Uploader")
    with st.form(key='upload_form'):
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        caption = st.text_input("Enter a caption for the image")
        submit_button = st.form_submit_button(label='Upload')

    # Check if the form has been submitted
    if submit_button:
        if uploaded_file is not None:
            # Save the uploaded file to the uploads directory
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Open the uploaded image
            image = Image.open(file_path)
            
            # Display the image
            st.image(image, caption=caption, use_column_width=True)
            st.write(f"Image uploaded successfully and saved to {file_path}!")
            
            # Upload the image and caption to the FastAPI service
            with open(file_path, "rb") as f:
                response = requests.post(
                    "http://localhost:8000/uploadImage/",
                    files={"file": f},
                    data={"caption": caption},
                    auth=HTTPBasicAuth('danial@example.com','mirza')
                )
            
            # Handle the response
            if response.status_code == 200:
                st.write("Image and caption uploaded to the server successfully!")
            else:
                st.write(f"Failed to upload to the server: {response.content}")
        else:
            st.write("Please upload an image file.")