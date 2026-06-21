# pyrefly: ignore [missing-import]
import yaml
import pickle
import os
from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
from app.config import RISK_RULES_PATH, RISK_CLASSIFIER_PATH

class RiskClassifier:
    _rules = None
    _ml_model = None

    @classmethod
    def load_rules(cls) -> List[Dict[str, Any]]:
        if cls._rules is None:
            if os.path.exists(RISK_RULES_PATH):
                try:
                    with open(RISK_RULES_PATH, 'r') as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            cls._rules = data.get("rules", [])
                        else:
                            cls._rules = []
                        print(f"Loaded {len(cls._rules)} rules from {RISK_RULES_PATH}.")
                except Exception as e:
                    print(f"Failed to load rules: {e}")
                    cls._rules = []
            else:
                # Default rules if the YAML doesn't exist yet
                print("Rules file not found. Using default rules.")
                cls._rules = cls.get_default_rules()
        return cls._rules

    @classmethod
    def load_ml_model(cls):
        if cls._ml_model is None:
            if os.path.exists(RISK_CLASSIFIER_PATH):
                try:
                    with open(RISK_CLASSIFIER_PATH, 'rb') as f:
                        cls._ml_model = pickle.load(f)
                        print(f"Loaded ML risk classifier from {RISK_CLASSIFIER_PATH}.")
                except Exception as e:
                    print(f"Failed to load ML risk classifier: {e}")
                    cls._ml_model = None
            else:
                print("ML risk classifier pickle not found. ML-based risk detection will be bypassed until trained.")
                cls._ml_model = None
        return cls._ml_model

    @classmethod
    def scan_chunk(cls, text: str, page_number: int) -> List[Dict[str, Any]]:
        """
        Scans a chunk of text for compliance risks using both YAML rules and the ML classifier.
        Returns a list of detected risk matches.
        """
        matches = []
        rules = cls.load_rules()
        ml_model = cls.load_ml_model()

        # 1. Rule-Based Scanning
        text_lower = text.lower()
        matched_rule_ids = set()
        
        for rule in rules:
            rule_id = rule.get("id")
            keywords = rule.get("keywords", [])
            
            # Simple keyword matching
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.append({
                        "clause_text": text,
                        "rule_id": rule_id,
                        "category": rule.get("category"),
                        "severity": rule.get("severity"),
                        "source": "Rule",
                        "confidence": 1.0,
                        "page_number": page_number
                    })
                    matched_rule_ids.add(rule_id)
                    break  # Matched this rule once for this chunk, move to next rule

        # 2. ML-Based Scanning (if model available)
        if ml_model:
            try:
                # Expecting ml_model is a Pipeline containing vectorizer + classifier
                prediction = ml_model.predict([text])[0]
                probabilities = ml_model.predict_proba([text])[0]
                
                # Assume classes are ['Compliant', 'Liability', 'Term', 'Compliance'] or similar
                class_labels = ml_model.classes_
                pred_idx = list(class_labels).index(prediction)
                prob = float(probabilities[pred_idx])

                # If the predicted class is a Risk category and probability is high
                if prediction != "Compliant" and prob > 0.65:
                    # Map class to severity
                    severity = "Medium"
                    if prediction == "Liability":
                        severity = "High"
                    
                    matches.append({
                        "clause_text": text,
                        "rule_id": f"ml_{prediction.lower()}",
                        "category": prediction,
                        "severity": severity,
                        "source": "ML",
                        "confidence": prob,
                        "page_number": page_number
                    })
            except Exception as e:
                print(f"ML risk classifier prediction error: {e}")

        # Deduplicate matches of the exact same category and source in the same chunk
        unique_matches = []
        seen = set()
        for m in matches:
            key = (m["category"], m["source"])
            if key not in seen:
                seen.add(key)
                unique_matches.append(m)

        return unique_matches

    @staticmethod
    def get_default_rules() -> List[Dict[str, Any]]:
        return [
            {
                "id": "unlimited_liability",
                "name": "Unlimited Liability Clause",
                "category": "Liability",
                "severity": "High",
                "keywords": ["unlimited liability", "shall not be limited", "liability is unlimited", "no cap on liability", "indemnify without limit"],
                "description": "Flags clauses that expose the company to unlimited financial or legal damages."
            },
            {
                "id": "auto_renewal",
                "name": "Automatic Contract Renewal",
                "category": "Term",
                "severity": "Medium",
                "keywords": ["auto-renew", "automatically renew", "tacit renewal", "automatic extension", "renew automatically"],
                "description": "Flags clauses that cause the contract to auto-renew unless active cancelation occurs."
            },
            {
                "id": "no_audit",
                "name": "No Audit Rights",
                "category": "Compliance",
                "severity": "High",
                "keywords": ["no audit rights", "audit is prohibited", "shall not audit", "waives audit rights", "restricted access to audit"],
                "description": "Flags clauses that deny the ability to inspect the vendor's records or facilities for compliance."
            },
            {
                "id": "ip_ownership",
                "name": "Intellectual Property Transfer",
                "category": "Compliance",
                "severity": "Medium",
                "keywords": ["waives all rights", "transfer all intellectual property", "assigns intellectual property", "sole ownership of vendor"],
                "description": "Flags clauses transfering IP rights of custom-built software or assets back to the vendor."
            }
        ]
