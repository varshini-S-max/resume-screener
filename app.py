"""Streamlit UI for the Resume Screener. Run: streamlit run app.py"""
import streamlit as st

from screener import clean, extract_text, load_skills, match_score, skill_gap

st.set_page_config(page_title="AI Resume Screener", page_icon="📄")

# ---------- Custom CSS: animated background + glass cards ----------
st.markdown(
    """
<style>
/* Animated gradient background */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #1b2a49, #24243e);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Soft glowing blobs floating in the background */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background:
        radial-gradient(circle at 20% 25%, rgba(0, 219, 222, 0.18), transparent 35%),
        radial-gradient(circle at 80% 70%, rgba(252, 0, 255, 0.15), transparent 35%);
    animation: floatGlow 12s ease-in-out infinite alternate;
}
@keyframes floatGlow {
    from { transform: translate(0, 0) scale(1); }
    to   { transform: translate(30px, -20px) scale(1.15); }
}

/* Transparent top bar */
[data-testid="stHeader"] { background: transparent; }

/* Gradient title */
h1 {
    text-align: center;
    background: linear-gradient(90deg, #00dbde, #fc00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Glass card */
.glass {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    padding: 16px 20px;
    backdrop-filter: blur(10px);
    margin-bottom: 12px;
}
.glass h4 { margin: 0 0 10px 0; }

/* Skill chips */
.chip {
    display: inline-block;
    padding: 4px 12px;
    margin: 3px 4px 3px 0;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
}
.chip-ok  { background: rgba(46, 204, 113, 0.2); color: #5dffa0; border: 1px solid #2ecc71; }
.chip-bad { background: rgba(255, 82, 82, 0.2);  color: #ff8a8a; border: 1px solid #ff5252; }
</style>
""",
    unsafe_allow_html=True,
)


def chips(items, css_class):
    if not items:
        return "<i>None</i>"
    return "".join(f'<span class="chip {css_class}">{s}</span>' for s in items)


# ---------- UI ----------
st.title("📄 AI Resume Screener")
st.caption("Upload a resume and paste a job description to see match score and skill gap.")

pdf = st.file_uploader("Upload Resume (PDF)", type="pdf")
jd = st.text_area("Paste Job Description", height=200)

if st.button("Analyze") and pdf and jd.strip():
    resume_text = clean(extract_text(pdf))
    job_text = clean(jd)

    if not resume_text:
        st.error("Could not read text from this PDF (maybe it is a scanned image).")
        st.stop()

    with st.spinner("Analyzing..."):
        score = match_score(resume_text, job_text)
        matched, missing = skill_gap(resume_text, job_text, load_skills())

    st.metric("Match Score", f"{score}%")
    st.progress(min(int(score), 100))

    st.markdown(
        f'<div class="glass"><h4>✅ Matched skills</h4>{chips(matched, "chip-ok")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="glass"><h4>❌ Missing skills</h4>{chips(missing, "chip-bad")}</div>',
        unsafe_allow_html=True,
    )
elif pdf is None or not jd.strip():
    st.info("Upload a PDF and paste a job description, then click Analyze.")
