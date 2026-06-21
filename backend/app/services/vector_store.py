# pyrefly: ignore [missing-import]
import faiss
# pyrefly: ignore [missing-import]
import numpy as np
import os
from typing import List, Dict, Any, Tuple
from app.config import FAISS_INDEX_PATH
from app.services.embedder import Embedder

class VectorStore:
    _index = None
    _dimension = 384  # Dimension for all-MiniLM-L6-v2

    @classmethod
    def get_index(cls):
        if cls._index is None:
            if os.path.exists(FAISS_INDEX_PATH):
                try:
                    print(f"Loading FAISS index from {FAISS_INDEX_PATH}...")
                    cls._index = faiss.read_index(FAISS_INDEX_PATH)
                except Exception as e:
                    print(f"Failed to load FAISS index: {e}, creating a new flat index.")
                    cls._index = faiss.IndexFlatIP(cls._dimension)
            else:
                print("Creating new FAISS IndexFlatIP...")
                cls._index = faiss.IndexFlatIP(cls._dimension)
        return cls._index

    @classmethod
    def rebuild_index(cls, chunks: List[Dict[str, Any]]) -> None:
        """
        Rebuilds the FAISS index from scratch using the provided list of chunks.
        Each chunk should be a dict: {"id": int, "content": str}
        """
        if not chunks:
            # Create an empty index
            cls._index = faiss.IndexFlatIP(cls._dimension)
            cls.save()
            return

        texts = [chunk["content"] for chunk in chunks]
        embeddings = Embedder.embed_documents(texts)
        
        # Normalize embeddings to unit length for Cosine Similarity (using IndexFlatIP)
        faiss.normalize_L2(embeddings)
        
        # Initialize new flat index
        new_index = faiss.IndexFlatIP(cls._dimension)
        new_index.add(embeddings)
        
        cls._index = new_index
        cls.save()
        print(f"FAISS index rebuilt successfully with {len(chunks)} vectors.")

    @classmethod
    def search(cls, query_text: str, k: int = 3) -> List[Tuple[int, float]]:
        """
        Searches the FAISS index for the top-k matches for query_text.
        Returns a list of (vector_index, score).
        """
        index = cls.get_index()
        if index.ntotal == 0:
            return []

        query_vector = Embedder.embed_query(query_text)
        # Reshape to (1, dim)
        query_vector = np.expand_dims(query_vector, axis=0).astype('float32')
        faiss.normalize_L2(query_vector)

        # Search index
        scores, indices = index.search(query_vector, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1: # FAISS returns -1 if there are not enough vectors in index
                results.append((int(idx), float(score)))
        return results

    @classmethod
    def save(cls) -> None:
        if cls._index is not None:
            faiss.write_index(cls._index, FAISS_INDEX_PATH)
            print(f"FAISS index saved to {FAISS_INDEX_PATH}.")
