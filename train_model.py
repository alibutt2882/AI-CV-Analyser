"""
train_model.py
----------------
Trains the Resume/CV category classification model used by the Streamlit
CV Analyser app.

Datasets used:
  1. data/UpdatedResumeDataSet.csv  -> columns: Category, Resume
  2. data/Resume.csv                -> columns: ID, Resume_str, Resume_html, Category
  3. data/resume_data.csv           -> used only to build the master "skills"
                                        vocabulary (not used for classification
                                        labels, since its schema is different -
                                        it is a job/resume matching dataset).

Output artifacts (saved into models/):
  - tfidf_vectorizer.pkl : fitted TF-IDF vectorizer
  - category_model.pkl   : trained classifier (Logistic Regression)
  - label_classes.pkl    : sorted list of category labels (index -> label)
  - skills_master.pkl    : master list of known skills, used by the app to
                            highlight / match skills found inside a CV
  - metrics.json         : train/test accuracy + report, so the app can show
                            "model trained on X resumes, Y% accuracy" on the About page
"""

import re
import json
import ast
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# --------------------------------------------------------------------------
# 1. TEXT CLEANING HELPER
# --------------------------------------------------------------------------
URL_RE = re.compile(r"http\S+|www\S+")
NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")
MULTI_SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Lowercase, strip urls / special chars / extra whitespace from raw resume text."""
    if not isinstance(text, str):
        return ""
    text = URL_RE.sub(" ", text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = NON_ALPHA_RE.sub(" ", text)
    text = MULTI_SPACE_RE.sub(" ", text).strip().lower()
    return text


def normalize_label(label: str) -> str:
    """Turn 'INFORMATION-TECHNOLOGY' or 'Data Science' into a consistent Title Case label."""
    label = str(label).replace("-", " ").replace("_", " ").strip()
    return " ".join(w.capitalize() for w in label.split())


# --------------------------------------------------------------------------
# 2. LOAD + COMBINE DATASETS
# --------------------------------------------------------------------------
print("Loading datasets ...")

df1 = pd.read_csv("data/UpdatedResumeDataSet.csv")
df1 = df1.rename(columns={"Resume": "text", "Category": "category"})[["text", "category"]]

df2 = pd.read_csv("data/Resume.csv")
df2 = df2.rename(columns={"Resume_str": "text", "Category": "category"})[["text", "category"]]

combined = pd.concat([df1, df2], ignore_index=True)
combined["category"] = combined["category"].apply(normalize_label)
combined["clean_text"] = combined["text"].apply(clean_text)

# Drop empty / too-short resumes after cleaning
combined = combined[combined["clean_text"].str.split().str.len() > 15].reset_index(drop=True)

print(f"Total resumes after cleaning: {len(combined)}")
print(f"Number of categories: {combined['category'].nunique()}")

# --------------------------------------------------------------------------
# 3. BUILD MASTER SKILLS VOCABULARY (from resume_data.csv 'skills' column)
# --------------------------------------------------------------------------
print("Building master skills vocabulary ...")

skills_df = pd.read_csv("data/resume_data.csv", usecols=["skills"])

skill_set = set()
for raw in skills_df["skills"].dropna():
    try:
        # skills column is stored as a stringified python list, e.g. "['Python', 'SQL']"
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            for s in parsed:
                s = str(s).strip()
                if 1 < len(s) <= 40:
                    skill_set.add(s)
    except (ValueError, SyntaxError):
        continue

skills_master = sorted(skill_set)
print(f"Master skills vocabulary size: {len(skills_master)}")

# --------------------------------------------------------------------------
# 4. TRAIN / TEST SPLIT
# --------------------------------------------------------------------------
X = combined["clean_text"]
y = combined["category"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --------------------------------------------------------------------------
# 5. TF-IDF VECTORIZATION
# --------------------------------------------------------------------------
print("Fitting TF-IDF vectorizer ...")
vectorizer = TfidfVectorizer(
    max_features=6000,
    stop_words="english",
    ngram_range=(1, 2),
    sublinear_tf=True,
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# --------------------------------------------------------------------------
# 6. TRAIN CLASSIFIER
# --------------------------------------------------------------------------
print("Training Logistic Regression classifier ...")
model = LogisticRegression(
    max_iter=2000,
    C=5.0,
    class_weight="balanced",
    n_jobs=-1,
)
model.fit(X_train_vec, y_train)

# --------------------------------------------------------------------------
# 7. EVALUATE
# --------------------------------------------------------------------------
y_pred = model.predict(X_test_vec)
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, zero_division=0)

print(f"\nTest Accuracy: {acc:.4f}\n")
print(report)

# --------------------------------------------------------------------------
# 8. SAVE ARTIFACTS
# --------------------------------------------------------------------------
print("Saving model artifacts to models/ ...")
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
joblib.dump(model, "models/category_model.pkl")
joblib.dump(sorted(y.unique().tolist()), "models/label_classes.pkl")
joblib.dump(skills_master, "models/skills_master.pkl")

metrics = {
    "num_resumes_trained": int(len(combined)),
    "num_categories": int(combined["category"].nunique()),
    "test_accuracy": round(float(acc), 4),
}
with open("models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\nDone. Artifacts saved:")
print(" - models/tfidf_vectorizer.pkl")
print(" - models/category_model.pkl")
print(" - models/label_classes.pkl")
print(" - models/skills_master.pkl")
print(" - models/metrics.json")
