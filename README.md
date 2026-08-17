<div align="center">

# 🧬 AI CV Analyser — Neon Edition

### AI-powered resume screening with a neon-drenched UI ✨

An end-to-end machine learning + web app that reads a CV, predicts the best-fit job category, extracts matching skills, and shows it all in a glowing Dark/Light neon interface — with secure login & registration built in.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-neon?style=for-the-badge&color=39FF14)](LICENSE)

[🚀 Live Demo](#-getting-started) · [📂 Repository](https://github.com/alibutt2882/AI_CV_Analyser) · [🐛 Report a Bug](https://github.com/alibutt2882/AI_CV_Analyser/issues) · [✨ Request a Feature](https://github.com/alibutt2882/AI_CV_Analyser/issues)

</div>

---

## 📖 About The Project

**AI CV Analyser** takes a resume (PDF, DOCX, TXT, or pasted text), runs it through a custom-trained **TF-IDF + Logistic Regression** model, and tells you:

- 🎯 the most likely job category the CV belongs to
- 📊 the top-5 closest matching categories with confidence scores
- 🛠️ which known professional/technical skills it detected
- 📈 quick CV stats — word count, contact info detection, and more

All wrapped in a **neon-themed** Streamlit interface with a **Dark Neon / Light Neon** toggle, and gated behind a proper **email + username + password** login system backed by SQLite.

---

## 🌟 Features

| | |
|---|---|
| 🔐 **Secure Auth** | Register & log in with email + username + password. Passwords are salted and SHA-256 hashed — never stored in plain text. |
| 📄 **Multi-format CV Input** | Upload `.pdf`, `.docx`, `.txt`, or just paste your resume text directly. |
| 🎯 **ML-Powered Category Prediction** | Trained on 3,400+ real resumes across **45 job categories**, ~77% test accuracy. |
| 🛠️ **Skill Matching** | Auto-detects and highlights ~3,000+ known professional/technical skills in the CV. |
| 📊 **CV Insights** | Word count, character count, and email/phone detection at a glance. |
| 🎨 **Neon Dark/Light Theme** | A consistent glowing neon UI across every page, switchable in Settings. |
| ⚡ **Single-file App** | The entire application lives in one `app.py` — easy to read, run, and deploy. |

---

## 🧠 How the Model Was Trained

```
📂 Data sources
 ├── UpdatedResumeDataSet.csv   → resume text + job category
 ├── Resume.csv                 → resume text + job category
 └── resume_data.csv            → used to build the master skills vocabulary

🔧 Pipeline
 Raw Text → Clean & Normalize → TF-IDF (uni+bigrams, 6000 features)
          → Logistic Regression (class-weighted) → 45-category classifier
```

| Metric | Value |
|---|---|
| Resumes trained on | **3,441** |
| Job categories | **45** |
| Test accuracy | **~77%** |
| Skills vocabulary size | **~3,186** |

---

## 🛠️ Tech Stack

- **Frontend/App:** [Streamlit](https://streamlit.io/)
- **ML:** [scikit-learn](https://scikit-learn.org/), [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/)
- **Database:** SQLite (built-in, zero setup)
- **File Parsing:** PyPDF2, python-docx
- **Styling:** Custom neon CSS injected directly into Streamlit

---

## 🚀 Getting Started

### 1️⃣ Clone the repo

```bash
git clone https://github.com/alibutt2882/AI_CV_Analyser.git
cd AI_CV_Analyser
```

### 2️⃣ Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the app 🚀

```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser 🎉

> ⚠️ **Note:** Always use the *same* Python environment for both training (`train_model.py`) and running the app (`streamlit run app.py`). Mixing environments (e.g. Anaconda vs. a standalone Python) can cause model-loading version errors.

### 🔁 (Optional) Retrain the model

The trained model is already included in `models/`, but if you want to retrain from scratch:

```bash
python train_model.py
```

---

## 📸 Screenshots

> *Add your own screenshots/GIFs here once deployed — Login page, CV Analyser results, and the neon theme toggle in action look great in a README!*

---

## 🗂️ Project Structure

```
AI_CV_Analyser/
├── app.py               # 🧬 The entire app: auth, theme, model, UI
├── train_model.py        # 🏋️ One-time script to train the classifier
├── requirements.txt       # 📦 Pinned dependencies
├── models/                 # 🤖 Trained model artifacts
│   ├── tfidf_vectorizer.pkl
│   ├── category_model.pkl
│   ├── label_classes.pkl
│   ├── skills_master.pkl
│   └── metrics.json
├── data/                    # 📊 Training datasets
└── README.md
```

---

## 🗺️ Roadmap

- [ ] 📈 Add a "Model Info" page with full per-category precision/recall
- [ ] ☁️ One-click deploy button (Streamlit Community Cloud)
- [ ] 🌐 Multi-language resume support
- [ ] 🧾 Downloadable PDF analysis report
- [ ] 🔑 OAuth login (Google/GitHub)

Have an idea? [Open an issue](https://github.com/alibutt2882/AI_CV_Analyser/issues) 💡

---

## 🤝 Contributing

Contributions are welcome! 🙌

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 👨‍💻 Developer

**Ali Haider Butt**

[![GitHub](https://img.shields.io/badge/GitHub-alibutt2882-181717?style=for-the-badge&logo=github)](https://github.com/alibutt2882)

<div align="center">

### ⭐ If you found this project useful, consider giving it a star!

</div>
