import streamlit as st
from PIL import Image
import os
import requests
from requests.auth import HTTPBasicAuth

from image_uploader import image_uploader
from social import social

# Create the uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Function for the Social page (currently a placeholder)


# Main function to handle navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Image Uploader", "Social"])

    if page == "Home":
        st.title("Welcome to the App")
        st.write("Please choose a page to navigate to:")
    elif page == "Image Uploader":
        image_uploader()
    elif page == "Social":
        social()

if __name__ == "__main__":
    main()