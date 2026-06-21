from typing import List, Dict, Any

class Chunker:
    @staticmethod
    def chunk_document(pages_content: List[Dict[str, Any]], chunk_size: int = 500, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
        """
        Splits page text into overlapping word chunks.
        Each input page_content item is a dict with keys: 'page_number', 'text'.
        Returns a list of dicts: {'page_number': int, 'content': str}
        """
        chunks = []
        for page in pages_content:
            page_num = page["page_number"]
            text = page["text"].strip()
            if not text:
                continue

            words = text.split()
            if not words:
                continue

            i = 0
            while i < len(words):
                # Grab a chunk of words
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                chunks.append({
                    "page_number": page_num,
                    "content": chunk_text
                })
                
                # Advance by step (size - overlap)
                i += (chunk_size - chunk_overlap)
                
                # Prevent infinite loops if overlap is too large
                if chunk_size <= chunk_overlap:
                    break
        return chunks
