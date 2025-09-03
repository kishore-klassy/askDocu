# File: modules/vector_store.py
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

VECTOR_STORE_PATH = 'data/vector.index'
DOCS_PATH = 'data/docs.npy'

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []

    def build_index(self, documents):
        if not documents:
            raise ValueError("Cannot build index with empty documents list")
            
        texts = [doc['text'] for doc in documents]
        self.documents = documents
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # Ensure data directory exists
        os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
        
        # Save to disk
        faiss.write_index(self.index, VECTOR_STORE_PATH)
        np.save(DOCS_PATH, np.array(documents, dtype=object))

    def load_index(self):
        if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(DOCS_PATH):
            return False
        self.index = faiss.read_index(VECTOR_STORE_PATH)
        self.documents = np.load(DOCS_PATH, allow_pickle=True).tolist()
        return True

    def query(self, query_text, top_k=5):
        if self.index is None:
            raise RuntimeError("Vector index not initialized")
        if not query_text or not query_text.strip():
            return []
            
        q_emb = self.model.encode([query_text], convert_to_numpy=True)
        D, I = self.index.search(q_emb, min(top_k, len(self.documents)))
        
        # Filter out invalid indices and ensure we don't exceed document bounds
        valid_indices = [i for i in I[0] if 0 <= i < len(self.documents)]
        results = [self.documents[i] for i in valid_indices]
        return results

def create_or_load_vector_store(documents):
    store = VectorStore()
    
    # Try to load existing vector store first
    if store.load_index():
        print("Loaded existing vector store from disk.")
        return store
    
    # If loading fails or files don't exist, create new index
    print("Creating new vector store...")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
    
    # Remove old vector store files if they exist but are corrupted
    if os.path.exists(VECTOR_STORE_PATH):
        os.remove(VECTOR_STORE_PATH)
    if os.path.exists(DOCS_PATH):
        os.remove(DOCS_PATH)

    store.build_index(documents)
    return store

