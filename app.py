from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import fitz  # PyMuPDF
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def extract_policies_and_remediation_paths(text):
    """Extract policies from the PDF text."""
    policies = []
    policy_pattern = re.compile(r'\d+\.\d+\.\d+\s+\(L[1-2]\)\s+Ensure\s[\'"](.*?)[\'"]')
    policy_matches = policy_pattern.findall(text)

    for match in policy_matches:
        policies.append(match.strip())

    return policies

def generate_script(policy, audit_remediation, os):
    """Generate a script based on the policy, audit/remediation choice, and OS type."""
    if os == "Windows":
        script = f"# PowerShell script for {audit_remediation} policy: {policy}\n"
        script += "Write-Host 'Implementing the policy...'\n"
        script += f"Write-Host 'Policy: {policy}'\n"
    else:  # Assuming Linux
        script = f"# Shell script for {audit_remediation} policy: {policy}\n"
        script += "echo 'Implementing the policy...'\n"
        script += f"echo 'Policy: {policy}'\n"
    return script

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)

    # Extract policies
    policies = extract_policies_and_remediation_paths(text)

    return jsonify({'policies': policies})

@app.route('/generate_script', methods=['POST'])
def generate_script_route():
    data = request.get_json()
    policy = data.get('policy')
    audit_remediation = data.get('auditRemediation')
    os_type = data.get('os')

    if not policy or not audit_remediation or not os_type:
        return jsonify({'error': 'Incomplete data provided'}), 400

    # Generate script based on policy and selected options
    script = generate_script(policy, audit_remediation, os_type)

    return jsonify({'script': script})

if __name__ == '__main__':
    app.run(debug=True)
