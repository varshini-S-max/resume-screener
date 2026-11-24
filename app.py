"""Streamlit UI for the Resume Screener. Run: streamlit run app.py"""
import streamlit as st

from screener import clean, extract_text, load_skills, match_score, skill_gap

st.set_page_config(page_title="Resume Screener", page_icon="📄")
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
    col1, col2 = st.columns(2)
    col1.success("✅ Matched skills\n\n" + (", ".join(matched) or "None"))
    col2.error("❌ Missing skills\n\n" + (", ".join(missing) or "None"))
elif pdf is None or not jd.strip():
    st.info("Upload a PDF and paste a job description, then click Analyze.")
