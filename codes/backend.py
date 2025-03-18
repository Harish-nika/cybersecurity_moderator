import os
import faiss
import ollama
import uvicorn
import fitz  # PyMuPDF for PDFs
import numpy as np
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer

# Initialize FastAPI
app = FastAPI(title="Cybersecurity Content Moderator API")

# Load Sentence Transformer model for embeddings
embedding_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Create FAISS index
dimension = 384  # Embedding size of MiniLM
faiss_index = faiss.IndexFlatL2(dimension)
text_chunks = []  # Store original text chunks
chunk_id_map = {}  # Map FAISS index IDs to text chunks

# Ollama Model
#OLLAMA_MODEL = "cyber-moderator-G3:27b"
OLLAMA_MODEL = "cyber-moderator-Wlm:7b"

# ---- TEXT CHUNKING FUNCTION ----
def chunk_text(text: str, chunk_size: int = 300) -> List[str]:
    """Splits text into smaller chunks."""
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += " " + para
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# ---- FUNCTION TO ADD CHUNKS TO FAISS ----
def add_chunks_to_faiss(chunks: List[str]):
    """Embeds text chunks and stores them in FAISS for fast retrieval."""
    global text_chunks
    for chunk in chunks:
        embedding = embedding_model.encode([chunk])
        faiss_index.add(np.array(embedding, dtype=np.float32))
        chunk_id_map[len(text_chunks)] = chunk
        text_chunks.append(chunk)


# ---- API: Upload Text ----
@app.post("/moderate-text/")
async def moderate_text(content: str = Form(...)):
    """Accepts raw text, chunks it, adds to FAISS, and sends to Ollama for moderation."""
    chunks = chunk_text(content)
    add_chunks_to_faiss(chunks)

    results = []
    for chunk in chunks:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": chunk}]
        )
        results.append({"chunk": chunk, "moderation_result": response["message"]["content"]})

    return JSONResponse({"moderation_results": results})


# ---- API: Upload PDF ----
@app.post("/moderate-pdf/")
async def moderate_pdf(file: UploadFile = File(...)):
    """Extracts text from PDF, chunks it, adds to FAISS, and sends chunks to Ollama."""
    pdf_text = ""
    doc = fitz.open(stream=await file.read(), filetype="pdf")

    for page in doc:
        pdf_text += page.get_text("text") + "\n"

    chunks = chunk_text(pdf_text)
    add_chunks_to_faiss(chunks)

    results = []
    for chunk in chunks:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": chunk}]
        )
        results.append({"chunk": chunk, "moderation_result": response["message"]["content"]})

    return JSONResponse({"moderation_results": results})


# ---- API: Retrieve Chunks ----
@app.get("/retrieve-similar/")
async def retrieve_chunks(query: str):
    """Finds relevant text chunks using FAISS."""
    if len(text_chunks) == 0:
        raise HTTPException(status_code=400, detail="No data available for similarity search.")

    query_embedding = embedding_model.encode([query])
    _, indices = faiss_index.search(np.array(query_embedding, dtype=np.float32), k=5)

    retrieved_chunks = [chunk_id_map[idx] for idx in indices[0] if idx < len(text_chunks)]

    return JSONResponse({"similar_chunks": retrieved_chunks})


# ---- Run FastAPI ----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
