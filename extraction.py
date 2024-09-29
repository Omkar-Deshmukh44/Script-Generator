import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def extract_policies_and_remediation_paths(text):
    """Extract policies and their remediation paths."""
    policies = []
    remediation_paths = []

    # Regular expression to find policy titles
    policy_pattern = re.compile(r'\d+\.\d+\.\d+\s+\(L[1-2]\)\s+Ensure\s[\'"](.*?)[\'"]')
    # Regular expression to find remediation paths, assuming it starts with "Remediation:"
    remediation_pattern = re.compile(r'Remediation:([\s\S]*?)(?=\n\s*\d+\.\d+\.\d+|\Z)', re.MULTILINE)

    policy_matches = policy_pattern.findall(text)
    remediation_matches = remediation_pattern.findall(text)

    for match in policy_matches:
        policies.append(match.strip())

    for match in remediation_matches:
        cleaned_path = " ".join(match.split()).strip()
        remediation_paths.append(cleaned_path)

    return policies, remediation_paths
