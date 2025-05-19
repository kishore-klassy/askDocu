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
        texts = [doc['text'] for doc in documents]
        self.documents = documents
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

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
        q_emb = self.model.encode([query_text], convert_to_numpy=True)
        D, I = self.index.search(q_emb, top_k)
        results = [self.documents[i] for i in I[0]]
        return results

def create_or_load_vector_store(documents):
    # Remove old vector store files
    if os.path.exists(VECTOR_STORE_PATH):
        os.remove(VECTOR_STORE_PATH)
    if os.path.exists(DOCS_PATH):
        os.remove(DOCS_PATH)

    store = VectorStore()
    store.build_index(documents)
    return store

