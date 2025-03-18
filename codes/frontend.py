import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Cybersecurity Content Moderator", layout="wide")

st.title("🔍 Cybersecurity Content Moderator")

# Tabs for different functionalities
tab1, tab2 = st.tabs(["📜 Moderate Content", "🔎 Retrieve Similar Chunks"])

with tab1:
    st.subheader("📝 Upload Content for Moderation")

    content_type = st.radio("Select Input Type:", ["Paste Text", "Upload PDF"])

    if content_type == "Paste Text":
        text_input = st.text_area("Enter text for moderation:", height=200)
        if st.button("Moderate Text"):
            if text_input.strip():
                response = requests.post(f"{API_URL}/moderate-text/", data={"content": text_input})
                if response.status_code == 200:
                    results = response.json()["moderation_results"]
                    for res in results:
                        st.markdown(f"**Chunk:** {res['chunk']}")
                        st.code(res["moderation_result"], language="json")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            else:
                st.warning("Please enter text for moderation.")

    elif content_type == "Upload PDF":
        uploaded_file = st.file_uploader("Upload PDF for moderation", type=["pdf"])
        if uploaded_file:
            if st.button("Moderate PDF"):
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(f"{API_URL}/moderate-pdf/", files=files)
                if response.status_code == 200:
                    results = response.json()["moderation_results"]
                    for res in results:
                        st.markdown(f"**Chunk:** {res['chunk']}")
                        st.code(res["moderation_result"], language="json")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

with tab2:
    st.subheader("🔎 Retrieve Similar Chunks")
    query = st.text_input("Enter text to find similar content:")
    if st.button("Search"):
        if query.strip():
            response = requests.get(f"{API_URL}/retrieve-similar/", params={"query": query})
            if response.status_code == 200:
                similar_chunks = response.json()["similar_chunks"]
                if similar_chunks:
                    st.write("### 🔍 Similar Content Found:")
                    for chunk in similar_chunks:
                        st.write(f"- {chunk}")
                else:
                    st.info("No similar content found.")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        else:
            st.warning("Please enter text to search for similar content.")
