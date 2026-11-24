# 📄 AI Resume Screener

A simple NLP tool that compares a resume (PDF) with a job description and shows:

- **Match score (%)**: semantic similarity using sentence embeddings
- **Matched skills**: skills required by the job that the resume has
- **Missing skills**: the skill gap to work on next

## How it works

1. Extract text from the resume PDF (`pdfplumber`)
2. Clean the text (lowercase, remove symbols)
3. Convert text to embeddings with `all-MiniLM-L6-v2` (`sentence-transformers`)
4. Split the resume into chunks, compare each chunk with the job description using **cosine similarity**, and average the top 3
5. Find matched / missing skills using whole-word matching against `skills.txt`

## Tech stack

Python · Streamlit · sentence-transformers · pdfplumber · pytest

## Run locally

```bash
git clone https://github.com/varshini-S-max/resume-screener.git
cd resume-screener
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest
```

## Project structure

```
resume-screener/
├── app.py              
├── screener.py          
├── skills.txt          
├── tests/              
├── requirements.txt
└── README.md
```



## Limitations

- Skills are found by keyword match, so synonyms (e.g. "ML" vs "machine learning") are missed.
- Scanned (image) PDFs are not supported (no OCR).
- The match score is a rough indicator, not a hiring decision.

## Future improvements

- Skill extraction with spaCy NER
- Rank multiple resumes for one job
- LLM-based resume improvement suggestions
- OCR support for scanned PDFs

## Author

varshini-S-max . [LinkedIn](www.linkedin.com/in/varshini-s-a5a578382)
