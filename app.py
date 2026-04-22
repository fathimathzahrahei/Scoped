import os
import json
import time
import re
import hashlib
import datetime
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
TAVILY_KEY     = os.getenv("TAVILY_API_KEY", "")

st.set_page_config(
    page_title="Scoped 🎯",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
}

/* ── Background — deep navy, zero purple ── */
[data-testid="stAppViewContainer"] > .main {
    background: #020d1a !important;
    min-height: 100vh !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu, footer         { visibility: hidden !important; }

/* ── Container — kill all top space ── */
[data-testid="block-container"] {
    max-width: 700px !important;
    padding: 0 1.2rem 4rem !important;
    margin-top: 0 !important;
}
[data-testid="stAppViewContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
[data-testid="stHeader"] { display: none !important; }
.appview-container .main .block-container { padding-top: 0 !important; margin-top: 0 !important; }
section[data-testid="stMain"] { padding-top: 0 !important; margin-top: 0 !important; }
section[data-testid="stMain"] > div:first-child { padding-top: 0 !important; }

/* ── Typography ── */
h1 { font-size:2.4rem !important; font-weight:900 !important; color:#F1F5F9 !important; letter-spacing:-0.04em !important; line-height:1.1 !important; }
h2 { font-size:1.5rem !important; font-weight:800 !important; color:#F1F5F9 !important; letter-spacing:-0.02em !important; }
h3 { font-size:1.1rem !important; font-weight:600 !important; color:#CBD5E1 !important; }
p  { color:#94A3B8 !important; line-height:1.7 !important; font-size:0.95rem !important; }

/* ── Buttons — teal → cyan ── */
.stButton > button p,
.stButton > button span,
.stButton > button * {
    color: #fff !important;
}
.stButton > button {
    background: linear-gradient(135deg, #0EA5E9, #06B6D4) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 6px 24px rgba(6,182,212,0.35) !important;
    width: 100% !important;
    min-height: 54px !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 12px 32px rgba(6,182,212,0.5) !important;
    background: linear-gradient(135deg, #38BDF8, #22D3EE) !important;
}
.stButton > button:active  { transform: translateY(0) scale(0.99) !important; }
.stButton > button:disabled {
    background: #0f2030 !important;
    color: #2a4a6a !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: not-allowed !important;
}

/* ── Text input ── */
.stTextInput > div > div > input {
    background: #0a1929 !important;
    border: 1.5px solid #1a3a5c !important;
    color: #F1F5F9 !important;
    border-radius: 14px !important;
    padding: 0.8rem 1.1rem !important;
    font-size: 1rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #06B6D4 !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,0.2) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #2a4a6a !important; }
.stTextInput > label {
    color: #38BDF8 !important; font-size:0.72rem !important;
    font-weight:800 !important; letter-spacing:0.12em !important;
    text-transform:uppercase !important;
}

/* ── Slider ── */
.stSlider > label {
    color: #38BDF8 !important; font-size:0.72rem !important;
    font-weight:800 !important; letter-spacing:0.12em !important;
    text-transform:uppercase !important;
}
[data-baseweb="slider"] div[role="slider"] {
    background: linear-gradient(135deg, #0EA5E9, #06B6D4) !important;
    border: 2px solid #fff !important;
    box-shadow: 0 0 10px rgba(6,182,212,0.6) !important;
}

/* ── Radio ── */
[data-testid="stRadio"] { width:100% !important; }
[data-testid="stRadio"] > div { width:100% !important; }
[data-testid="stRadio"] > div[role="radiogroup"] {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 0.6rem !important;
    width: 100% !important;
}
[data-testid="stRadio"] label {
    display:flex !important; align-items:center !important;
    background: #0a1929 !important;
    border: 1.5px solid #1a3a5c !important;
    border-radius: 14px !important;
    padding: 0.8rem 1rem !important;
    margin: 0 !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    color: #CBD5E1 !important;
    font-size: 0.93rem !important;
    min-height: 52px !important;
}
[data-testid="stRadio"] label:hover {
    border-color: #06B6D4 !important;
    background: rgba(6,182,212,0.1) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div > div > div {
    background: linear-gradient(90deg, #0EA5E9, #06B6D4, #22D3EE) !important;
    border-radius: 99px !important;
}
[data-testid="stProgressBar"] > div > div > div {
    background: #0a1929 !important;
    border-radius: 99px !important;
    height: 8px !important;
}

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    background: rgba(6,182,212,0.08) !important;
    border-radius: 14px !important;
    color: #CBD5E1 !important;
    border: 1px solid rgba(6,182,212,0.25) !important;
}

/* ── Divider ── */
hr { border-color: #1a3a5c !important; margin:1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 5px; }
::-webkit-scrollbar-track { background: #020d1a; }
::-webkit-scrollbar-thumb { background: #06B6D4; border-radius: 99px; }

/* ── Mobile ── */
@media (max-width: 640px) {
    [data-testid="block-container"] { padding: 0.75rem 0.75rem 3rem !important; }
    h1 { font-size: 1.9rem !important; }
    h2 { font-size: 1.3rem !important; }
    .stButton > button { font-size: 0.92rem !important; padding: 0.7rem 1rem !important; }
}
</style>
"""

# ── Session state ─────────────────────────────────────────────────────────────

def _init():
    today = str(datetime.date.today())
    defaults = {
        "app_state":           "home",
        "topic":               "",
        "duration":            25,
        "briefing_data":       None,
        "start_time":          None,
        "streak":              0,
        "streak_date":         today,
        "completed_sessions":  [],
        "quiz_answers":        {},
        "quiz_current_q":      0,
        "score":               0,
        "temptation_answered": False,
        "temptation_correct":  False,
        "minutes_completed":   0,
        "next_reminder":       300,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.streak_date != today:
        st.session_state.streak    = 0
        st.session_state.streak_date = today


# ── API helpers ───────────────────────────────────────────────────────────────

def _extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```\s*$",       "", text, flags=re.MULTILINE)
    text = text.strip()
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                return json.loads(text[i:])
            except json.JSONDecodeError:
                pass
    raise ValueError(f"No valid JSON found. Raw:\n{text[:400]}")


def _llm(prompt: str) -> str:
    if not OPENROUTER_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in .env")
    client = OpenAI(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")
    models = [
        "openai/gpt-oss-20b:free",
        "liquid/lfm-2.5-1.2b-instruct:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "google/gemma-3-12b-it:free",
    ]
    last_err = None
    for model in models:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
            )
            return r.choices[0].message.content
        except Exception as e:
            last_err = e
    raise last_err


def fetch_briefing(topic: str, duration: int) -> dict:
    sources_text = "(Live search unavailable)"
    if TAVILY_KEY:
        try:
            tc      = TavilyClient(api_key=TAVILY_KEY)
            results = tc.search(topic, max_results=5)
            parts   = [
                f"Title: {r.get('title','')}\n{r.get('content','')[:800]}"
                for r in results.get("results", [])
            ]
            sources_text = "\n\n---\n\n".join(parts)
        except Exception as e:
            sources_text = f"(Search error: {e})"

    prompt = f"""You are a focused learning assistant. Topic: "{topic}". Duration: {duration} min.

Context: {sources_text[:2000]}

Reply with ONLY this JSON (no markdown, no extra text). Keep all strings SHORT (under 20 words each):

{{"overview":"2 sentence summary of {topic}","key_concepts":["Term: explanation","Term: explanation","Term: explanation","Term: explanation","Term: explanation"],"what_you_will_know":["You will understand X","You will be able to Y","You will know the difference between A and B"],"temptation_question":{{"question":"Short question about {topic}?","options":["A. choice","B. choice","C. choice","D. choice"],"answer":"A","explanation":"One sentence."}},"quiz_questions":[{{"question":"Short Q about {topic}?","options":["A. choice","B. choice","C. choice","D. choice"],"answer":"B","explanation":"One sentence."}},{{"question":"Short Q about {topic}?","options":["A. choice","B. choice","C. choice","D. choice"],"answer":"C","explanation":"One sentence."}},{{"question":"Short Q about {topic}?","options":["A. choice","B. choice","C. choice","D. choice"],"answer":"A","explanation":"One sentence."}}]}}"""
    return _extract_json(_llm(prompt))


# ── Shared UI ─────────────────────────────────────────────────────────────────

def _logo():
    streak = st.session_state.streak
    flames = "🔥" * min(streak, 8) if streak > 0 else ""
    if streak > 0:
        streak_html = (
            f"<div style='font-size:1.3rem;line-height:1;margin-bottom:3px;'>{flames}</div>"
            f"<div style='color:#F97316;font-weight:800;font-size:0.8rem;'>"
            f"🔥 {streak} session{'s' if streak != 1 else ''} today</div>"
        )
    else:
        streak_html = "<div style='color:#1e4a6a;font-weight:700;font-size:0.78rem;'>No streak yet</div>"

    mark_html = (
        "<span style='display:inline-flex;align-items:center;justify-content:center;"
        "width:2rem;height:2rem;border-radius:8px;"
        "background:linear-gradient(135deg,#0EA5E9,#06B6D4);"
        "font-size:1rem;font-weight:900;color:#fff;margin-right:0.5rem;'>"
        "S</span>"
    )
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;padding:1.25rem 0 0.5rem;'>"
        f"<div>"
        f"<div style='display:flex;align-items:center;font-size:2rem;font-weight:900;letter-spacing:-0.04em;line-height:1;color:#F1F5F9;'>"
        f"{mark_html}Scoped</div>"
        f"<div style='color:#06B6D4;font-size:0.8rem;font-weight:700;letter-spacing:0.1em;"
        f"text-transform:uppercase;margin-top:3px;'>Stay in the Zone ⚡</div>"
        f"</div>"
        f"<div style='text-align:right;'>{streak_html}</div>"
        f"</div>"
        f"<div style='height:1px;background:linear-gradient(90deg,#0EA5E944,#06B6D444,#0EA5E944);"
        f"margin-bottom:1.25rem;'></div>",
        unsafe_allow_html=True,
    )


def _card(html: str, padding: str = "1.5rem"):
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(6,182,212,0.3);"
        f"border-radius:20px;padding:{padding};margin:0.75rem 0;"
        f"box-shadow:0 4px 24px rgba(6,182,212,0.1);'>{html}</div>",
        unsafe_allow_html=True,
    )


def _timer(remaining: float):
    total = st.session_state.duration * 60
    pct   = max(0.0, min(1.0, 1 - remaining / total))
    mins, secs = int(remaining // 60), int(remaining % 60)

    if remaining > total * 0.5:
        col, glow, label = "#0EA5E9", "rgba(6,182,212,0.2)", "🎯 In the zone!"
    elif remaining > total * 0.2:
        col, glow, label = "#F97316", "rgba(249,115,22,0.2)", "🔥 Almost there!"
    else:
        col, glow, label = "#22D3EE", "rgba(34,211,238,0.2)", "⚡ Final push!"

    st.markdown(
        f"<div style='background:rgba(255,255,255,0.04);border:2px solid {col}55;"
        f"border-radius:24px;padding:1.75rem 1rem;margin:0.5rem 0;text-align:center;"
        f"box-shadow:0 0 50px {glow},inset 0 1px 0 rgba(255,255,255,0.07);'>"
        f"<div style='color:#38BDF8;font-size:0.7rem;text-transform:uppercase;"
        f"letter-spacing:0.16em;margin-bottom:0.5rem;font-weight:700;'>{label}</div>"
        f"<div style='font-size:4.8rem;font-weight:900;color:{col};"
        f"letter-spacing:-0.05em;line-height:1;text-shadow:0 0 30px {col}88;'>"
        f"{mins:02d}:{secs:02d}</div>"
        f"<div style='color:#1e4a6a;font-size:0.68rem;margin-top:0.4rem;'>TIME REMAINING</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(pct)


def _mind_map_row(s: dict):
    pct = int((s["score"] / 3) * 100)
    if pct >= 67:
        bc, emoji = "#22C55E", "🌟"
    elif pct >= 33:
        bc, emoji = "#F97316", "🔥"
    else:
        bc, emoji = "#0EA5E9", "💪"
    ts  = s.get("timestamp", "")
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(6,182,212,0.2);"
        f"border-radius:16px;padding:0.9rem 1.2rem;margin:0.4rem 0;"
        f"display:flex;justify-content:space-between;align-items:center;"
        f"box-shadow:0 2px 12px rgba(6,182,212,0.06);'>"
        f"<div style='min-width:0;flex:1;'>"
        f"<div style='color:#fff;font-weight:700;font-size:0.95rem;"
        f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{s['topic']}</div>"
        f"<div style='color:#1e4a6a;font-size:0.75rem;margin-top:3px;'>"
        f"⏱ {s['duration']} min{(' · ' + ts) if ts else ''}</div>"
        f"</div>"
        f"<div style='background:{bc}22;border:1px solid {bc}55;border-radius:99px;"
        f"padding:0.25rem 0.85rem;margin-left:0.75rem;flex-shrink:0;'>"
        f"<span style='color:{bc};font-weight:800;font-size:0.82rem;'>{emoji} {pct}%</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_home():
    _logo()

    # Hero card
    st.markdown(
        "<div style='background:linear-gradient(135deg,rgba(6,182,212,0.18) 0%,rgba(14,165,233,0.12) 50%,rgba(6,182,212,0.08) 100%);"
        "border:1px solid rgba(6,182,212,0.4);border-radius:24px;padding:2.25rem 1.75rem 2rem;"
        "margin-bottom:1.5rem;text-align:center;"
        "box-shadow:0 8px 40px rgba(6,182,212,0.15),inset 0 1px 0 rgba(255,255,255,0.08);'>"
        "<div style='font-size:3rem;margin-bottom:0.6rem;'>&#x1F31F;</div>"
        "<h2 style='margin:0 0 0.5rem;background:linear-gradient(135deg,#fff,#CBD5E1);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>What will you master today?</h2>"
        "<p style='margin:0;color:#38BDF8;font-size:0.92rem;font-weight:500;'>"
        "Declare your intent. Lock in. Emerge smarter. &#x1F680;"
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    topic    = st.text_input("LEARNING TOPIC",
                             placeholder="e.g. Neural networks, Black holes, Byzantine consensus...",
                             value=st.session_state.topic)
    duration = st.slider("SESSION LENGTH (minutes)", 5, 120, st.session_state.duration, 5)

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    if st.button("🎯  Start Session", use_container_width=True):
        if not topic.strip():
            st.error("⚠️ Please enter a topic to focus on.")
        elif not OPENROUTER_KEY:
            st.error("⚠️ OPENROUTER_API_KEY not found in your .env file.")
        else:
            st.session_state.topic    = topic.strip()
            st.session_state.duration = duration
            st.session_state.app_state = "loading"
            st.rerun()

    if st.session_state.completed_sessions:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='color:#38BDF8;font-size:0.72rem;font-weight:800;"
            "text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;'>"
            "&#x1F5FA;&#xFE0F; Today's Sessions</div>",
            unsafe_allow_html=True,
        )
        for s in st.session_state.completed_sessions:
            _mind_map_row(s)


def page_loading():
    _logo()
    st.markdown(
        f"<div style='text-align:center;padding:3rem 1rem 2rem;'>"
        f"<div style='font-size:3.5rem;margin-bottom:1rem;animation:spin 2s linear infinite;'>&#x1F52D;</div>"
        f"<h2 style='background:linear-gradient(135deg,#0EA5E9,#06B6D4);"
        f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>Scanning the web for</h2>"
        f"<div style='background:linear-gradient(135deg,#F97316,#06B6D4);"
        f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        f"font-size:1.3rem;font-weight:800;margin-top:-0.3rem;margin-bottom:0.75rem;'>\"{st.session_state.topic}\"</div>"
        f"<p style='color:#38BDF8;'>Fetching live sources &middot; Crafting your briefing... &#x2728;</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    try:
        data = fetch_briefing(st.session_state.topic, st.session_state.duration)
        st.session_state.briefing_data       = data
        st.session_state.start_time          = time.time()
        st.session_state.quiz_answers        = {}
        st.session_state.quiz_current_q      = 0
        st.session_state.temptation_answered = False
        st.session_state.temptation_correct  = False
        st.session_state.next_reminder       = 300
        st.session_state.app_state           = "session"
    except Exception as e:
        st.error(f"⚠️ Couldn't generate briefing: {e}")
        if st.button("← Back to Home"):
            st.session_state.app_state = "home"
            st.rerun()
        return
    st.rerun()


def page_session():
    if not st.session_state.briefing_data or st.session_state.start_time is None:
        st.session_state.app_state = "home"
        st.rerun()
        return

    elapsed   = time.time() - st.session_state.start_time
    remaining = st.session_state.duration * 60 - elapsed

    if remaining <= 0:
        st.session_state.minutes_completed = st.session_state.duration
        st.session_state.app_state = "quiz"
        st.rerun()
        return

    _logo()
    _timer(remaining)

    # ── 5-minute reminder banner ──
    if elapsed >= st.session_state.next_reminder:
        st.markdown(
            f"<div style='background:linear-gradient(135deg,rgba(6,182,212,0.15),rgba(14,165,233,0.15));"
            f"border:1.5px solid rgba(6,182,212,0.5);border-radius:16px;"
            f"padding:0.85rem 1.25rem;margin:0.75rem 0;display:flex;align-items:center;gap:0.75rem;"
            f"box-shadow:0 4px 20px rgba(6,182,212,0.1);'>"
            f"<span style='font-size:1.4rem;'>&#x1F440;</span>"
            f"<span style='color:#CBD5E1;font-size:0.9rem;font-weight:600;'>"
            f"Still with us? Remember: <strong style='background:linear-gradient(90deg,#0EA5E9,#06B6D4);"
            f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>"
            f"{st.session_state.topic}</strong> is waiting! &#x1F525;</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if elapsed >= st.session_state.next_reminder + 30:
            st.session_state.next_reminder += 300

    data = st.session_state.briefing_data

    # Overview
    _card(
        f"<div style='color:#38BDF8;font-size:0.68rem;text-transform:uppercase;"
        f"letter-spacing:0.12em;margin-bottom:0.6rem;font-weight:800;'>&#x1F4CC; OVERVIEW</div>"
        f"<p style='color:#CBD5E1;margin:0;line-height:1.75;font-size:0.95rem;'>"
        f"{data.get('overview','')}</p>"
    )

    # Key concepts
    st.markdown(
        "<div style='color:#6B7280;font-size:0.68rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.12em;margin:1.2rem 0 0.5rem;'>"
        "🧩 KEY CONCEPTS</div>",
        unsafe_allow_html=True,
    )
    for concept in data.get("key_concepts", []):
        st.markdown(
            f"<div style='background:#1E2130;border:1px solid #2A3347;border-radius:10px;"
            f"padding:0.7rem 1rem;margin:0.3rem 0;font-size:0.9rem;color:#E2E8F0;'>"
            f"<span style='color:#38BDF8;margin-right:0.5rem;font-weight:700;'>▸</span>{concept}</div>",
            unsafe_allow_html=True,
        )

    # What you'll know
    st.markdown(
        "<div style='color:#6B7280;font-size:0.68rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.12em;margin:1.2rem 0 0.5rem;'>"
        "🏁 BY THE END, YOU WILL...</div>",
        unsafe_allow_html=True,
    )
    for item in data.get("what_you_will_know", []):
        st.markdown(
            f"<div style='color:#E2E8F0;margin:0.3rem 0;font-size:0.9rem;padding:0.1rem 0;'>"
            f"<span style='color:#22C55E;margin-right:0.5rem;'>✓</span>{item}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1px;background:#2A3347;margin:1.25rem 0;'></div>", unsafe_allow_html=True)

    # Action buttons
    if not st.session_state.temptation_answered:
        if st.button("&#x1F608;  I need a break", use_container_width=True):
            st.session_state.app_state = "temptation"
            st.rerun()
    else:
        st.markdown(
            "<div style='background:rgba(34,197,94,0.1);border:1.5px solid rgba(34,197,94,0.35);"
            "border-radius:14px;padding:0.85rem 1rem;font-size:0.9rem;color:#86EFAC;text-align:center;"
            "box-shadow:0 4px 16px rgba(34,197,94,0.1);'>"
            "&#x1F4AA; Nice! You actually know this. Keep going! &#x1F31F;"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    if st.button("🚪  End Session Early", use_container_width=True):
        st.session_state.minutes_completed = max(1, int(elapsed / 60))
        st.session_state.app_state = "early_exit"
        st.rerun()

    time.sleep(1)
    st.rerun()


def page_temptation():
    if not st.session_state.briefing_data:
        st.session_state.app_state = "home"
        st.rerun()
        return

    _logo()
    st.markdown(
        "<div style='text-align:center;padding:1rem 0 0.75rem;'>"
        "<div style='font-size:3rem;'>&#x1F9E0;</div>"
        "<h2 style='margin:0.5rem 0 0.3rem;background:linear-gradient(135deg,#0EA5E9,#06B6D4);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>Pattern Interrupt &#x26A1;</h2>"
        "<p style='color:#38BDF8;max-width:400px;margin:0 auto;font-size:0.9rem;font-weight:500;'>"
        "Answer this first &mdash; then your break is totally guilt-free. &#x1F60A;"
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    q = st.session_state.briefing_data.get("temptation_question", {})
    _card(
        f"<p style='color:#fff;font-size:1rem;font-weight:700;margin:0;line-height:1.6;'>"
        f"{q.get('question','')}</p>"
    )

    if not st.session_state.temptation_answered:
        selected = st.radio("options", q.get("options", []),
                            key="trap_radio", label_visibility="hidden", index=None)
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("Lock in Answer 🎯", use_container_width=True, disabled=selected is None):
            correct = q.get("answer", "A").upper()
            st.session_state.temptation_correct  = bool(selected and selected[0].upper() == correct)
            st.session_state.temptation_answered = True
            st.rerun()
    else:
        q_opts       = q.get("options", [])
        correct_letter = q.get("answer", "A").upper()
        correct_opt    = next((o for o in q_opts if o.startswith(correct_letter)), "")

        if st.session_state.temptation_correct:
            st.markdown(
                "<div style='background:rgba(34,197,94,0.1);border:1.5px solid rgba(34,197,94,0.4);"
                "border-radius:18px;padding:1.25rem 1.5rem;margin:0.75rem 0;text-align:center;"
                "box-shadow:0 4px 20px rgba(34,197,94,0.15);'>"
                "<div style='font-size:2.5rem;'>&#x1F389;</div>"
                "<p style='color:#86EFAC;font-weight:800;font-size:1rem;margin:0.3rem 0;'>"
                "Nice! You actually know this. Keep going &#x1F4AA;"
                "</p>"
                f"<p style='color:#1e4a6a;font-size:0.85rem;margin:0;'>{q.get('explanation','')}</p>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background:rgba(239,68,68,0.1);border:1.5px solid rgba(239,68,68,0.4);"
                f"border-radius:18px;padding:1.25rem 1.5rem;margin:0.75rem 0;"
                f"box-shadow:0 4px 20px rgba(239,68,68,0.1);'>"
                f"<p style='color:#FCA5A5;font-weight:800;margin:0 0 0.4rem;'>Not quite &mdash; but that's how we learn! &#x1F4A1;</p>"
                f"<p style='color:#CBD5E1;font-size:0.9rem;margin:0 0 0.3rem;'>&#x2713; <strong>{correct_opt}</strong></p>"
                f"<p style='color:#1e4a6a;font-size:0.85rem;margin:0;'>{q.get('explanation','')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚡  Back to Focus!", use_container_width=True):
                st.session_state.app_state = "session"
                st.rerun()
        with c2:
            if st.button("☕  Take a Break", use_container_width=True):
                st.session_state.app_state = "session"
                st.rerun()


def page_quiz():
    if not st.session_state.briefing_data:
        st.session_state.app_state = "home"
        st.rerun()
        return

    _logo()
    questions = st.session_state.briefing_data.get("quiz_questions", [])
    current   = st.session_state.quiz_current_q

    st.markdown(
        "<div style='text-align:center;padding:0.5rem 0 1rem;'>"
        "<div style='font-size:2.8rem;'>&#x26A1;</div>"
        "<h2 style='margin:0.4rem 0 0.2rem;background:linear-gradient(135deg,#0EA5E9,#06B6D4);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>Knowledge Pulse</h2>"
        "<p style='color:#38BDF8;font-size:0.88rem;font-weight:500;'>3 quick questions. No fail state &mdash; just vibes. &#x1F60E;</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Progress through questions
    st.progress((current) / len(questions))
    st.markdown(
        f"<div style='color:#38BDF8;font-size:0.72rem;font-weight:700;text-align:right;"
        f"margin-top:-0.5rem;margin-bottom:0.75rem;letter-spacing:0.05em;'>"
        f"Question {current + 1} of {len(questions)} &#x1F4CA;</div>",
        unsafe_allow_html=True,
    )

    if current < len(questions):
        q = questions[current]
        _card(
            f"<div style='color:#38BDF8;font-size:0.68rem;text-transform:uppercase;"
            f"letter-spacing:0.12em;margin-bottom:0.6rem;font-weight:800;'>Q{current + 1}</div>"
            f"<p style='color:#fff;font-size:1rem;font-weight:700;margin:0;line-height:1.55;'>"
            f"{q['question']}</p>"
        )

        selected = st.radio(
            "options",
            q.get("options", []),
            key=f"qz_{current}",
            label_visibility="hidden",
            index=None,
        )

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        is_last  = current == len(questions) - 1
        btn_text = "Submit Quiz ✨" if is_last else "Next Question →"

        if st.button(btn_text, disabled=selected is None, use_container_width=True):
            st.session_state.quiz_answers[current] = selected
            if not is_last:
                st.session_state.quiz_current_q += 1
            else:
                answers   = st.session_state.quiz_answers
                answers[current] = selected
                score = sum(
                    1 for i, q in enumerate(questions)
                    if (a := answers.get(i))
                    and a[0].upper() == q.get("answer", "").upper()
                )
                st.session_state.score = score
                st.session_state.streak += 1
                st.session_state.completed_sessions.append({
                    "topic":     st.session_state.topic,
                    "duration":  st.session_state.duration,
                    "score":     score,
                    "timestamp": datetime.datetime.now().strftime("%H:%M"),
                })
                st.session_state.app_state = "results"
            st.rerun()


def page_results():
    if not st.session_state.briefing_data:
        st.session_state.app_state = "home"
        st.rerun()
        return

    _logo()
    score     = st.session_state.score
    questions = st.session_state.briefing_data.get("quiz_questions", [])
    total     = len(questions)
    topic     = st.session_state.topic
    duration  = st.session_state.duration

    score_data = {
        3: ("🔥", "#F97316", "Perfect! You actually learned tonight."),
        2: ("💪", "#38BDF8", "Solid session. One concept to revisit."),
        1: ("👀", "#38BDF8", "Good start. Come back tomorrow for round 2."),
        0: ("💙", "#22C55E", "Happens. The fact you showed up matters."),
    }
    icon, color, msg = score_data.get(score, score_data[0])

    # Score hero
    st.markdown(
        f"<div style='text-align:center;padding:1.5rem 1rem 1rem;'>"
        f"<div style='font-size:3.8rem;line-height:1;filter:drop-shadow(0 0 20px {color}88);'>{icon}</div>"
        f"<div style='font-size:5rem;font-weight:900;color:{color};"
        f"line-height:1;margin:0.2rem 0;letter-spacing:-0.04em;"
        f"text-shadow:0 0 40px {color}66;'>{score}/{total}</div>"
        f"<p style='font-size:1.05rem;color:#CBD5E1;font-weight:700;margin:0.3rem 0 0.1rem;'>{msg}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Session summary card
    streak = st.session_state.streak
    flames = "&#x1F525;" * min(streak, 10)
    _card(
        f"<div style='color:#38BDF8;font-size:0.68rem;text-transform:uppercase;"
        f"letter-spacing:0.12em;margin-bottom:1rem;font-weight:800;'>&#x1F4CB; SESSION SUMMARY</div>"
        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;'>"
        f"<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:0.75rem;"
        f"border:1px solid rgba(6,182,212,0.15);'>"
        f"<div style='color:#1e4a6a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'>Topic</div>"
        f"<div style='color:#fff;font-weight:700;font-size:0.9rem;margin-top:3px;"
        f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{topic}</div>"
        f"</div>"
        f"<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:0.75rem;"
        f"border:1px solid rgba(6,182,212,0.15);'>"
        f"<div style='color:#1e4a6a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'>Duration</div>"
        f"<div style='color:#fff;font-weight:700;font-size:0.9rem;margin-top:3px;'>{duration} min</div>"
        f"</div>"
        f"<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:0.75rem;"
        f"border:1px solid rgba(6,182,212,0.15);'>"
        f"<div style='color:#1e4a6a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'>Score</div>"
        f"<div style='color:{color};font-weight:700;font-size:0.9rem;margin-top:3px;'>{score}/{total}</div>"
        f"</div>"
        f"<div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:0.75rem;"
        f"border:1px solid rgba(6,182,212,0.15);'>"
        f"<div style='color:#1e4a6a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'>Streak</div>"
        f"<div style='color:#F97316;font-weight:700;font-size:0.9rem;margin-top:3px;'>"
        f"{flames} {streak} today</div>"
        f"</div>"
        f"</div>",
        padding="1.25rem",
    )

    # Answer review
    st.markdown(
        "<div style='color:#38BDF8;font-size:0.68rem;font-weight:800;"
        "text-transform:uppercase;letter-spacing:0.12em;margin:1.25rem 0 0.5rem;'>"
        "&#x1F4D6; ANSWER REVIEW</div>",
        unsafe_allow_html=True,
    )
    for i, q in enumerate(questions):
        user_ans       = st.session_state.quiz_answers.get(i, "")
        correct_letter = q.get("answer", "").upper()
        is_correct     = bool(user_ans and user_ans[0].upper() == correct_letter)
        correct_opt    = next((o for o in q.get("options", []) if o.startswith(correct_letter)), "")
        bc   = "#22C55E" if is_correct else "#EF4444"
        tick = "✅" if is_correct else "❌"

        st.markdown(
            f"<div style='background:#1E2130;border:1.5px solid {bc}33;border-radius:14px;"
            f"padding:1rem 1.25rem;margin:0.5rem 0;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"margin-bottom:0.4rem;'>"
            f"<span style='color:#6B7280;font-size:0.7rem;text-transform:uppercase;"
            f"letter-spacing:0.1em;'>Q{i + 1}</span><span>{tick}</span></div>"
            f"<p style='color:#F1F5F9;font-weight:600;margin:0 0 0.5rem;font-size:0.92rem;"
            f"line-height:1.45;'>{q['question']}</p>"
            f"<p style='color:#22C55E;margin:0;font-size:0.85rem;'>✓ {correct_opt}</p>"
            f"<p style='color:#6B7280;margin:0.2rem 0 0;font-size:0.82rem;font-style:italic;'>"
            f"{q.get('explanation','')}</p></div>",
            unsafe_allow_html=True,
        )

    # Mind map
    if st.session_state.completed_sessions:
        st.markdown(
            "<div style='color:#38BDF8;font-size:0.68rem;font-weight:800;"
            "text-transform:uppercase;letter-spacing:0.12em;margin:1.25rem 0 0.5rem;'>"
            "&#x1F5FA;&#xFE0F; TODAY'S SESSIONS</div>",
            unsafe_allow_html=True,
        )
        for s in st.session_state.completed_sessions:
            _mind_map_row(s)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    if st.button("🚀  Same time tomorrow? Start another session", use_container_width=True):
        st.session_state.topic    = ""
        st.session_state.app_state = "home"
        st.rerun()


def page_early_exit():
    _logo()
    mins  = st.session_state.minutes_completed
    topic = st.session_state.topic

    st.markdown(
        f"<div style='text-align:center;padding:2.5rem 1rem 1.5rem;'>"
        f"<div style='font-size:3.8rem;filter:drop-shadow(0 0 16px rgba(6,182,212,0.4));'>&#x1F319;</div>"
        f"<h2 style='margin:0.75rem 0 0.25rem;background:linear-gradient(135deg,#0EA5E9,#06B6D4);"
        f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>You gave it a shot! &#x1F4AA;</h2>"
        f"<p style='color:#38BDF8;font-size:0.88rem;font-weight:500;'>\"{topic}\"</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    _card(
        f"<p style='color:#CBD5E1;font-size:1.05rem;line-height:1.8;margin:0;text-align:center;'>"
        f"You focused for <strong style='background:linear-gradient(135deg,#0EA5E9,#06B6D4);"
        f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{mins} minutes</strong> today. "
        f"That&rsquo;s {mins} more than doing nothing. See you soon &#x1F499; &#x1F31F;"
        f"</p>"
    )

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    if st.button("🔄  Try Again", use_container_width=True):
        st.session_state.start_time = None
        st.session_state.app_state  = "loading"
        st.rerun()

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    if st.button("🏠  Back to Home", use_container_width=True):
        st.session_state.topic     = ""
        st.session_state.app_state = "home"
        st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────

def main():
    st.markdown(CSS, unsafe_allow_html=True)
    _init()
    pages = {
        "home":       page_home,
        "loading":    page_loading,
        "session":    page_session,
        "temptation": page_temptation,
        "quiz":       page_quiz,
        "results":    page_results,
        "early_exit": page_early_exit,
    }
    pages.get(st.session_state.get("app_state", "home"), page_home)()


main()
