# pyrefly: ignore [missing-import]
import pypdf
from typing import List, Tuple, Dict, Any

class PDFParser:
    @staticmethod
    def extract_text_by_page(file_path: str) -> List[Tuple[int, str]]:
        """
        Reads a PDF and returns a list of tuples containing (page_number_1_indexed, text).
        """
        pages_content = []
        try:
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_content.append((i + 1, text))
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
        return pages_content

    @staticmethod
    def detect_document_type(filename: str, full_text: str) -> str:
        """
        Infers document type based on text content and filename.
        Returns one of: "HR Policy", "Vendor Contract", "Security SOP", "General"
        """
        import re
        filename_lower = filename.lower()
        
        # 1. Primary check: Filename keywords/prefixes
        if any(kw in filename_lower for kw in ["hr_policy", "hr policy", "handbook", "employee"]):
            return "HR Policy"
        if any(kw in filename_lower for kw in ["security_sop", "security sop", "sop", "procedure"]):
            return "Security SOP"
        if any(kw in filename_lower for kw in ["vendor_contract", "vendor contract", "contract", "agreement", "nda"]):
            return "Vendor Contract"
            
        # 2. Secondary check: Content regex search with word boundaries
        text_lower = (filename + " " + full_text).lower()
        if re.search(r'\b(hr policy|employee handbook|conduct|leave policy|leave of absence|benefits)\b', text_lower):
            return "HR Policy"
        if re.search(r'\b(sop|standard operating procedure|security policy|password policy|incident response)\b', text_lower):
            return "Security SOP"
        if re.search(r'\b(vendor|contract|agreement|nda|sla|liability)\b', text_lower):
            return "Vendor Contract"
            
        return "General"
