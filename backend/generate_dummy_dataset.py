# pyrefly: ignore [missing-import]
import os
import yaml
import pickle
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Base Paths
BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
MODELS_DIR = BACKEND_DIR / "app" / "models"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def write_risk_rules():
    rules_data = {
        "rules": [
            {
                "id": "unlimited_liability",
                "name": "Unlimited Liability Clause",
                "category": "Liability",
                "severity": "High",
                "keywords": [
                    "unlimited liability", 
                    "shall not be limited", 
                    "liability is unlimited", 
                    "no cap on liability", 
                    "indemnify without limit",
                    "consequential damages without limitation"
                ],
                "description": "Flags clauses that expose the company to unlimited financial or legal damages."
            },
            {
                "id": "auto_renewal",
                "name": "Automatic Contract Renewal",
                "category": "Term",
                "severity": "Medium",
                "keywords": [
                    "auto-renew", 
                    "automatically renew", 
                    "tacit renewal", 
                    "automatic extension", 
                    "renew automatically",
                    "automatic roll-over"
                ],
                "description": "Flags clauses that cause the contract to auto-renew unless active cancelation occurs."
            },
            {
                "id": "no_audit",
                "name": "No Audit Rights",
                "category": "Compliance",
                "severity": "High",
                "keywords": [
                    "no audit rights", 
                    "audit is prohibited", 
                    "shall not audit", 
                    "waives audit rights", 
                    "restricted access to audit",
                    "no inspection of facilities"
                ],
                "description": "Flags clauses that deny the ability to inspect the vendor's records or facilities for compliance."
            },
            {
                "id": "ip_ownership",
                "name": "Intellectual Property Transfer",
                "category": "Compliance",
                "severity": "Medium",
                "keywords": [
                    "waives all rights", 
                    "transfer all intellectual property", 
                    "assigns intellectual property", 
                    "sole ownership of vendor",
                    "retain all intellectual property rights"
                ],
                "description": "Flags clauses transfering IP rights of custom-built software or assets back to the vendor."
            }
        ]
    }
    
    rules_path = DATA_DIR / "risk_rules.yaml"
    with open(rules_path, 'w') as f:
        yaml.safe_dump(rules_data, f)
    print(f"Generated risk rules at {rules_path}")

def generate_pdf(filename: str, title: str, paragraphs: list):
    pdf_path = DOCUMENTS_DIR / filename
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=10
    )

    story = [
        Paragraph(title, title_style),
        Spacer(1, 12)
    ]
    
    for p in paragraphs:
        story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    print(f"Generated PDF: {filename}")

def build_dummy_pdfs():
    # 5 HR Policies
    hr_docs = [
        (
            "HR_Policy_01_General_Conduct.pdf", 
            "Employee Code of Conduct and Workplace Policies",
            [
                "This document outlines the standard conduct guidelines expected from all employees at our organization. We aim to maintain a professional, respectful, and safe work environment.",
                "Employees are expected to arrive on time, act with integrity, and maintain a high standard of professional performance. Regular attendance is key to our operational success.",
                "Intellectual Property Policy: The employee acknowledges that any intellectual property developed during the course of employment is owned solely by the employer. The employee hereby waives all rights to such creations.",
                "Failure to comply with these conduct guidelines may result in disciplinary action up to and including termination of employment."
            ]
        ),
        (
            "HR_Policy_02_Leave_Management.pdf",
            "Leave of Absence and Attendance Policy",
            [
                "Our leave policy covers paid time off, sick leave, parental leave, and other leaves of absence. Full-time employees accrue 1.5 days of PTO per month.",
                "Employees must request planned leave at least two weeks in advance. Unplanned sick leave should be reported before 9:00 AM on the day of absence.",
                "Standard operating guidelines apply to leave approval. In case of an emergency, please notify HR immediately.",
                "Automatic roll-over of unused leave will occur on December 31st, up to a maximum of 5 business days. Any unused leaves exceeding this limit will expire."
            ]
        ),
        (
            "HR_Policy_03_Work_From_Home.pdf",
            "Remote Work and WFH Policy Guidelines",
            [
                "This policy defines eligibility and expectations for employees working from home. Eligible roles may work remotely up to 3 days per week with manager approval.",
                "Employees must maintain a secure, private workstation and ensure reliable internet connectivity during standard working hours.",
                "Communication should remain prompt. Standard response times on team chat and emails should not exceed one hour during the work day.",
                "Compliance scanning: To ensure remote worker compliance, the employee waives all rights to privacy on their home networks. The IT team reserves the right to audit and run compliance monitoring tools on private networks without restriction."
            ]
        ),
        (
            "HR_Policy_04_Social_Media.pdf",
            "Social Media Usage Policy for Employees",
            [
                "Employees are representatives of our brand. When posting on social media, employees must make it clear that opinions expressed are their own.",
                "Do not post confidential company information, client trade secrets, or project code repositories to public forums or social networks.",
                "Respectful online engagement is required. Harassment, discrimination, or hate speech posted online will result in immediate termination.",
                "This policy applies both during and outside of normal work hours, ensuring a high standard of external brand protection."
            ]
        ),
        (
            "HR_Policy_05_Performance_Review.pdf",
            "Employee Performance Evaluation Guidelines",
            [
                "Performance reviews are conducted annually in Q4. Goals are set collaboratively at the start of the fiscal year.",
                "Reviews are designed to support professional growth, outline performance improvements, and determine merit-based compensation changes.",
                "We provide regular feedback cycles to ensure transparency and accountability. Managers are required to check in bi-weekly.",
                "Promotions and salary adjustments are based on performance, budget availability, and market competitiveness."
            ]
        )
    ]

    # 5 Vendor Contracts
    contract_docs = [
        (
            "Vendor_Contract_01_Acme_Software.pdf",
            "Software License and Vendor Service Agreement",
            [
                "This Software License Agreement is made between Acme Software Inc. ('Vendor') and the Client. The Vendor grants a non-exclusive license to use the platform.",
                "Service Level Agreement: The Vendor guarantees a platform uptime of 99.9%. Scheduled maintenance will occur only on weekends with 48 hours notification.",
                "Indemnification and Liability: The Vendor's total liability under this agreement shall be capped at the fees paid in the previous 12 months.",
                "Term and Termination: This agreement is valid for 1 year. The contract will auto-renew for successive 1-year terms unless either party gives written notice of termination 60 days prior to renewal."
            ]
        ),
        (
            "Vendor_Contract_02_TechConsulting.pdf",
            "Consulting Services and Master Agreement",
            [
                "This agreement is entered into for the provision of professional consulting and software development services by TechConsulting Group.",
                "Intellectual Property: All software, frameworks, and documents developed during this engagement shall remain the sole ownership of vendor, and client shall receive only a limited use license.",
                "Liability Terms: In no event shall either party's liability exceed $50,000, except for breaches of confidentiality or gross negligence.",
                "Termination: Either party may terminate this agreement with 30 days written notice. Payment for completed milestones is due immediately upon termination."
            ]
        ),
        (
            "Vendor_Contract_03_CloudData_Storage.pdf",
            "Cloud Storage and Managed Services Contract",
            [
                "This Contract outlines the terms for cloud storage hosting provided by CloudData Storage Systems. Data will be hosted in secure, redundant facilities.",
                "Security Audits: The vendor maintains strict security protocols. However, the client agrees that the client waives all audit rights. The client is prohibited from performing independent compliance audits or inspecting vendor facilities.",
                "Unlimited Liability: Notwithstanding anything to the contrary, the Client shall have unlimited liability for any breaches of system security or data access policies caused by its users.",
                "Billing Terms: Payments are processed monthly. Late payments accrue interest at 1.5% per month."
            ]
        ),
        (
            "Vendor_Contract_04_LogisticsCorp.pdf",
            "Logistics and Supply Chain Distribution Agreement",
            [
                "LogisticsCorp agrees to perform shipping and distribution services as specified in Exhibit A. Standard delivery timelines apply.",
                "Risk of Loss: Risk of loss or damage to goods passes to the Client upon delivery to the carrier at our distribution center.",
                "Insurance Requirements: LogisticsCorp shall maintain commercial general liability insurance of at least $2,000,000 during the contract term.",
                "This agreement shall renew automatically for successive periods of three years, creating a tacit renewal unless canceled 90 days in advance."
            ]
        ),
        (
            "Vendor_Contract_05_Facilities_Management.pdf",
            "Office Facilities Maintenance and Cleaning Contract",
            [
                "This Service Agreement covers standard cleaning, landscaping, and office maintenance services for the Client's corporate offices.",
                "Fees and Expenses: The monthly fee is fixed as stated in Exhibit B. Out-of-pocket expenses must be pre-approved by the Client.",
                "Audit Clause: The Client reserves the right to audit service logs and invoices. The Vendor shall provide access to records within 5 business days.",
                "Governing Law: This agreement shall be governed by and construed in accordance with the laws of the State of Delaware."
            ]
        )
    ]

    # 5 Security SOPs
    sop_docs = [
        (
            "Security_SOP_01_Access_Control.pdf",
            "Identity and Access Control Standard Operating Procedure",
            [
                "This SOP establishes the guidelines for access controls to production servers and critical database infrastructures.",
                "Access is granted on the principle of least privilege. All users must authenticate via Multi-Factor Authentication (MFA).",
                "Password requirements: Passwords must be at least 12 characters long, containing uppercase, lowercase, numbers, and special characters.",
                "Accounts will be locked after 5 failed login attempts. Suspended accounts must be verified by the Security Operations Center (SOC)."
            ]
        ),
        (
            "Security_SOP_02_Incident_Response.pdf",
            "Cybersecurity Incident Response Plan and SOP",
            [
                "This SOP provides structured procedures for detecting, responding to, and recovering from cybersecurity incidents.",
                "Incident classification: Incidents are categorized from Level 1 (Low) to Level 4 (Critical). SOC must be alerted within 15 minutes of detection.",
                "Forensics and Auditing: The incident team must collect and preserve system logs. Under no circumstances should audit logs be modified or deleted.",
                "Review and Updates: The incident response plan must be reviewed annually and updated to incorporate lessons learned from tabletop exercises."
            ]
        ),
        (
            "Security_SOP_03_Data_Encryption.pdf",
            "Data Encryption and Privacy SOP",
            [
                "All customer data must be encrypted both in transit and at rest. Encryption protocols must use industry-standard algorithms.",
                "Data in transit must be encrypted using TLS 1.3. Data at rest must use AES-256 encryption keys.",
                "Key Management: Encryption keys must be rotated every 90 days. Key storage databases must have restricted access controls.",
                "No inspection: To protect database secrets, we enforce a strict policy where no audit rights are granted, and no inspection of encryption modules is allowed."
            ]
        ),
        (
            "Security_SOP_04_Patch_Management.pdf",
            "System Patching and Vulnerability SOP",
            [
                "This SOP defines timelines for applying security patches to servers, network appliances, and developer workstations.",
                "Critical patches must be applied within 72 hours of release. High-risk patches must be applied within 14 days.",
                "A vulnerability scan must be conducted weekly. Identified risks must be logged and tracked in the security registry.",
                "System rollback plans must be prepared prior to patch deployment to ensure high availability in case of deployment failure."
            ]
        ),
        (
            "Security_SOP_05_Vendor_Assessment.pdf",
            "Third-Party Vendor Risk Assessment SOP",
            [
                "All third-party vendors must undergo a security risk assessment before integration into production systems.",
                "Vendors must complete the Security Questionnaire and provide a SOC 2 Type II report representing external compliance.",
                "Contracts with vendors must contain standard indemnity clauses, audit permissions, and SLA uptime guarantees.",
                "Annual reviews of critical vendors will be conducted. Vendors failing to meet security criteria will face contract termination."
            ]
        )
    ]

    all_docs = hr_docs + contract_docs + sop_docs
    for filename, title, paragraphs in all_docs:
        generate_pdf(filename, title, paragraphs)

def train_risk_classifier():
    # Labeled clauses for training
    training_data = [
        # Liability Risk
        ("The vendor's liability shall not be limited for any damages under this agreement.", "Liability"),
        ("The client agrees to provide unlimited liability for any systemic failures.", "Liability"),
        ("There is no cap on liability for breaches of confidentiality.", "Liability"),
        ("The contractor accepts unlimited liability for consequential damages without limitation.", "Liability"),
        ("Notwithstanding anything else, client indemnifies vendor without limit.", "Liability"),
        ("The vendor shall hold the buyer harmless and accept full unlimited liability.", "Liability"),
        
        # Term Risk
        ("This agreement will automatically renew for successive one-year periods.", "Term"),
        ("The contract auto-renews unless written cancelation is received 30 days prior.", "Term"),
        ("This agreement shall renew automatically for consecutive terms.", "Term"),
        ("A tacit renewal clause applies, automatically extending the contract.", "Term"),
        ("Unless either party cancels, the agreement will auto-renew annually.", "Term"),
        ("The license key will automatically roll-over into a new subscription term.", "Term"),
        
        # Compliance Risk (No audit / IP waiving)
        ("The client waives all audit rights to inspect the vendor's records.", "Compliance"),
        ("Audit is prohibited and client shall not inspect vendor systems.", "Compliance"),
        ("Under this SOP, no audit rights are granted to external compliance officers.", "Compliance"),
        ("The buyer waives all rights and transfers all intellectual property.", "Compliance"),
        ("Sole ownership of all software and tools belongs to the vendor.", "Compliance"),
        ("The vendor retains all intellectual property rights and client gets no code.", "Compliance"),
        ("No audit rights or inspection of facilities is allowed for the client.", "Compliance"),
        
        # Compliant / Safe text
        ("The company values and protects the privacy and data security of all clients.", "Compliant"),
        ("This policy outlines the standard rules of conduct expected from our staff.", "Compliant"),
        ("Passwords must be at least 12 characters in length for system access.", "Compliant"),
        ("The client reserves the right to audit records upon reasonable notice.", "Compliant"),
        ("Each party retains its pre-existing intellectual property rights.", "Compliant"),
        ("Either party may terminate the agreement for convenience with 30 days notice.", "Compliant"),
        ("The vendor's liability is capped at the total amount paid by the client.", "Compliant"),
        ("This agreement is valid for a period of two years from the effective date.", "Compliant"),
        ("We conduct annual evaluations of cybersecurity measures to keep systems safe.", "Compliant"),
        ("All employee records are kept strictly confidential by HR.", "Compliant"),
        ("The security operations center is responsible for monitoring network traffic.", "Compliant")
    ]
    
    X = [item[0] for item in training_data]
    y = [item[1] for item in training_data]
    
    # Simple Pipeline: TFIDF + Logistic Regression (multi_class='multinomial')
    model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True, stop_words='english')),
        ('clf', LogisticRegression(C=5.0, random_state=42))
    ])
    
    model.fit(X, y)
    
    model_path = MODELS_DIR / "risk_classifier.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Trained ML risk classifier and saved to {model_path}")

if __name__ == "__main__":
    print("Generating compliance intelligence dataset...")
    write_risk_rules()
    build_dummy_pdfs()
    train_risk_classifier()
    print("Dataset generation complete!")
