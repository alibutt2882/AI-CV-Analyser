# 🧬 Neon CV Analyser

An AI-powered CV/resume analyser built with **Streamlit**, a **scikit-learn**
text classification model, and a **SQLite**-backed login/register system —
wrapped in a Neon Dark/Light themed UI.

Developed by **Ali Haider Butt**.

---

## What's included

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app (routing, login/register, analyser, about, settings) |
| `database.py` | SQLite user auth (register/login, salted+hashed passwords) |
| `model_utils.py` | Loads the trained model, extracts text from PDF/DOCX/TXT, predicts category, matches skills |
| `theme.py` | Neon Dark/Light CSS theme injected on every page |
| `train_model.py` | Script used to train the classifier from the 3 CSV datasets |
| `models/` | Trained artifacts (TF-IDF vectorizer, classifier, label list, skills vocabulary, metrics) — **already trained**, no need to retrain |
| `data/` | The 3 source CSVs used for training |
| `requirements.txt` | Python dependencies |

## Model details

- **Data**: Combined `UpdatedResumeDataSet.csv` + `Resume.csv` (~3,441 cleaned resumes, 45 job categories). `resume_data.csv` was used to build a master vocabulary of ~3,186 known skills for skill-matching.
- **Pipeline**: TF-IDF (unigrams+bigrams, 6000 features) → Logistic Regression (`class_weight="balanced"`).
- **Test accuracy**: ~77% across 45 categories (see `models/metrics.json`).

If you want to retrain (e.g. after adding more data), just run:

```bash
python train_model.py
```

This regenerates everything inside `models/`.

## How to run

1. **Install dependencies** (Python 3.10+ recommended):

```bash
pip install -r requirements.txt
```

2. **Run the app**:

```bash
streamlit run app.py
```

3. Open the URL Streamlit prints (usually `http://localhost:8501`).

4. **Register** a new account (username + email + password), then **log in**
   with your email + password.

5. Go to **CV Analyser**, upload a PDF/DOCX/TXT resume (or paste text), and
   click **Analyse CV** to see:
   - the predicted job category + confidence
   - top-5 matching categories chart
   - matched skills as neon badges
   - basic CV stats (word count, email/phone detection)

6. Use **Settings** in the sidebar to switch between **Dark Neon** and
   **Light Neon** themes, or to log out.

7. Check the **About App** page for app details and developer info.

## Notes

- `users.db` (SQLite) is created automatically on first run in the project
  folder — it stores usernames, emails, salts, and SHA-256 password hashes
  (never plain-text passwords).
- The neon theme is applied globally via injected CSS in `theme.py`, so it
  stays consistent across the login, register, analyser, about, and settings
  pages.
- The classifier is a demo-grade model (77% accuracy on 45 fine-grained
  categories) — good enough to show meaningful predictions, but for
  production use you'd want more labeled data per category and possibly a
  transformer-based embedding model.
  #############################################################
# {cd "C:\Users\REHMAT COMPUTERS\Downloads\neon_cv_analyser"

# create a clean virtual environment (use whichever python you'll run the app with)
python -m venv venv
venv\Scripts\activate

# install the pinned dependencies into it
pip install -r requirements.txt

# delete the old pickle files (they were built with a different sklearn version)
del models\category_model.pkl
del models\tfidf_vectorizer.pkl

# retrain inside this venv, so the new .pkl files match this venv's sklearn version
python train_model.py

# run the app with the SAME venv
streamlit run app.py}