# pyrefly: ignore [missing-import]
from transformers import pipeline
from typing import List, Dict, Any
from app.config import QA_MODEL_NAME

class QAEngine:
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            print(f"Loading QA model: {QA_MODEL_NAME}...")
            cls._pipeline = pipeline("question-answering", model=QA_MODEL_NAME)
        return cls._pipeline

    @classmethod
    def answer_question(cls, question: str, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs extractive QA across a list of passages.
        Each passage should be a dict: {
            "content": str,
            "document_name": str,
            "page_number": int
        }
        Returns the best answer, confidence score, citation, and surrounding text context.
        """
        qa_pipeline = cls.get_pipeline()
        
        best_answer = {
            "answer": "No answer found in the selected documents.",
            "score": 0.0,
            "document_name": None,
            "page_number": None,
            "context": None,
            "start": 0,
            "end": 0
        }

        if not passages:
            return best_answer

        results = []
        for passage in passages:
            content = passage["content"]
            if not content.strip():
                continue
            
            try:
                # Run extractive QA pipeline on this specific passage
                res = qa_pipeline(question=question, context=content)
                
                results.append({
                    "answer": res["answer"],
                    "score": float(res["score"]),
                    "document_name": passage["document_name"],
                    "page_number": passage["page_number"],
                    "context": content,
                    "start": res["start"],
                    "end": res["end"]
                })
            except Exception as e:
                print(f"QA pipeline error on passage from {passage['document_name']}: {e}")

        if not results:
            return best_answer

        # Sort answers by confidence score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return the best answer (highest score) and top alternatives
        best = results[0]
        
        # If the best score is very low, we can still return it but flag it
        if best["score"] < 0.01:
            best["answer"] = "Uncertain: " + best["answer"]

        # Add top alternatives for UI display if requested
        best["alternatives"] = results[1:3]
        return best
