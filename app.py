import streamlit as st
import fitz  # PyMuPDF for PDF processing
import faiss
import numpy as np
import ollama
from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the Ollama model
llm = ollama.Ollama(model="cyber-moderator-G3:27b")

# Initialize FAISS index
embedding_dim = 384  # Dimension of all-MiniLM-L6-v2 embeddings
index = faiss.IndexFlatL2(embedding_dim)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n\n".join([page.get_text("text") for page in doc])
    return text

# Function to split text into chunks (paragraphs)
def split_text_into_chunks(text):
    paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
    return paragraphs

# Function to get embeddings and store in FAISS
def store_embeddings(chunks):
    vectors = np.array([embedding_model.encode(chunk) for chunk in chunks]).astype("float32")
    index.add(vectors)
    return vectors

# Function to retrieve the top similar chunks
def retrieve_similar_chunks(query, top_k=3):
    query_embedding = np.array([embedding_model.encode(query)]).astype("float32")
    _, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]

# Function to send chunk to Ollama for moderation
def moderate_content(chunk):
    response = llm.chat(messages=[{"role": "user", "content": f'content: "{chunk}"'}])
    return response["message"]["content"]

# Streamlit UI
st.title("Cybersecurity Content Moderator (Ollama)")

# User selects input method
option = st.radio("Choose Input Method:", ("Copy-Paste Text", "Upload PDF"))

if option == "Copy-Paste Text":
    user_input = st.text_area("Paste your content here:")
    if st.button("Moderate Content") and user_input:
        chunks = split_text_into_chunks(user_input)
        store_embeddings(chunks)
        st.write("### Moderation Results:")
        for chunk in chunks:
            st.write(f"**Chunk:** {chunk}")
            output = moderate_content(chunk)
            st.json(output)

elif option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file and st.button("Process PDF"):
        text = extract_text_from_pdf(uploaded_file)
        chunks = split_text_into_chunks(text)
        store_embeddings(chunks)
        st.write("### Moderation Results:")
        for chunk in chunks:
            st.write(f"**Chunk:** {chunk}")
            output = moderate_content(chunk)
            st.json(output)
