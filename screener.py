"""Core logic for the Resume Screener: text extraction, cleaning, scoring, skill gap."""
import re
from functools import lru_cache
from pathlib import Path

import pdfplumber

SKILLS_FILE = Path(__file__).parent / "skills.txt"


def extract_text(pdf_file):
    """Extract text from a PDF path or file-like object."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + " "
    return text


def clean(text):
    """Lowercase and remove special characters (keeps + # . for c++, c#, node.js)."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_skills(path=SKILLS_FILE):
    """Read skills.txt. Format per line:  skill name: alias1, alias2

    Returns {canonical skill: [all accepted spellings]}, all cleaned/lowercase.
    """
    skills = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, rest = line.partition(":")
        names = [name] + rest.split(",")
        variants = sorted({clean(n) for n in names if n.strip()})
        skills[name.strip().lower()] = variants  # keep original name for display
    return skills


def _has_word(word, text):
    """Whole-word match, so 'java' does not match inside 'javascript'."""
    pattern = r"(?<![a-z0-9+#])" + re.escape(word) + r"(?![a-z0-9+#])"
    return re.search(pattern, text) is not None


def _has_skill(variants, text):
    return any(_has_word(v, text) for v in variants)


def skill_gap(resume, job, skills):
    """Return (matched, missing) skill names. Inputs must be cleaned text.

    `skills` is the dict from load_skills() (a plain list of names also works).
    """
    if not isinstance(skills, dict):
        skills = {s.strip().lower(): [clean(s)] for s in skills}
    matched, missing = [], []
    for name, variants in skills.items():
        in_job = _has_skill(variants, job)
        in_resume = _has_skill(variants, resume)
        if in_job and in_resume:
            matched.append(name)
        elif in_job:
            missing.append(name)
    return matched, missing


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer  # lazy import: fast tests
    return SentenceTransformer("all-MiniLM-L6-v2")


def _chunks(text, size=60):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [text]


def match_score(resume, job, top_k=3):
    """Semantic match (0-100).

    The resume is split into chunks; each chunk is compared with the job
    description using cosine similarity, and the best `top_k` are averaged.
    """
    from sentence_transformers import util

    model = _get_model()
    chunks = _chunks(resume)
    chunk_emb = model.encode(chunks)
    job_emb = model.encode(job)
    sims = util.cos_sim(job_emb, chunk_emb)[0].tolist()
    best = sorted(sims, reverse=True)[:top_k]
    score = sum(best) / len(best)
    return round(max(0.0, min(1.0, score)) * 100, 2)
