"""
model_utils.py
---------------
Utility functions used by the Streamlit app to:
  1. Load the trained TF-IDF + Logistic Regression model (cached).
  2. Clean / extract text from uploaded CVs (.pdf, .docx, .txt).
  3. Predict the most likely job category + top-N probabilities.
  4. Match skills found in the CV text against the master skills vocabulary.
"""

import re
import json
import joblib
import numpy as np
import io

import PyPDF2
import docx

MODEL_DIR = "models"


# --------------------------------------------------------------------------
# TEXT CLEANING (must match the cleaning used in train_model.py)
# --------------------------------------------------------------------------
URL_RE = re.compile(r"http\S+|www\S+")
NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")
MULTI_SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = URL_RE.sub(" ", text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = NON_ALPHA_RE.sub(" ", text)
    text = MULTI_SPACE_RE.sub(" ", text).strip().lower()
    return text


# --------------------------------------------------------------------------
# LOADING TRAINED ARTIFACTS
# --------------------------------------------------------------------------
def load_artifacts():
    """Load vectorizer, model, label classes, skills vocabulary and metrics."""
    vectorizer = joblib.load(f"{MODEL_DIR}/tfidf_vectorizer.pkl")
    model = joblib.load(f"{MODEL_DIR}/category_model.pkl")
    labels = joblib.load(f"{MODEL_DIR}/label_classes.pkl")
    skills_master = joblib.load(f"{MODEL_DIR}/skills_master.pkl")
    with open(f"{MODEL_DIR}/metrics.json") as f:
        metrics = json.load(f)
    return vectorizer, model, labels, skills_master, metrics


# --------------------------------------------------------------------------
# FILE TEXT EXTRACTION
# --------------------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs)


def extract_text(uploaded_file) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    `uploaded_file` is a Streamlit UploadedFile object.
    """
    name = uploaded_file.name.lower()
    raw_bytes = uploaded_file.read()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(raw_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(raw_bytes)
    elif name.endswith(".txt"):
        return raw_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


# --------------------------------------------------------------------------
# PREDICTION
# --------------------------------------------------------------------------
def predict_category(raw_text: str, vectorizer, model, top_n: int = 5):
    """
    Predict the most likely job categories for a given resume text.
    Returns a list of (label, probability) tuples sorted descending, length top_n.
    """
    cleaned = clean_text(raw_text)
    vec = vectorizer.transform([cleaned])
    probs = model.predict_proba(vec)[0]
    classes = model.classes_

    ranked = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


# --------------------------------------------------------------------------
# SKILL MATCHING
# --------------------------------------------------------------------------
def match_skills(raw_text: str, skills_master: list, limit: int = 40) -> list:
    """
    Find which known skills (from the master vocabulary) appear in the CV text.
    Simple case-insensitive whole-word / phrase matching.
    """
    text_lower = raw_text.lower()
    found = []
    for skill in skills_master:
        skill_l = skill.lower().strip()
        if not skill_l:
            continue
        # word-boundary match so "R" doesn't match inside "Marketing", etc.
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill_l) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
        if len(found) >= limit:
            break
    return found


def basic_cv_stats(raw_text: str) -> dict:
    """Compute a few simple, useful stats about the CV for the dashboard."""
    words = raw_text.split()
    return {
        "word_count": len(words),
        "char_count": len(raw_text),
        "has_email": bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)),
        "has_phone": bool(re.search(r"(\+?\d[\d\-\s]{8,}\d)", raw_text)),
    }
