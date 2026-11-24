"""Streamlit UI for the Resume Screener (neon AI theme). Run: streamlit run app.py"""
import base64
from pathlib import Path

import streamlit as st

from screener import clean, extract_text, load_skills, match_score, skill_gap

st.set_page_config(page_title="AI Resume Screener", page_icon="🧠")

BANNER = Path(__file__).parent / "assets" / "banner.jpg"

CSS = """
<style>
/* ===== Neon AI background: gradient + moving grid ===== */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(0, 240, 255, 0.16), transparent 40%),
        radial-gradient(circle at 85% 75%, rgba(168, 85, 247, 0.20), transparent 40%),
        linear-gradient(160deg, #050816, #0b1026 50%, #120a2e);
    background-attachment: fixed;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(0, 240, 255, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.06) 1px, transparent 1px);
    background-size: 44px 44px;
    animation: gridMove 12s linear infinite;
}
@keyframes gridMove {
    from { background-position: 0 0; }
    to   { background-position: 44px 44px; }
}
[data-testid="stHeader"] { background: transparent; }

/* ===== Banner ===== */
.banner-wrap { text-align: center; margin-bottom: 8px; }
.banner-wrap img {
    width: 100%;
    max-width: 420px;
    border-radius: 18px;
    border: 1px solid rgba(0, 240, 255, 0.6);
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.45), 0 0 60px rgba(168, 85, 247, 0.30);
    animation: pulseGlow 3.5s ease-in-out infinite alternate;
}
@keyframes pulseGlow {
    from { box-shadow: 0 0 15px rgba(0, 240, 255, 0.35), 0 0 40px rgba(168, 85, 247, 0.20); }
    to   { box-shadow: 0 0 35px rgba(0, 240, 255, 0.70), 0 0 80px rgba(168, 85, 247, 0.45); }
}

/* ===== Title ===== */
h1 {
    text-align: center;
    background: linear-gradient(90deg, #00f0ff, #a855f7, #ff4ecd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}
.tagline { text-align: center; color: #9fb3d9; margin-top: -10px; margin-bottom: 18px; }

/* ===== Inputs ===== */
[data-testid="stFileUploader"] section,
.stTextArea textarea {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(0, 240, 255, 0.35) !important;
    border-radius: 12px !important;
}
.stTextArea textarea:focus { box-shadow: 0 0 12px rgba(0, 240, 255, 0.6) !important; }

/* ===== Button ===== */
.stButton > button {
    background: linear-gradient(90deg, #00c6ff, #7b2ff7);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 28px;
    font-weight: 700;
    transition: all 0.25s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 22px rgba(0, 198, 255, 0.8);
    color: white;
}

/* ===== Gauge ===== */
.gauge-box { text-align: center; }
.gauge {
    width: 150px; height: 150px; border-radius: 50%;
    background: conic-gradient(var(--c) calc(var(--p) * 1%), rgba(255, 255, 255, 0.10) 0);
    display: grid; place-items: center; margin: 0 auto 8px auto;
    box-shadow: 0 0 28px var(--c);
}
.gauge-inner {
    width: 116px; height: 116px; border-radius: 50%;
    background: #0b1026;
    display: grid; place-items: center;
    font-size: 1.7rem; font-weight: 800; color: var(--c);
}
.gauge-label { color: #9fb3d9; font-size: 0.95rem; }

/* ===== Glass cards + chips ===== */
.glass {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 16px;
    padding: 16px 20px;
    backdrop-filter: blur(10px);
    margin-top: 14px;
}
.glass h4 { margin: 0 0 10px 0; }
.chip {
    display: inline-block; padding: 4px 12px; margin: 3px 4px 3px 0;
    border-radius: 999px; font-size: 0.85rem; font-weight: 600;
}
.chip-ok  { background: rgba(46, 204, 113, 0.15); color: #5dffa0; border: 1px solid #2ecc71; }
.chip-bad { background: rgba(255, 82, 82, 0.15);  color: #ff8a8a; border: 1px solid #ff5252; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def chips(items, css_class):
    if not items:
        return "<i>None</i>"
    return "".join(f'<span class="chip {css_class}">{s}</span>' for s in items)


def gauge(value, label, color):
    value = max(0, min(100, value))
    return (
        f'<div class="gauge-box"><div class="gauge" style="--p:{value};--c:{color}">'
        f'<div class="gauge-inner">{value:g}%</div></div>'
        f'<div class="gauge-label">{label}</div></div>'
    )


# ---------- Header ----------
if BANNER.exists():
    img64 = base64.b64encode(BANNER.read_bytes()).decode()
    st.markdown(
        f'<div class="banner-wrap"><img src="data:image/jpeg;base64,{img64}" alt="AI"></div>',
        unsafe_allow_html=True,
    )
st.title("AI Resume Screener")
st.markdown(
    '<p class="tagline">Upload a resume, paste a job description, '
    "and see your match score and skill gap.</p>",
    unsafe_allow_html=True,
)

# ---------- Inputs ----------
pdf = st.file_uploader("Upload Resume (PDF)", type="pdf")
jd = st.text_area("Paste Job Description", height=180)

# ---------- Result ----------
if st.button("🚀 Analyze") and pdf and jd.strip():
    resume_text = clean(extract_text(pdf))
    job_text = clean(jd)

    if not resume_text:
        st.error("Could not read text from this PDF (maybe it is a scanned image).")
        st.stop()

    with st.spinner("Analyzing..."):
        score = match_score(resume_text, job_text)
        matched, missing = skill_gap(resume_text, job_text, load_skills())

    required = len(matched) + len(missing)
    coverage = round(100 * len(matched) / required, 1) if required else 0

    col1, col2 = st.columns(2)
    col1.markdown(gauge(score, "Semantic match", "#00f0ff"), unsafe_allow_html=True)
    col2.markdown(gauge(coverage, "Skill coverage", "#a855f7"), unsafe_allow_html=True)

    st.markdown(
        f'<div class="glass"><h4>✅ Matched skills</h4>{chips(matched, "chip-ok")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="glass"><h4>❌ Missing skills (your next learning targets)</h4>'
        f'{chips(missing, "chip-bad")}</div>',
        unsafe_allow_html=True,
    )
elif pdf is None or not jd.strip():
    st.info("Upload a PDF and paste a job description, then click Analyze.")
