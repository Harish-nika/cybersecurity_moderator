import streamlit as st
from langchain_community.llms import Ollama

# Load the Ollama model
llm = Ollama(model="cyber-moderator-G3:27b")

# Streamlit App UI
st.set_page_config(page_title="Cybersecurity Content Moderator", layout="wide")

st.title("🛡️ Cybersecurity Content Moderator")
st.write("Enter text to check for harmful content.")

# User input field
user_input = st.text_area("Enter text for moderation:", height=150)

if st.button("Moderate Content"):
    if user_input.strip():
        formatted_input = f'"{user_input}"'  # Ensure text is within quotes
        with st.spinner("Analyzing..."):
            try:
                response = llm.invoke(formatted_input)  # Get moderation results
                st.subheader("🔍 Moderation Result")
                st.json({
                    "user_input": user_input,
                    "moderation_result": response
                })
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter some text to analyze.")
