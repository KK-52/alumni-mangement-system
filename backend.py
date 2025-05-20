from fastapi import FastAPI, UploadFile, File, Form
import fitz  # PyMuPDF
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
import re

app = FastAPI()
nlp = spacy.load("en_core_web_sm")  # For basic NLP
model = SentenceTransformer("all-MiniLM-L6-v2")  # Semantic search model

resumes = {}  # Stores resumes {"filename": "text"}
embeddings = {}  # Stores embeddings {"filename": embedding}
requirements = {}  # Stores job requirements {"requirement_name": embedding}
summaries = {}  # Stores resume summaries {"filename": "summary text"}

# Function to extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file, filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

# Function to extract skills from resume text
def extract_skills(text):
    skill_keywords = [
        "Python", "Java", "C++", "TensorFlow", "PyTorch", "NumPy", "Pandas", "Scikit-learn",
        "Machine Learning", "Deep Learning", "NLP", "Cloud", "Azure", "AWS", "SQL", "NoSQL",
        "MongoDB", "PostgreSQL", "Flask", "Django", "Keras", "Git", "GitHub", "React",
        "Node.js", "Express.js", "HTML", "CSS", "JavaScript", "Docker", "Kubernetes"
    ]

    # Normalize text
    text = text.lower()
    
    # Extract matching skills
    extracted_skills = {skill for skill in skill_keywords if skill.lower() in text}
    
    return list(extracted_skills)

# Function to generate a concise summary
def summarize_resume(text):
    doc = nlp(text)
    
    # Extract key entities (skills, tools, technologies)
    skills = extract_skills(text)
    
    # Extract most relevant experience-related sentences
    experience_sentences = [sent.text for sent in doc.sents if "experience" in sent.text.lower() or "worked" in sent.text.lower()]
    
    # Construct summary
    summary = {
        "top_skills": skills[:10],  # Limit to 10 skills
        "experience_highlights": experience_sentences[:3]  # Limit to 3 key experience points
    }
    
    return summary

@app.post("/upload_resumes/")
async def upload_resumes(files: list[UploadFile] = File(...)):
    uploaded_files = []
    
    for file in files:
        content = await file.read()
        text = extract_text_from_pdf(content)
        resumes[file.filename] = text
        embeddings[file.filename] = model.encode(text, convert_to_tensor=True)
        
        # Generate and store summary
        summaries[file.filename] = summarize_resume(text)
        
        uploaded_files.append(file.filename)
    
    return {"message": "Resumes uploaded successfully", "uploaded_files": uploaded_files}

@app.post("/add_requirement/")
async def add_requirement(requirement_name: str = Form(...), description: str = Form(...)):
    requirements[requirement_name] = model.encode(description, convert_to_tensor=True)
    return {"message": "Requirement added successfully", "requirement_name": requirement_name}

@app.post("/recommend/")
async def recommend_candidates(requirement_name: str = Form(...)):
    lower_req_name = requirement_name.lower()

    # Find stored requirement (ignore case)
    matching_requirement = None
    for stored_name in requirements.keys():
        if stored_name.lower() == lower_req_name:
            matching_requirement = stored_name
            break  

    if not matching_requirement:
        return {"error": "Requirement not found"}

    requirement_embedding = requirements[matching_requirement]

    # Compute similarity scores
    ranked_candidates = sorted(
        [
            (
                filename,
                util.pytorch_cos_sim(requirement_embedding, emb).item()
            ) for filename, emb in embeddings.items()
        ],
        key=lambda x: x[1], reverse=True  # Sort in descending order
    )

    # Construct response with ranking & summaries
    recommendations = []
    for i, (filename, score) in enumerate(ranked_candidates):
        rank = i + 1
        summary = summaries.get(filename, {"top_skills": [], "experience_highlights": []})
        
        if score > 0.85:
            message = f"🏆 Resume '{filename}' is a **great fit** for the job!"
        elif score > 0.65:
            message = f"✅ Resume '{filename}' is a **good fit** for the job."
        else:
            message = f"⚠️ Resume '{filename}' has a **low match** with the job."

        recommendations.append(
            {
                "rank": rank,
                "resume": filename,
                "similarity_score": score,
                "message": message,
                "summary": summary
            }
        )

    return {"top_candidates": recommendations}
