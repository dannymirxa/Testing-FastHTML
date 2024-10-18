import streamlit as st
import requests
import os
from requests.auth import HTTPBasicAuth

def social():
    st.title("Social")
    response = requests.get("http://localhost:8000/postByEmail/danial@example.com")
    posts = response.json()
    if 'comments' not in st.session_state:
        st.session_state.comments = {}

    for post in posts:
        image_path = os.path.join("uploads", post['image'])
        if os.path.exists(image_path):
            st.image(image_path, caption=post['caption'])
            if post['image'] not in st.session_state.comments:
                response = requests.get(f"http://localhost:8000/commentsByImage/{post['image']}")
                st.session_state.comments[post['image']] = response.json()

            for comment in st.session_state.comments[post['image']]:
                st.write(f"{comment['text']} - {comment['created_at']}")
            with st.form(key=post['image']):
                comment = st.text_input("Comment")
                submit_button = st.form_submit_button(label='Comment')
                if submit_button:
                    response = requests.post(
                        "http://localhost:8000/postComment/",
                        json={"Image": post['image'], "Text": comment},
                        auth=HTTPBasicAuth('danial@example.com','mirza')
                    )
                    if response.status_code == 200:
                        st.write("Comment posted successfully!")
                        response = requests.get(f"http://localhost:8000/commentsByImage/{post['image']}")
                        st.session_state.comments[post['image']] = response.json()
                    else:
                        st.write(f"Failed to post comment: {response.content}")
        else:
            st.write("Image not found.")