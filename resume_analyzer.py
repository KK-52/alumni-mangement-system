import pandas as pd
import spacy
import fitz  # PyMuPDF for PDF extraction
import os

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Define the applications file
APPLICATIONS_FILE = "applications.csv"

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with fitz.open(pdf_path) as doc:
            text = "\n".join([page.get_text("text") for page in doc])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def analyze_resume(resume_text):
    """Analyze resume text to extract key details."""
    doc = nlp(resume_text)

    # Extract skills (keywords, entities, or patterns)
    skills = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    
    # Extract years of experience (basic pattern matching)
    experience = []
    for ent in doc.ents:
        if ent.label_ in ["DATE", "TIME"]:
            experience.append(ent.text)

    # Generate a summary (first 2 sentences)
    summary = " ".join([sent.text for sent in doc.sents][:2])

    return {
        "Skills": ", ".join(skills[:10]),  # Limiting to top 10 skills
        "Experience": ", ".join(experience[:5]),  # Limiting to top 5 dates
        "Summary": summary
    }

def process_resumes():
    """Process all resumes in the applications file."""
    if not os.path.exists(APPLICATIONS_FILE):
        print("No applications file found.")
        return None

    df = pd.read_csv(APPLICATIONS_FILE)

    if "ATTACHED RESUME" not in df.columns:
        print("No resumes found in applications file.")
        return None

    results = []
    for _, row in df.iterrows():
        resume_path = row["ATTACHED RESUME"]
        if pd.notna(resume_path) and os.path.exists(resume_path):
            resume_text = extract_text_from_pdf(resume_path)
            if resume_text:
                analysis = analyze_resume(resume_text)
                results.append({
                    "Company": row["COMPANY NAME"],
                    "Role": row["ROLE"],
                    "Qualification": row["QUALIFICATION"],
                    "Skills": analysis["Skills"],
                    "Experience": analysis["Experience"],
                    "Summary": analysis["Summary"],
                    "Resume Path": resume_path
                })

    return pd.DataFrame(results)

if __name__ == "__main__":
    df_results = process_resumes()
    if df_results is not None:
        print(df_results.head())  # Print the first few analyzed resumes
