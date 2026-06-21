# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
from typing import List
from app.config import EMBEDDING_MODEL_NAME
# pyrefly: ignore [missing-import]
import numpy as np

class Embedder:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
            cls._instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return cls._instance

    @classmethod
    def embed_query(cls, text: str) -> np.ndarray:
        model = cls.get_instance()
        # Ensure single vector is 1D array or list
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding

    @classmethod
    def embed_documents(cls, texts: List[str]) -> np.ndarray:
        model = cls.get_instance()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings
