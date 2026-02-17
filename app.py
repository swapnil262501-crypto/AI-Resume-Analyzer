from flask import Flask, render_template, request
import PyPDF2
import re

app = Flask(__name__)

# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# ---------- BASIC INFO EXTRACTION ----------
def extract_emails(text):
    return list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)))

def extract_phone_numbers(text):
    return list(set(re.findall(r'\+?\d[\d\s\-]{8,}\d', text)))

# ---------- SECTION EXTRACTION ----------
def extract_section(text, section_names):
    lines = text.split("\n")
    extracted_content = []
    capture = False

    for line in lines:
        clean_line = line.strip()
        if any(section.lower() in clean_line.lower() for section in section_names):
            capture = True
            continue
        if capture and re.match(r'^[A-Z ]{3,}$', clean_line):
            break
        if capture and clean_line != "":
            if clean_line not in extracted_content:
                extracted_content.append(clean_line)
    return extracted_content

# ---------- ROUTES ----------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if 'resume' not in request.files:
        return "No file uploaded", 400
    file = request.files['resume']
    if file.filename == '':
        return "No file selected", 400

    text = extract_text_from_pdf(file)

    education_section = extract_section(text, [
        "Education",
        "Academic Background",
        "Academic Qualifications",
        "Educational Qualification",
        "Qualifications"
    ])

    skills_section = extract_section(text, [
        "Skills",
        "Technical Skills",
        "Core Competencies",
        "Professional Skills",
        "Key Skills"
    ])

    emails = extract_emails(text)
    phones = extract_phone_numbers(text)

    structured_text = []
    for line in text.split("\n"):
        clean_line = line.strip()
        if clean_line != "" and clean_line not in structured_text:
            structured_text.append(clean_line)

    info = {
        "email": emails,
        "phone": phones,
        "education": education_section,
        "skills": skills_section
    }

    return render_template('result.html', info=info, structured_text=structured_text)

if __name__ == "__main__":
    app.run(debug=True)
