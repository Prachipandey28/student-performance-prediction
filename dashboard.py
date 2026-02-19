"""
dashboard.py — EduSense v5
Pages: Dashboard | Add Student | Student Lookup | Student Suggestions
       Student Roadmap | Class Insights | AI Chatbot
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import google.generativeai as genai  # ← THIS LINE MUST BE HERE

from database import StudentDatabase
from mailer import send_registration_email

# ── page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="EduSense",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:#050A14; --card:#0C1526; --card2:#0F1C30;
  --cyan:#00F5FF; --purple:#BF5AF2; --green:#30D158;
  --orange:#FF9F0A; --red:#FF453A; --yellow:#FFD60A;
  --txt:#E8F4FD; --muted:#6B7FA3; --border:rgba(0,245,255,0.12);
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  background-image:
    radial-gradient(ellipse at 15% 10%, rgba(0,245,255,.05) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 90%, rgba(191,90,242,.05) 0%, transparent 50%);
  font-family: 'DM Sans', sans-serif;
  color: var(--txt) !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #060E1C 0%, #091422 100%) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }

/* metric card */
.mc { background:var(--card); border:1px solid var(--border);
      border-radius:16px; padding:1.1rem 1.3rem; position:relative; overflow:hidden; }
.mc::before { content:''; position:absolute; top:0; left:0; right:0; height:2px;
              background:linear-gradient(90deg,var(--cyan),var(--purple)); }
.mc-lbl { font-family:'Space Mono',monospace; font-size:.58rem; letter-spacing:2px;
           text-transform:uppercase; color:var(--muted); margin-bottom:.35rem; }
.mc-val { font-family:'Syne',sans-serif; font-size:1.85rem; font-weight:800; line-height:1; }
.mc-sub { font-size:.71rem; color:var(--muted); margin-top:.2rem; }

/* hero */
.hero { background:linear-gradient(135deg,rgba(0,245,255,.07),rgba(191,90,242,.07));
        border:1px solid var(--border); border-radius:20px;
        padding:1.7rem 2.2rem; margin-bottom:1.4rem;
        position:relative; overflow:hidden; }
.hero::after { content:'EduSense'; position:absolute; right:2rem; top:50%;
               transform:translateY(-50%); font-family:'Syne',sans-serif;
               font-size:4.5rem; font-weight:800; color:rgba(0,245,255,.04);
               letter-spacing:-4px; pointer-events:none; user-select:none; }
.hero-h { font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800;
          letter-spacing:-1px; line-height:1.1; }
.hero-s { font-family:'Space Mono',monospace; font-size:.61rem; letter-spacing:2px;
          color:var(--muted); text-transform:uppercase; margin-top:.4rem; }

/* section header */
.sh { font-family:'Syne',sans-serif; font-weight:700; font-size:.98rem;
      color:var(--txt); margin-bottom:.75rem;
      display:flex; align-items:center; gap:.5rem; }
.sh b { display:inline-block; width:7px; height:7px; background:var(--cyan);
        border-radius:2px; box-shadow:0 0 10px rgba(0,245,255,.5); }

/* divider */
.dv { height:1px; background:linear-gradient(90deg,transparent,var(--cyan),transparent);
      margin:1.5rem 0; opacity:.2; }

/* score bar */
.sbo { background:rgba(255,255,255,.06); border-radius:100px; height:7px; }
.sbi { height:7px; border-radius:100px;
       background:linear-gradient(90deg,var(--cyan),var(--purple)); }

/* suggestion pills */
.sug { background:var(--card); border:1px solid var(--border);
       border-left:3px solid var(--cyan); border-radius:12px;
       padding:.85rem 1.1rem; margin-bottom:.6rem; font-size:.86rem; line-height:1.55; }
.sug.w { border-left-color:var(--orange); }
.sug.d { border-left-color:var(--red); }
.sug.g { border-left-color:var(--green); }
.sug.p { border-left-color:var(--purple); }
.stag { font-family:'Space Mono',monospace; font-size:.56rem; letter-spacing:1.5px;
        text-transform:uppercase; margin-bottom:.25rem; opacity:.6; }

/* flowchart */
.fn { display:flex; align-items:flex-start; gap:.9rem; margin-bottom:.35rem; }
.fn-left { display:flex; flex-direction:column; align-items:center; flex-shrink:0; }
.fn-dot { width:34px; height:34px; border-radius:50%; display:flex; align-items:center;
          justify-content:center; font-family:'Space Mono',monospace;
          font-size:.6rem; font-weight:700; flex-shrink:0; }
.fn-line { width:2px; height:24px; background:linear-gradient(180deg,rgba(0,245,255,.4),transparent); }
.fn-body { background:var(--card); border:1px solid var(--border);
           border-radius:13px; padding:.85rem 1.1rem; flex:1; margin-bottom:.6rem; }
.fn-title { font-family:'Syne',sans-serif; font-weight:700; font-size:.9rem; margin-bottom:.2rem; }
.fn-desc  { font-size:.77rem; color:var(--muted); line-height:1.5; }
.fn-badge { display:inline-block; font-family:'Space Mono',monospace; font-size:.55rem;
            letter-spacing:1px; padding:2px 8px; border-radius:20px; margin-bottom:.3rem; }
.b-done   { background:rgba(48,209,88,.13); color:#30D158; border:1px solid rgba(48,209,88,.3); }
.b-active { background:rgba(0,245,255,.1); color:#00F5FF; border:1px solid rgba(0,245,255,.3); }
.b-warn   { background:rgba(255,159,10,.1); color:#FF9F0A; border:1px solid rgba(255,159,10,.3); }
.b-danger { background:rgba(255,69,58,.1); color:#FF453A; border:1px solid rgba(255,69,58,.3); }
.b-plan   { background:rgba(191,90,242,.1); color:#BF5AF2; border:1px solid rgba(191,90,242,.3); }
.b-future { background:rgba(107,127,163,.1); color:#6B7FA3; border:1px solid rgba(107,127,163,.3); }

/* profile field */
.pf { background:rgba(0,0,0,.22); border:1px solid rgba(255,255,255,.06);
      border-radius:10px; padding:.65rem .9rem; margin-bottom:.4rem; }
.pf-l { font-family:'Space Mono',monospace; font-size:.54rem; color:var(--muted);
        letter-spacing:1.5px; text-transform:uppercase; margin-bottom:.15rem; }
.pf-v { font-family:'Syne',sans-serif; font-size:.92rem; font-weight:700; }

/* chat bubbles */
.cb-u { background:linear-gradient(135deg,rgba(0,245,255,.14),rgba(191,90,242,.1));
        border:1px solid rgba(0,245,255,.2); border-radius:16px 16px 4px 16px;
        padding:.75rem 1rem; margin-bottom:.5rem;
        font-size:.86rem; line-height:1.55; max-width:86%; margin-left:auto; }
.cb-b { background:var(--card); border:1px solid var(--border);
        border-radius:16px 16px 16px 4px;
        padding:.75rem 1rem; margin-bottom:.5rem;
        font-size:.86rem; line-height:1.65; max-width:92%; }
.cb-name { font-family:'Space Mono',monospace; font-size:.54rem; letter-spacing:1.5px;
           text-transform:uppercase; margin-bottom:.3rem; opacity:.55; }

/* inputs */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea textarea {
  background: var(--card2) !important;
  border: 1px solid var(--border) !important;
  color: var(--txt) !important;
  border-radius: 10px !important;
}
.stFormSubmitButton button, .stButton button {
  background: linear-gradient(135deg, var(--cyan), var(--purple)) !important;
  color: #050A14 !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 10px !important;
  letter-spacing: .4px !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important; border-radius:12px !important;
  border: 1px solid var(--border) !important; gap:0 !important; padding:4px !important;
}
.stTabs [data-baseweb="tab"] {
  font-family:'Syne',sans-serif !important; font-weight:600 !important;
  font-size:.81rem !important; color:var(--muted) !important; border-radius:9px !important;
}
.stTabs [aria-selected="true"] {
  background:linear-gradient(135deg,rgba(0,245,255,.15),rgba(191,90,242,.15)) !important;
  color:var(--txt) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top:1.2rem !important; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-thumb { background:rgba(0,245,255,.2); border-radius:2px; }

/* colour helpers */
.cc  { color:var(--cyan);   }
.cg  { color:var(--green);  }
.cp  { color:var(--purple); }
.co  { color:var(--orange); }
.cr  { color:var(--red);    }
</style>
""", unsafe_allow_html=True)

# ── constants ────────────────────────────────────────────────────
DOMAINS = [
    "Engineering", "Medical", "Commerce", "Arts & Humanities",
    "Law", "Management", "Science", "Architecture", "Pharmacy", "Design",
]
BRANCHES = {
    "Engineering":       ["Computer Science (CS)", "Information Technology (IT)",
                          "Electronics & Communication (ECE)", "Electrical (EE)",
                          "Mechanical (ME)", "Civil (CE)", "AI & Machine Learning",
                          "Data Science", "Cybersecurity", "Other"],
    "Medical":           ["MBBS", "BDS", "Nursing", "Physiotherapy", "Pharmacy", "Other"],
    "Commerce":          ["B.Com", "BBA", "CA", "Economics", "Finance", "Other"],
    "Arts & Humanities": ["English", "Psychology", "History", "Sociology", "Journalism", "Other"],
    "Law":               ["LLB", "BA LLB", "BBA LLB", "Other"],
    "Management":        ["MBA", "BBA", "HR", "Marketing", "Operations", "Other"],
    "Science":           ["Physics", "Chemistry", "Biology", "Mathematics", "Statistics", "Other"],
    "Architecture":      ["B.Arch", "Interior Design", "Urban Planning", "Other"],
    "Pharmacy":          ["B.Pharm", "M.Pharm", "Pharma D", "Other"],
    "Design":            ["Graphic Design", "UX/UI", "Fashion Design", "Product Design", "Other"],
}
SUBJECTS = [
    "Python", "Java", "C/C++", "JavaScript", "TypeScript", "Rust", "Go",
    "Data Structures & Algorithms", "Operating Systems", "Computer Networks",
    "Database Management (DBMS)", "Machine Learning", "Deep Learning",
    "Natural Language Processing", "Computer Vision", "Cloud Computing",
    "DevOps & Docker", "Web Dev (React/Node)", "Android Development",
    "iOS Development", "Cybersecurity", "Blockchain",
    "Mathematics", "Statistics & Probability", "Linear Algebra",
    "Digital Electronics", "Signals & Systems", "Control Systems",
    "Thermodynamics", "Fluid Mechanics", "Structural Analysis",
    "Accounting", "Financial Management", "Business Law",
    "Marketing Management", "Organic Chemistry", "Biochemistry",
    "Quantum Mechanics", "Research Methodology", "Technical Writing",
    "UI/UX Design", "Graphic Design", "Soft Skills",
]
ACTIVITIES = [
    "Sports (Cricket, Football, Basketball, etc.)",
    "Online Gaming / Esports",
    "Chess / Board Games",
    "Music (Singing, Instrument)",
    "Dance / Performing Arts",
    "Coding Clubs / Hackathons",
    "Debate / Public Speaking",
    "Photography / Videography",
    "Art & Painting",
    "Reading / Writing / Blogging",
    "Yoga / Gym / Fitness",
    "Drama / Theatre",
    "Social Work / NGO",
    "Robotics / Maker Clubs",
    "Cooking / Culinary Arts",
    "Travelling / Adventure Sports",
    "None",
]

COLORS = ["#00F5FF", "#BF5AF2", "#30D158", "#FF9F0A", "#FF453A", "#5E5CE6", "#64D2FF"]
PLY = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#E8F4FD"),
    margin=dict(l=20, r=20, t=35, b=20),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
)

# ── db ───────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    return StudentDatabase()

db = get_db()

# ── small helpers ────────────────────────────────────────────────
def grade_color(g):
    m = {"O": "#00F5FF", "A+": "#30D158", "A": "#30D158",
         "B+": "#FF9F0A", "B": "#FF9F0A", "F": "#FF453A"}
    return m.get(g, "#E8F4FD")

def bar(val, mx=100):
    pct = max(0, min(100, val / mx * 100))
    return f'<div class="sbo"><div class="sbi" style="width:{pct}%"></div></div>'

def pfield(label, val):
    return (
        f'<div class="pf">'
        f'<div class="pf-l">{label}</div>'
        f'<div class="pf-v">{val}</div>'
        f'</div>'
    )

def tag(text, color="#00F5FF", bg="rgba(0,245,255,.1)", border="rgba(0,245,255,.25)"):
    return (
        f'<span style="display:inline-block;background:{bg};border:1px solid {border};'
        f'border-radius:20px;padding:3px 10px;font-size:.73rem;margin:3px;color:{color}">'
        f'{text}</span>'
    )

def hero(title, sub):
    st.markdown(
        f'<div class="hero"><div class="hero-h">{title}</div>'
        f'<div class="hero-s">{sub}</div></div>',
        unsafe_allow_html=True,
    )

def sh(text):
    st.markdown(f'<div class="sh"><b></b>{text}</div>', unsafe_allow_html=True)

def dv():
    st.markdown('<div class="dv"></div>', unsafe_allow_html=True)

def sug_card(kind, tag_txt, msg):
    st.markdown(
        f'<div class="sug {kind}"><div class="stag">{tag_txt}</div>{msg}</div>',
        unsafe_allow_html=True,
    )

# ── flowchart node helper (NO backslash in f-string) ────────────
def flow_node(dot_color, rgb, num, badge_cls, badge_lbl, title, desc, show_line):
    line_html = '<div class="fn-line"></div>' if show_line else ""
    st.markdown(
        f'<div class="fn">'
        f'<div class="fn-left">'
        f'<div class="fn-dot" style="background:rgba({rgb},.15);border:2px solid {dot_color};color:{dot_color}">'
        f'{num:02d}</div>'
        f'{line_html}'
        f'</div>'
        f'<div class="fn-body">'
        f'<span class="fn-badge {badge_cls}">{badge_lbl}</span>'
        f'<div class="fn-title">{title}</div>'
        f'<div class="fn-desc">{desc}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

def dot_rgb(cls):
    m = {
        "b-done":   ("#30D158", "48,209,88"),
        "b-active": ("#00F5FF", "0,245,255"),
        "b-warn":   ("#FF9F0A", "255,159,10"),
        "b-danger": ("#FF453A", "255,69,58"),
        "b-plan":   ("#BF5AF2", "191,90,242"),
        "b-future": ("#6B7FA3", "107,127,163"),
    }
    return m.get(cls, ("#00F5FF", "0,245,255"))

# ── student suggestions engine ───────────────────────────────────
def student_suggestions(s):
    tips = []
    cgpa     = s.get("cgpa", 0)
    sem_cgpa = s.get("current_sem_cgpa", 0)
    att      = s.get("attendance", 0)
    study    = s.get("study_hours", 0)
    screen   = s.get("screen_time", 0)
    sleep    = s.get("sleep_hours", 0)
    absences = s.get("absences", 0)
    stress   = s.get("stress_level", "")
    acts     = s.get("activities", "")

    # overall CGPA
    if cgpa < 5.0:
        tips.append(("d", "CRITICAL CGPA",
            f"Predicted CGPA {cgpa}/10 — you are at-risk of failing. "
            "Seek academic counselling immediately, focus on highest-weight subjects, "
            "and attend every class without exception."))
    elif cgpa < 7.0:
        tips.append(("w", "CGPA IMPROVEMENT NEEDED",
            f"CGPA {cgpa}/10. Increase study hours, target 90%+ attendance, "
            "and complete all assignments to reach 7.0+."))
    else:
        tips.append(("g", "GOOD CGPA",
            f"CGPA {cgpa}/10 — great performance! Keep the momentum going."))

    # current semester CGPA
    if sem_cgpa < 5.0:
        tips.append(("d", "SEMESTER CRISIS",
            f"Current semester CGPA is only {sem_cgpa}/10. "
            "Talk to your professor about remedial exams or bonus assignments immediately."))
    elif sem_cgpa < 7.0:
        tips.append(("w", "SEMESTER CGPA BELOW TARGET",
            f"Semester CGPA {sem_cgpa}/10 — still time to improve. "
            "Prioritise upcoming internal tests and submit all pending work."))
    elif sem_cgpa > cgpa:
        tips.append(("g", "SEMESTER TRENDING UP",
            f"Semester CGPA {sem_cgpa}/10 is higher than overall {cgpa}/10 — you are improving!"))

    # attendance
    if att < 60:
        tips.append(("d", "CRITICAL ATTENDANCE",
            f"Attendance {att:.0f}% is dangerously low. "
            "Below 75% you may be barred from exams. Attend every class starting today."))
    elif att < 75:
        tips.append(("w", "LOW ATTENDANCE WARNING",
            f"Attendance {att:.0f}% is below the 75% eligibility threshold. "
            "You cannot afford any more absences."))
    elif att >= 90:
        tips.append(("g", "EXCELLENT ATTENDANCE", f"{att:.0f}% — outstanding regularity!"))

    # study hours
    if study < 1.5:
        tips.append(("d", "CRITICALLY LOW STUDY TIME",
            f"Only {study}h/day is far below the minimum. "
            "Aim for 3–4h daily using the Pomodoro technique: 25 min study, 5 min break."))
    elif study < 3.0:
        tips.append(("w", "INCREASE STUDY HOURS",
            f"{study}h/day is below the recommended 3h. "
            "Add one focused hour each evening before sleep."))

    # screen time
    if screen > 6:
        tips.append(("d", "EXCESSIVE SCREEN TIME",
            f"{screen}h/day of screen time is damaging focus and sleep. "
            "Use app timers, delete distracting apps, go grayscale after 9 pm."))
    elif screen > 4:
        tips.append(("w", "HIGH SCREEN TIME",
            f"{screen}h/day is high. Reduce by 30 min each week with scheduled phone-free study blocks."))
    else:
        tips.append(("g", "HEALTHY SCREEN TIME", f"Only {screen}h/day — good digital discipline!"))

    # sleep
    if sleep < 5:
        tips.append(("d", "SLEEP DEPRIVATION",
            f"Only {sleep}h sleep/night severely impairs memory and focus. "
            "Fix sleep before adding more study hours — it is counter-productive otherwise."))
    elif sleep < 6.5:
        tips.append(("w", "INSUFFICIENT SLEEP",
            f"{sleep}h/night is below the 7h optimum. Sleep 30 min earlier each night this week."))

    # absences
    if absences > 15:
        tips.append(("d", "CRITICAL ABSENCES",
            f"{absences} absences will severely impact your grade and eligibility. "
            "Get medical documentation if applicable and speak to your coordinator."))
    elif absences > 8:
        tips.append(("w", "HIGH ABSENCES",
            f"{absences} absences is concerning. Do not miss any more classes."))

    # stress
    if stress == "High":
        tips.append(("d", "HIGH STRESS ALERT",
            "High stress detected. Try: 10-min morning meditation, journaling before bed, "
            "talking to a counsellor, and reducing caffeine. You are not alone."))
    elif stress == "Medium":
        tips.append(("w", "MODERATE STRESS",
            "Medium stress is manageable. Practice 4-7-8 breathing and take a 5-min break every 90 min."))

    # gaming + screen time warning
    if ("Gaming" in acts or "Esports" in acts) and screen > 4:
        tips.append(("w", "GAMING + HIGH SCREEN TIME",
            "Online gaming combined with high screen time heavily impacts studies. "
            "Set hard limits: max 1h gaming on weekdays, 2h on weekends."))

    # internet & support
    if s.get("internet_access") == "No":
        tips.append(("p", "INTERNET ACCESS",
            "No home internet. Use college library WiFi, NPTEL, and offline YouTube downloads "
            "for lectures. Ask about the college device-lending programme."))
    if s.get("extra_support") == "No" and cgpa < 7.0:
        tips.append(("p", "GET EXTRA SUPPORT",
            "Enrolling in tutoring or coaching — even 2 sessions/week — can raise your CGPA by 1 point."))

    return tips

# ── student roadmap engine ───────────────────────────────────────
def student_roadmap(s):
    """Returns list of (badge_cls, badge_lbl, title, desc) tuples."""
    att      = s.get("attendance", 0)
    screen   = s.get("screen_time", 0)
    sleep    = s.get("sleep_hours", 0)
    study    = s.get("study_hours", 0)
    stress   = s.get("stress_level", "")
    sem_cgpa = s.get("current_sem_cgpa", 0)
    cgpa     = s.get("cgpa", 0)
    absences = s.get("absences", 0)

    steps = []

    # 1 attendance
    if att >= 75:
        steps.append(("b-done", "DONE", "Maintain 75%+ Attendance",
            f"Currently {att:.0f}% — good! Keep attending every class to stay exam-eligible."))
    elif att >= 60:
        steps.append(("b-warn", "ACTION", "Fix Attendance Immediately",
            f"At {att:.0f}% you are close to the danger zone. Attend every class from today — no exceptions."))
    else:
        steps.append(("b-danger", "URGENT", "Critical: Attendance Below 60%",
            f"At {att:.0f}% you may be barred from exams. Visit your HOD / Dean today and explain your situation."))

    # 2 screen time
    if screen <= 3:
        steps.append(("b-done", "DONE", "Screen Time Under Control",
            f"Only {screen}h/day — excellent. Keep phone away during every study session."))
    elif screen <= 5:
        steps.append(("b-warn", "IMPROVE", "Reduce Screen Time",
            f"{screen}h/day is borderline. Set daily app timers and use grayscale mode after 9 pm."))
    else:
        steps.append(("b-danger", "URGENT", "Cut Screen Time Aggressively",
            f"{screen}h/day is hurting focus and sleep. Delete the most distracting apps temporarily."))

    # 3 sleep
    if sleep >= 7:
        steps.append(("b-done", "DONE", "Sleep Routine Healthy",
            f"{sleep}h/night — your brain consolidates memory effectively. Protect this routine."))
    elif sleep >= 6:
        steps.append(("b-warn", "IMPROVE", "Improve Sleep by 1 Hour",
            f"At {sleep}h, try sleeping 30 min earlier. No screens 45 min before bed."))
    else:
        steps.append(("b-danger", "URGENT", "Sleep Deprivation — Fix First",
            f"Only {sleep}h/night — cognitive impairment is occurring. Fix sleep before increasing study hours."))

    # 4 study
    if study >= 4:
        steps.append(("b-done", "DONE", "Study Hours Sufficient",
            f"{study}h/day — great! Focus on quality: active recall, past papers, Feynman technique."))
    elif study >= 2.5:
        steps.append(("b-warn", "IMPROVE", "Add 1-2 Hours Daily Study",
            f"At {study}h/day, add 1.5h split as 45 min morning + 45 min evening using Pomodoro."))
    else:
        steps.append(("b-danger", "URGENT", "Study Plan Overhaul Needed",
            f"Only {study}h/day — create a daily timetable with fixed, non-negotiable study blocks."))

    # 5 absences
    if absences <= 5:
        steps.append(("b-done", "DONE", "Absences Under Control",
            f"Only {absences} absences — good. Each absence costs ~0.5 final score points."))
    elif absences <= 10:
        steps.append(("b-warn", "CAUTION", "Limit Further Absences",
            f"{absences} absences already — do not miss any more classes this semester."))
    else:
        steps.append(("b-danger", "URGENT", "High Absences — Take Action",
            f"{absences} absences is severe. Speak to your coordinator and get documentation if needed."))

    # 6 stress
    if stress == "Low":
        steps.append(("b-done", "DONE", "Stress Well Managed",
            "Low stress — healthy mental state. Maintain work-life balance and protect your wellbeing."))
    elif stress == "Medium":
        steps.append(("b-warn", "IMPROVE", "Manage Stress Proactively",
            "Medium stress is manageable. 10 min daily meditation, journaling, and talking to friends help greatly."))
    else:
        steps.append(("b-danger", "URGENT", "Address High Stress Now",
            "High stress impairs memory and decision-making. Book a session with your college counsellor this week."))

    # 7 semester CGPA
    if sem_cgpa >= 8.0:
        steps.append(("b-done", "DONE", "Semester CGPA On Track",
            f"Semester CGPA {sem_cgpa}/10 — excellent! Aim for the same consistency next semester."))
    elif sem_cgpa >= 6.0:
        steps.append(("b-active", "TARGET", "Push Semester CGPA to 8.0",
            f"At {sem_cgpa}/10, you need {8.0 - sem_cgpa:.1f} more points. "
            "Focus on upcoming internals and pending assignments."))
    else:
        steps.append(("b-danger", "URGENT", "Semester CGPA Rescue Plan",
            f"At {sem_cgpa}/10, talk to professors about extra credit and internal re-evaluation immediately."))

    # 8 overall CGPA goal
    if cgpa >= 8.5:
        steps.append(("b-done", "ACHIEVED", "Overall CGPA Goal Reached",
            f"CGPA {cgpa}/10 — distinction level! Explore research internships and higher studies."))
    elif cgpa >= 7.0:
        steps.append(("b-active", "TARGET", "Push Overall CGPA to 8.5+",
            f"At {cgpa}/10 you are {8.5 - cgpa:.1f} points from distinction. "
            "Each semester improvement compounds — start now."))
    else:
        steps.append(("b-warn", "RECOVER", "Long-Term CGPA Recovery Plan",
            f"At {cgpa}/10, recovery takes 2–3 consistent semesters. "
            "Every 0.5 point improvement matters for placements — start today."))

    # 9 final goal
    steps.append(("b-active", "GOAL", "Graduate with Distinction & Opportunities",
        "Complete your degree with strong CGPA, 2+ internships, 1 project or publication, "
        "and 1 extracurricular achievement. This combination opens doors to top placements and higher studies."))

    return steps

# ── report text ──────────────────────────────────────────────────
def report_text(s):
    subjects  = s.get("subjects", "").replace(", ", "\n   - ")
    acts      = s.get("activities", "None")
    risk_txt  = "YES - Needs Intervention" if s.get("at_risk") else "NO"
    generated = datetime.now().strftime("%d %b %Y, %I:%M %p")
    return f"""
==============================================================
         EduSense — Student Performance Report
==============================================================
Generated : {generated}

IDENTITY
  Name                : {s.get("name", "")}
  Student ID          : #{s.get("student_id", "")}
  Gender / Age        : {s.get("gender", "")} / {s.get("age", "")}
  Email               : {s.get("email", "—")}
  Phone               : {s.get("phone", "—")}

ACADEMIC
  Domain              : {s.get("domain", "")}
  Branch              : {s.get("branch", "")}
  Current Sem CGPA    : {s.get("current_sem_cgpa", 0)} / 10.0
  Overall CGPA        : {s.get("cgpa", 0)} / 10.0
  Grade               : {s.get("grade", "")}
  Pass / Fail         : {s.get("pass_fail", "")}
  At-Risk             : {risk_txt}
  Final Score         : {s.get("final_score", 0):.2f} / 100

SUBJECTS / LANGUAGES / WORK
   - {subjects}

ACTIVITIES
  {acts}

PERFORMANCE METRICS
  Attendance          : {s.get("attendance", 0):.1f}%
  Midterm Score       : {s.get("midterm_score", 0):.1f}
  Assignments         : {s.get("assignments", 0):.1f}
  Study Hours/Day     : {s.get("study_hours", 0)}h
  Screen Time/Day     : {s.get("screen_time", 0)}h
  Prev CGPA           : {s.get("prev_cgpa", 0)}
  Sleep Hours/Night   : {s.get("sleep_hours", 0)}h
  Absences            : {s.get("absences", 0)}
  Stress Level        : {s.get("stress_level", "")}
  Internet Access     : {s.get("internet_access", "")}
  Extra Support       : {s.get("extra_support", "")}

==============================================================
  EduSense · Student Performance Intelligence System
  Confidential — For Internal Use Only
==============================================================
"""

# ── sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-family:Syne;font-weight:800;font-size:1.4rem;color:#00F5FF">🎓 EduSense</div>'
        '<div style="font-family:Space Mono;font-size:.58rem;letter-spacing:2px;color:#6B7FA3;'
        'text-transform:uppercase;margin-bottom:1.25rem">STUDENT PERFORMANCE OS v5</div>',
        unsafe_allow_html=True,
    )

    page = st.radio("nav", [
        "📊  Dashboard",
        "➕  Add Student",
        "🔍  Student Lookup",
        "💡  Student Suggestions",
        "🗺️  Student Roadmap",
        "🏫  Class Insights",
        "🤖  AI Chatbot",
    ], label_visibility="collapsed")

    st.markdown('<div class="dv"></div>', unsafe_allow_html=True)

    df_live = db.get_dataframe()
    if len(df_live) > 0:
        avg_cgpa  = df_live["cgpa"].mean()
        at_risk_n = int(df_live["at_risk"].sum())
        rc        = "#FF453A" if at_risk_n > 0 else "#30D158"
        st.markdown(
            f'<div style="font-family:Space Mono;font-size:.56rem;letter-spacing:2px;'
            f'color:#6B7FA3;text-transform:uppercase;margin-bottom:.5rem">LIVE STATS</div>'
            f'<div style="color:#00F5FF;font-family:Syne;font-size:1.2rem;font-weight:800">'
            f'{len(df_live)}<span style="color:#6B7FA3;font-size:.66rem;margin-left:4px">STUDENTS</span></div>'
            f'<div style="color:#30D158;font-family:Syne;font-size:1.2rem;font-weight:800">'
            f'{avg_cgpa:.2f}<span style="color:#6B7FA3;font-size:.66rem;margin-left:4px">AVG CGPA</span></div>'
            f'<div style="color:{rc};font-family:Syne;font-size:1.2rem;font-weight:800">'
            f'{at_risk_n}<span style="color:#6B7FA3;font-size:.66rem;margin-left:4px">AT-RISK</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:Space Mono;font-size:.52rem;color:#6B7FA3">SQLite · Python · Streamlit · Claude AI</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════
if page == "📊  Dashboard":
    hero("Student Intelligence Command Center",
         "Real-time analytics · CGPA tracking · Risk detection")

    df = db.get_dataframe()
    if df.empty:
        st.markdown(
            '<div style="text-align:center;padding:4rem;background:var(--card);'
            'border:1px dashed rgba(0,245,255,.2);border-radius:20px">'
            '<div style="font-size:3rem">📭</div>'
            '<div style="font-family:Syne;font-size:1.2rem;font-weight:700;margin-top:.5rem">No Students Yet</div>'
            '<div style="color:#6B7FA3;font-size:.9rem;margin-top:.3rem">Add students via ➕ Add Student</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    avg_cgpa   = df["cgpa"].mean()
    pass_rate  = (df["pass_fail"] == "Pass").mean()
    at_risk_n  = int(df["at_risk"].sum())
    avg_screen = df["screen_time"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Total Students",    str(len(df)),      "cc", "enrolled"),
        (c2, "Average CGPA",      f"{avg_cgpa:.2f}/10",
         "cg" if avg_cgpa >= 7 else "co", "class average"),
        (c3, "Pass Rate",         f"{pass_rate:.1%}",
         "cg" if pass_rate >= .75 else "co", "of all students"),
        (c4, "At-Risk Students",  str(at_risk_n),
         "cr" if at_risk_n > 0 else "cg", "need intervention"),
        (c5, "Avg Screen Time",   f"{avg_screen:.1f}h",
         "co" if avg_screen > 4 else "cg", "per day"),
    ]
    for col, lbl, val, cls, sub in cards:
        with col:
            st.markdown(
                f'<div class="mc"><div class="mc-lbl">{lbl}</div>'
                f'<div class="mc-val {cls}">{val}</div>'
                f'<div class="mc-sub">{sub}</div></div>',
                unsafe_allow_html=True,
            )

    dv()

    col1, col2 = st.columns(2)
    with col1:
        sh("CGPA Distribution")
        fig = px.histogram(df, x="cgpa", nbins=10, color_discrete_sequence=["#00F5FF"])
        fig.update_layout(**PLY)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        sh("Grade Breakdown")
        gc = df["grade"].value_counts().reset_index()
        gc.columns = ["Grade", "Count"]
        fig2 = px.pie(gc, values="Count", names="Grade",
                      color_discrete_sequence=COLORS, hole=.55)
        fig2.update_layout(**PLY)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns(2)
    with col3:
        sh("Screen Time vs CGPA")
        fig3 = px.scatter(df, x="screen_time", y="cgpa", color="stress_level",
                          color_discrete_map={"Low": "#30D158", "Medium": "#FF9F0A", "High": "#FF453A"},
                          hover_data=["name", "student_id"],
                          labels={"screen_time": "Screen Time (hrs)", "cgpa": "CGPA"})
        fig3.update_layout(**PLY)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col4:
        sh("Current Sem CGPA vs Overall CGPA")
        fig4 = px.scatter(df, x="current_sem_cgpa", y="cgpa", color="grade",
                          color_discrete_sequence=COLORS,
                          hover_data=["name", "student_id"],
                          labels={"current_sem_cgpa": "Semester CGPA", "cgpa": "Overall CGPA"})
        fig4.update_layout(**PLY)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    dv()
    sh("All Students")
    cols_show = ["student_id", "name", "domain", "branch",
                 "current_sem_cgpa", "cgpa", "grade", "pass_fail",
                 "attendance", "screen_time", "at_risk"]
    st.dataframe(df[[c for c in cols_show if c in df.columns]],
                 use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
# ADD STUDENT
# ════════════════════════════════════════════════════════════════
elif page == "➕  Add Student":
    hero("Register New Student",
         "Complete profile · CGPA auto-calculated · Email confirmation sent")

    with st.form("add_form", clear_on_submit=True):
        sh("Identity & Contact")
        r1, r2, r3 = st.columns(3)
        with r1:
            student_id = st.number_input("Student ID (integer)", min_value=1,
                                         max_value=999999, step=1, value=1001)
            name = st.text_input("Full Name", placeholder="e.g. Arjun Sharma")
        with r2:
            email = st.text_input("Email", placeholder="student@college.edu")
            phone = st.text_input("Phone", placeholder="+91 98765 43210")
        with r3:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            age    = st.number_input("Age", min_value=15, max_value=30, value=20)

        dv()
        sh("Domain & Branch")
        d1, d2 = st.columns(2)
        with d1:
            domain = st.selectbox("Domain", DOMAINS)
        with d2:
            branch = st.selectbox("Branch", BRANCHES.get(domain, ["Other"]))

        subjects_sel = st.multiselect(
            "Subjects / Programming Languages / Current Work (max 10)",
            SUBJECTS, max_selections=10,
        )

        dv()
        sh("Academic Performance")
        p1, p2, p3, p4, p5 = st.columns(5)
        with p1: prev_cgpa      = st.number_input("Previous CGPA (0-10)",  0.0, 10.0,  7.0, .1)
        with p2: cur_sem_cgpa   = st.number_input("Current Sem CGPA (0-10)", 0.0, 10.0, 7.0, .1)
        with p3: midterm        = st.number_input("Midterm Score (0-100)", 0.0, 100.0, 70.0, .5)
        with p4: assignments    = st.number_input("Assignments (0-100)",   0.0, 100.0, 70.0, .5)
        with p5: attendance     = st.number_input("Attendance %",          0.0, 100.0, 85.0, .5)

        dv()
        sh("Lifestyle & Habits")
        l1, l2, l3, l4, l5, l6 = st.columns(6)
        with l1: study_hours    = st.number_input("Study Hrs/Day",     0.0, 16.0, 3.0, .5)
        with l2: screen_time    = st.number_input("Screen Time Hrs/Day", 0.0, 16.0, 3.0, .5)
        with l3: sleep_hours    = st.number_input("Sleep Hrs/Night",   0.0, 12.0, 7.0, .5)
        with l4: absences       = st.number_input("Absences",          0,   100,   2)
        with l5: stress_level   = st.selectbox("Stress Level", ["Low", "Medium", "High"])
        with l6: internet       = st.selectbox("Internet Access", ["Yes", "No"])

        activities_sel = st.multiselect("Extracurricular Activities", ACTIVITIES)
        extra_support  = st.selectbox("Extra Academic Support", ["Yes", "No"])

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "⚡ Register Student & Calculate CGPA", use_container_width=True
        )

    if submitted:
        sid  = int(student_id)
        errs = []
        if not name.strip():       errs.append("Name cannot be empty.")
        if db.exists(sid):         errs.append(f"Student ID #{sid} already exists.")
        if not subjects_sel:       errs.append("Select at least one subject.")

        if errs:
            for e in errs:
                st.error(f"❌ {e}")
        else:
            acts_str = ", ".join(activities_sel) if activities_sel else "None"
            data = {
                "student_id":       sid,
                "name":             name.strip(),
                "email":            email.strip(),
                "phone":            phone.strip(),
                "gender":           gender,
                "age":              int(age),
                "domain":           domain,
                "branch":           branch,
                "subjects":         ", ".join(subjects_sel),
                "internet_access":  internet,
                "extra_support":    extra_support,
                "attendance":       float(attendance),
                "study_hours":      float(study_hours),
                "screen_time":      float(screen_time),
                "prev_cgpa":        float(prev_cgpa),
                "current_sem_cgpa": float(cur_sem_cgpa),
                "assignments":      float(assignments),
                "midterm_score":    float(midterm),
                "sleep_hours":      float(sleep_hours),
                "absences":         int(absences),
                "activities":       acts_str,
                "stress_level":     stress_level,
            }
            if db.add_student(data):
                s      = db.get_student(sid)
                ghex   = grade_color(s["grade"])
                r_html = (
                    '<span style="color:#FF453A;font-weight:700">⚠️ YES</span>'
                    if s["at_risk"]
                    else '<span style="color:#30D158;font-weight:700">✅ NO</span>'
                )
                pf_col = "#30D158" if s["pass_fail"] == "Pass" else "#FF453A"

                mail_ok, mail_msg = send_registration_email(s)
                if mail_msg == "DEV_MODE":
                    mail_note = "📧 Set EDUSENSE_EMAIL env var to enable emails."
                elif mail_ok:
                    mail_note = f"📧 Confirmation sent to {s['email']}"
                else:
                    mail_note = f"📧 Email error: {mail_msg}"

                st.markdown(
                    f'<div style="background:var(--card);border:1px solid rgba(48,209,88,.3);'
                    f'border-radius:20px;padding:1.75rem;margin-top:1rem">'
                    f'<div style="font-family:Syne;font-size:1.1rem;font-weight:700;'
                    f'color:#30D158;margin-bottom:1.2rem">✅ {s["name"]} Registered!</div>'
                    f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:1rem;margin-bottom:1rem">'
                    f'<div><div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'letter-spacing:2px;text-transform:uppercase;margin-bottom:.15rem">ID</div>'
                    f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800">#{s["student_id"]}</div></div>'
                    f'<div><div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'letter-spacing:2px;text-transform:uppercase;margin-bottom:.15rem">SEM CGPA</div>'
                    f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800;color:#BF5AF2">'
                    f'{s["current_sem_cgpa"]}/10</div></div>'
                    f'<div><div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'letter-spacing:2px;text-transform:uppercase;margin-bottom:.15rem">OVERALL CGPA</div>'
                    f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800;color:#00F5FF">'
                    f'{s["cgpa"]}/10</div></div>'
                    f'<div><div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'letter-spacing:2px;text-transform:uppercase;margin-bottom:.15rem">GRADE</div>'
                    f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800;color:{ghex}">'
                    f'{s["grade"]}</div></div>'
                    f'<div><div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'letter-spacing:2px;text-transform:uppercase;margin-bottom:.15rem">STATUS</div>'
                    f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800;color:{pf_col}">'
                    f'{s["pass_fail"]}</div></div>'
                    f'<div><div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'letter-spacing:2px;text-transform:uppercase;margin-bottom:.15rem">AT-RISK</div>'
                    f'<div style="font-size:.82rem;margin-top:.1rem">{r_html}</div></div>'
                    f'</div>'
                    f'{bar(s["final_score"])}'
                    f'<div style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3;margin-top:.3rem">'
                    f'FINAL SCORE: {s["final_score"]:.2f}/100</div>'
                    f'<div style="margin-top:.7rem;font-size:.78rem;color:#6B7FA3">{mail_note}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.error("❌ Failed to add student — ID may already exist.")


# ════════════════════════════════════════════════════════════════
# STUDENT LOOKUP
# ════════════════════════════════════════════════════════════════
elif page == "🔍  Student Lookup":
    hero("Student Lookup", "Search by integer ID · Full profile · Download report")

    df = db.get_dataframe()
    if df.empty:
        st.info("No students yet.")
        st.stop()

    sid_in = st.number_input("Enter Student ID", min_value=1,
                             max_value=999999, step=1, value=1001)
    ca, cb = st.columns(2)
    with ca: do_search = st.button("🔍 Search", use_container_width=True)
    with cb: do_delete = st.button("🗑️ Delete Student", use_container_width=True)

    if do_delete:
        if db.get_student(int(sid_in)):
            db.delete_student(int(sid_in))
            st.success(f"✅ Student #{int(sid_in)} deleted.")
        else:
            st.error(f"❌ ID #{int(sid_in)} not found.")

    if do_search:
        s = db.get_student(int(sid_in))
        if s:
            ghex    = grade_color(s["grade"])
            r_label = "⚠️ YES" if s["at_risk"] else "✅ NO"
            r_col   = "#FF453A" if s["at_risk"] else "#30D158"

            st.markdown(
                f'<div style="background:var(--card);border:1px solid var(--border);'
                f'border-radius:20px;padding:1.75rem;margin-top:.75rem">'
                f'<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.4rem">'
                f'<div style="width:60px;height:60px;'
                f'background:linear-gradient(135deg,rgba(0,245,255,.2),rgba(191,90,242,.2));'
                f'border:2px solid rgba(0,245,255,.3);border-radius:50%;display:flex;'
                f'align-items:center;justify-content:center;font-family:Syne;'
                f'font-size:1.4rem;font-weight:800;color:#00F5FF">'
                f'{s["name"][0].upper()}</div>'
                f'<div style="flex:1">'
                f'<div style="font-family:Syne;font-size:1.25rem;font-weight:800">{s["name"]}</div>'
                f'<div style="font-family:Space Mono;font-size:.6rem;color:#6B7FA3;letter-spacing:2px">'
                f'ID #{s["student_id"]} · {s["gender"].upper()} · AGE {s["age"]}</div>'
                f'<div style="font-size:.78rem;color:#6B7FA3;margin-top:.2rem">'
                f'📧 {s.get("email","—")} &nbsp;·&nbsp; 📱 {s.get("phone","—")}</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-family:Syne;font-size:2.5rem;font-weight:800;'
                f'color:{ghex};line-height:1">{s["grade"]}</div>'
                f'<div style="font-family:Space Mono;font-size:.6rem;color:#6B7FA3">'
                f'CGPA {s["cgpa"]}/10</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            fa, fb = st.columns(2)
            with fa:
                st.markdown(pfield("Domain", s["domain"]), unsafe_allow_html=True)
                st.markdown(pfield("Branch", s["branch"]), unsafe_allow_html=True)
                st.markdown(pfield("Current Sem CGPA", f'{s["current_sem_cgpa"]}/10'), unsafe_allow_html=True)
                st.markdown(pfield("Overall CGPA", f'{s["cgpa"]}/10'), unsafe_allow_html=True)
                st.markdown(pfield("Attendance", f'{s["attendance"]:.1f}%'), unsafe_allow_html=True)
                st.markdown(pfield("Midterm Score", f'{s["midterm_score"]:.1f}'), unsafe_allow_html=True)
            with fb:
                st.markdown(pfield("Study Hours/Day", f'{s["study_hours"]}h'), unsafe_allow_html=True)
                st.markdown(pfield("Screen Time/Day", f'{s["screen_time"]}h'), unsafe_allow_html=True)
                st.markdown(pfield("Sleep Hours", f'{s["sleep_hours"]}h'), unsafe_allow_html=True)
                st.markdown(pfield("Absences", str(s["absences"])), unsafe_allow_html=True)
                st.markdown(pfield("Stress Level", s["stress_level"]), unsafe_allow_html=True)
                st.markdown(pfield("At-Risk", r_label), unsafe_allow_html=True)

            # subjects tags
            subj_str = s.get("subjects", "")
            if subj_str:
                tags_html = "".join(
                    tag(t.strip()) for t in subj_str.split(",") if t.strip()
                )
                st.markdown(
                    f'<div class="pf"><div class="pf-l">Subjects / Languages / Work</div>'
                    f'<div style="margin-top:.4rem">{tags_html}</div></div>',
                    unsafe_allow_html=True,
                )

            # activities tags
            acts_str = s.get("activities", "")
            if acts_str and acts_str != "None":
                act_tags = "".join(
                    tag(a.strip(), "#BF5AF2", "rgba(191,90,242,.1)", "rgba(191,90,242,.25)")
                    for a in acts_str.split(",") if a.strip()
                )
                st.markdown(
                    f'<div class="pf"><div class="pf-l">Activities</div>'
                    f'<div style="margin-top:.4rem">{act_tags}</div></div>',
                    unsafe_allow_html=True,
                )

            fs = s["final_score"]
            st.markdown(
                f'<div style="margin-top:.75rem;background:rgba(0,0,0,.2);'
                f'border-radius:12px;padding:.9rem 1rem">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:.35rem">'
                f'<div style="font-family:Space Mono;font-size:.56rem;color:#6B7FA3;'
                f'letter-spacing:2px;text-transform:uppercase">FINAL SCORE</div>'
                f'<div style="font-family:Space Mono;font-size:.62rem;color:#00F5FF">{fs:.2f}/100</div>'
                f'</div>'
                f'{bar(fs)}'
                f'<div style="display:flex;justify-content:space-between;margin-top:.35rem">'
                f'<div style="font-size:.74rem;color:{r_col};font-weight:700">At-Risk: {r_label}</div>'
                f'<div style="font-size:.74rem;color:#6B7FA3">Pass/Fail: '
                f'<strong style="color:{"#30D158" if s["pass_fail"]==chr(80)+chr(97)+chr(115)+chr(115) else chr(35)+chr(70)+chr(70)+chr(52)+chr(53)+chr(51)+chr(65)}">'
                f'{s["pass_fail"]}</strong></div>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            sh("Download Report")
            st.download_button(
                "📄 Download TXT Report",
                data=report_text(s),
                file_name=f'student_{s["student_id"]}_{s["name"].replace(" ","_")}.txt',
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.error(f"❌ No student found with ID #{int(sid_in)}")


# ════════════════════════════════════════════════════════════════
# STUDENT SUGGESTIONS
# ════════════════════════════════════════════════════════════════
elif page == "💡  Student Suggestions":
    hero("Student Suggestions",
         "Personalised advice for each student · Search by integer ID")

    df = db.get_dataframe()
    if df.empty:
        st.info("No students yet.")
        st.stop()

    sid_in = st.number_input("Enter Student ID", min_value=1,
                             max_value=999999, step=1, value=1001, key="sug_sid")
    go_btn = st.button("💡 Get Suggestions", use_container_width=False)

    if go_btn:
        s = db.get_student(int(sid_in))
        if s:
            ghex = grade_color(s["grade"])
            st.markdown(
                f'<div style="background:var(--card);border:1px solid var(--border);'
                f'border-radius:16px;padding:1.2rem 1.5rem;margin-bottom:1.4rem;'
                f'display:flex;align-items:center;gap:1.2rem">'
                f'<div style="width:50px;height:50px;'
                f'background:linear-gradient(135deg,rgba(0,245,255,.2),rgba(191,90,242,.2));'
                f'border:2px solid rgba(0,245,255,.3);border-radius:50%;display:flex;'
                f'align-items:center;justify-content:center;font-family:Syne;'
                f'font-size:1.3rem;font-weight:800;color:#00F5FF">'
                f'{s["name"][0].upper()}</div>'
                f'<div style="flex:1">'
                f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800">{s["name"]}</div>'
                f'<div style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3;letter-spacing:2px">'
                f'ID #{s["student_id"]} · {s["branch"]} · {s["domain"]}</div>'
                f'</div>'
                f'<div style="text-align:right;margin-right:.5rem">'
                f'<div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                f'text-transform:uppercase;margin-bottom:.15rem">SEM CGPA</div>'
                f'<div style="font-family:Syne;font-size:1.3rem;font-weight:800;color:#BF5AF2">'
                f'{s["current_sem_cgpa"]}/10</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-family:Syne;font-size:1.6rem;font-weight:800;color:{ghex}">'
                f'{s["grade"]}</div>'
                f'<div style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3">'
                f'CGPA {s["cgpa"]}/10</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            tips = student_suggestions(s)
            sh(f"Personalised Insights ({len(tips)} items)")
            for kind, tag_txt, msg in tips:
                sug_card(kind, tag_txt, msg)
        else:
            st.error(f"❌ No student found with ID #{int(sid_in)}")


# ════════════════════════════════════════════════════════════════
# STUDENT ROADMAP
# ════════════════════════════════════════════════════════════════
elif page == "🗺️  Student Roadmap":
    hero("Student Roadmap",
         "Point-to-point flowchart · Personalised action plan · Search by integer ID")

    df = db.get_dataframe()
    if df.empty:
        st.info("No students yet.")
        st.stop()

    sid_in = st.number_input("Enter Student ID", min_value=1,
                             max_value=999999, step=1, value=1001, key="rm_sid")
    go_btn = st.button("🗺️ Generate Roadmap", use_container_width=False)

    if go_btn:
        s = db.get_student(int(sid_in))
        if s:
            ghex = grade_color(s["grade"])
            at_label = "⚠️ AT-RISK" if s["at_risk"] else "✅ ON TRACK"

            st.markdown(
                f'<div style="background:var(--card);border:1px solid var(--border);'
                f'border-radius:16px;padding:1.2rem 1.5rem;margin-bottom:1.4rem;'
                f'display:flex;align-items:center;gap:1.2rem">'
                f'<div style="width:50px;height:50px;'
                f'background:linear-gradient(135deg,rgba(0,245,255,.2),rgba(191,90,242,.2));'
                f'border:2px solid rgba(0,245,255,.3);border-radius:50%;display:flex;'
                f'align-items:center;justify-content:center;font-family:Syne;'
                f'font-size:1.3rem;font-weight:800;color:#00F5FF">'
                f'{s["name"][0].upper()}</div>'
                f'<div style="flex:1">'
                f'<div style="font-family:Syne;font-size:1.1rem;font-weight:800">{s["name"]}</div>'
                f'<div style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3;letter-spacing:2px">'
                f'ID #{s["student_id"]} · Sem CGPA {s["current_sem_cgpa"]}/10 · Overall CGPA {s["cgpa"]}/10'
                f'</div></div>'
                f'<div style="text-align:right">'
                f'<div style="font-family:Syne;font-size:1.6rem;font-weight:800;color:{ghex}">'
                f'{s["grade"]}</div>'
                f'<div style="font-family:Space Mono;font-size:.6rem;color:#6B7FA3">{at_label}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            # legend
            st.markdown(
                '<div style="display:flex;flex-wrap:wrap;gap:1rem;margin-bottom:1.2rem">'
                + "".join(
                    f'<div style="display:flex;align-items:center;gap:.4rem;'
                    f'font-size:.74rem;color:{clr}">'
                    f'<div style="width:10px;height:10px;background:{bg};'
                    f'border:1px solid {clr};border-radius:3px"></div>{lbl}</div>'
                    for clr, bg, lbl in [
                        ("#30D158", "rgba(48,209,88,.25)",  "Completed / Good"),
                        ("#00F5FF", "rgba(0,245,255,.2)",   "In Progress / Target"),
                        ("#FF9F0A", "rgba(255,159,10,.2)",  "Needs Attention"),
                        ("#FF453A", "rgba(255,69,58,.2)",   "Urgent / Critical"),
                    ]
                )
                + "</div>",
                unsafe_allow_html=True,
            )

            col_flow, col_stats = st.columns([2, 1])

            steps = student_roadmap(s)

            with col_flow:
                sh("Your Action Flowchart")
                for i, (badge_cls, badge_lbl, title, desc) in enumerate(steps):
                    dc, rgb = dot_rgb(badge_cls)
                    flow_node(dc, rgb, i + 1, badge_cls, badge_lbl,
                              title, desc, show_line=(i < len(steps) - 1))

            with col_stats:
                sh("Quick Stats")
                stat_rows = [
                    ("Attendance",    f'{s["attendance"]:.0f}%',     "#30D158" if s["attendance"] >= 75 else "#FF453A"),
                    ("Study Hrs/Day", f'{s["study_hours"]}h',        "#30D158" if s["study_hours"] >= 3 else "#FF9F0A"),
                    ("Screen Time",   f'{s["screen_time"]}h/day',    "#30D158" if s["screen_time"] <= 4 else "#FF453A"),
                    ("Sleep",         f'{s["sleep_hours"]}h/night',  "#30D158" if s["sleep_hours"] >= 7 else "#FF9F0A"),
                    ("Absences",      str(s["absences"]),            "#30D158" if s["absences"] <= 5 else "#FF453A"),
                    ("Stress",        s["stress_level"],             {"Low": "#30D158", "Medium": "#FF9F0A", "High": "#FF453A"}.get(s["stress_level"], "#E8F4FD")),
                    ("Sem CGPA",      f'{s["current_sem_cgpa"]}/10', "#00F5FF"),
                    ("Overall CGPA",  f'{s["cgpa"]}/10',             grade_color(s["grade"])),
                ]
                for lbl, val, clr in stat_rows:
                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--border);'
                        f'border-radius:10px;padding:.6rem .9rem;margin-bottom:.4rem;'
                        f'display:flex;justify-content:space-between;align-items:center">'
                        f'<div style="font-family:Space Mono;font-size:.58rem;color:var(--muted)">{lbl}</div>'
                        f'<div style="font-family:Syne;font-size:.93rem;font-weight:800;color:{clr}">{val}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # score bar
                fs = s["final_score"]
                st.markdown(
                    f'<div style="background:rgba(0,0,0,.2);border-radius:10px;padding:.8rem;margin-top:.5rem">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:.35rem">'
                    f'<div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'text-transform:uppercase;letter-spacing:1.5px">FINAL SCORE</div>'
                    f'<div style="font-family:Space Mono;font-size:.6rem;color:#00F5FF">{fs:.1f}/100</div>'
                    f'</div>{bar(fs)}</div>',
                    unsafe_allow_html=True,
                )

                # summary counts
                done_n   = sum(1 for bc, *_ in steps if bc == "b-done")
                warn_n   = sum(1 for bc, *_ in steps if bc in ("b-warn", "b-active"))
                danger_n = sum(1 for bc, *_ in steps if bc == "b-danger")
                st.markdown(
                    f'<div style="background:rgba(0,0,0,.2);border-radius:10px;padding:.8rem;margin-top:.5rem">'
                    f'<div style="font-family:Space Mono;font-size:.54rem;color:#6B7FA3;'
                    f'text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.5rem">ROADMAP SUMMARY</div>'
                    f'<div style="display:flex;gap:.75rem">'
                    f'<div style="text-align:center;flex:1"><div style="font-family:Syne;font-size:1.3rem;'
                    f'font-weight:800;color:#30D158">{done_n}</div>'
                    f'<div style="font-size:.63rem;color:#6B7FA3">DONE</div></div>'
                    f'<div style="text-align:center;flex:1"><div style="font-family:Syne;font-size:1.3rem;'
                    f'font-weight:800;color:#FF9F0A">{warn_n}</div>'
                    f'<div style="font-size:.63rem;color:#6B7FA3">IMPROVE</div></div>'
                    f'<div style="text-align:center;flex:1"><div style="font-family:Syne;font-size:1.3rem;'
                    f'font-weight:800;color:#FF453A">{danger_n}</div>'
                    f'<div style="font-size:.63rem;color:#6B7FA3">URGENT</div></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.error(f"❌ No student found with ID #{int(sid_in)}")


# ════════════════════════════════════════════════════════════════
# CLASS INSIGHTS
# ════════════════════════════════════════════════════════════════
elif page == "🏫  Class Insights":
    hero("Class Insights", "Overall class health · Trends · Intervention signals")

    df = db.get_dataframe()
    if df.empty:
        st.info("No students yet.")
        st.stop()

    tabs = st.tabs(["📊 Overview", "⚠️ At-Risk", "📈 Boosters", "🧘 Wellbeing"])

    with tabs[0]:
        avg_cgpa   = df["cgpa"].mean()
        pass_rate  = (df["pass_fail"] == "Pass").mean()
        avg_attend = df["attendance"].mean()
        avg_screen = df["screen_time"].mean()
        avg_study  = df["study_hours"].mean()
        at_risk_pct = df["at_risk"].mean()
        n = len(df)

        if avg_attend < 75:
            sug_card("d", "ATTENDANCE CRISIS",
                f"Class avg attendance {avg_attend:.1f}% — below 75% threshold. Deploy early-warning alerts now.")
        elif avg_attend < 85:
            sug_card("w", "LOW ATTENDANCE",
                f"Avg attendance {avg_attend:.1f}%. Introduce incentives and investigate absence patterns.")
        else:
            sug_card("g", "GREAT ATTENDANCE", f"Avg {avg_attend:.1f}% — excellent class regularity!")

        if pass_rate < 0.6:
            sug_card("d", "CRITICAL PASS RATE", f"Only {pass_rate:.1%} passing. Urgent curriculum review needed.")
        elif pass_rate < 0.8:
            sug_card("w", "BELOW TARGET", f"Pass rate {pass_rate:.1%} is below the 80% target.")
        else:
            sug_card("g", "STRONG PASS RATE", f"{pass_rate:.1%} pass rate — excellent performance!")

        if avg_screen > 5:
            sug_card("d", "CLASS SCREEN TIME",
                f"Avg {avg_screen:.1f}h/day screen time across class. Run a digital wellness session urgently.")
        elif avg_screen > 3:
            sug_card("w", "MODERATE SCREEN TIME",
                f"Avg screen time {avg_screen:.1f}h/day. Encourage phone-free study periods.")

        if at_risk_pct > 0.3:
            sug_card("d", "HIGH AT-RISK RATIO",
                f"{at_risk_pct:.1%} of students are at-risk. Deploy counsellors and peer tutors immediately.")

        high_stress_pct = (df["stress_level"] == "High").mean()
        if high_stress_pct > 0.4:
            sug_card("w", "STRESS EPIDEMIC",
                f"{high_stress_pct:.1%} of students report high stress. Schedule wellness workshops this week.")

    with tabs[1]:
        ar_df = df[df["at_risk"] == 1].copy()
        if ar_df.empty:
            sug_card("g", "STATUS", "No at-risk students — all meet minimum CGPA thresholds. 🎉")
        else:
            sug_card("d", "ALERT",
                f"{len(ar_df)} student(s) are at-risk (CGPA below 5.0). Immediate intervention required.")
            for _, row in ar_df.iterrows():
                reasons = []
                if row["attendance"] < 75:       reasons.append(f"Low attendance ({row['attendance']:.0f}%)")
                if row["study_hours"] < 2:       reasons.append(f"Low study ({row['study_hours']:.1f}h/day)")
                if row["stress_level"] == "High":reasons.append("High stress")
                if row["absences"] > 10:         reasons.append(f"High absences ({int(row['absences'])})")
                if row["screen_time"] > 5:       reasons.append(f"Screen time ({row['screen_time']:.1f}h)")
                reasons_str = " · ".join(reasons) if reasons else "Multiple factors"
                st.markdown(
                    f'<div style="background:rgba(255,69,58,.06);border:1px solid rgba(255,69,58,.2);'
                    f'border-radius:13px;padding:.95rem 1.2rem;margin-bottom:.6rem">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:.3rem">'
                    f'<div><span style="font-family:Syne;font-size:.98rem;font-weight:700">'
                    f'{row["name"]}</span>'
                    f'<span style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3;margin-left:.7rem">'
                    f'ID #{int(row["student_id"])}</span></div>'
                    f'<div style="font-family:Space Mono;font-size:.66rem;color:#FF453A;font-weight:700">'
                    f'CGPA {row["cgpa"]}/10</div></div>'
                    f'<div style="font-size:.77rem;color:#FF9F0A;margin-bottom:.2rem">⚡ {reasons_str}</div>'
                    f'<div style="font-size:.75rem;color:#6B7FA3">'
                    f'Action: 1-on-1 counsellor · peer tutor · parent notification</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with tabs[2]:
        sug_card("", "STUDY HOURS ROI",
            "Students studying 3+ hrs/day consistently earn higher CGPA. Encourage structured study schedules.")
        sug_card("w", "SCREEN TIME IMPACT",
            "Each extra hour beyond 4h screen time costs ~1.5 final score points. Promote digital-detox habits.")
        sug_card("w", "ABSENCE PENALTY",
            "Each absence costs ~0.5 final score points. 10 absences = 5-point drop — communicate this clearly.")
        sug_card("d", "STRESS EFFECT",
            "High-stress students score 7 points lower on average. Integrate stress management into the calendar.")
        sug_card("p", "GAMING INSIGHT",
            "Students with gaming + high screen time (>5h) show 0.8 lower CGPA. Set limits, not bans.")
        if len(df) >= 3:
            dv()
            sh("Top 5 Performers")
            top5 = df.nlargest(5, "cgpa")[
                ["student_id", "name", "domain", "cgpa", "grade", "attendance", "screen_time"]
            ]
            st.dataframe(top5, use_container_width=True, hide_index=True)

    with tabs[3]:
        avg_sleep  = df["sleep_hours"].mean()
        poor_sleep = int((df["sleep_hours"] < 6).sum())
        high_st    = int((df["stress_level"] == "High").sum())
        low_act    = int((df["activities"] == "None").sum())
        n = len(df)

        sk = "d" if poor_sleep > n * .3 else "w" if poor_sleep > 0 else "g"
        sug_card(sk, "SLEEP HEALTH",
            f"{poor_sleep} student(s) sleep fewer than 6h/night. Class avg: {avg_sleep:.1f}h. "
            "Run a sleep hygiene session and recommend screen-time curfews.")

        stk = "d" if high_st > n * .4 else "w" if high_st > 0 else "g"
        sug_card(stk, "STRESS LEVELS",
            f"{high_st} student(s) report high stress ({high_st/n:.1%} of class). "
            "Introduce mindfulness and reduce assignment pile-up.")

        ack = "w" if low_act > n * .3 else "g"
        sug_card(ack, "ZERO ACTIVITIES",
            f"{low_act} student(s) have no extracurricular activities. "
            "Promote clubs, sports, and arts — even 1 activity improves wellbeing.")


# ════════════════════════════════════════════════════════════════
# 
# elif page == "🤖  AI Chatbot":
#     hero("AI Chatbot", "Powered by Gemini · Ask anything about student performance")

#     # ── init Gemini ──────────────────────────────────────────────
#     try:
#         api_key = st.secrets.get("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
#         if not api_key:
#             st.error("❌ GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml")
#             st.stop()
#         genai.configure(api_key=api_key)
#         model = genai.GenerativeModel("gemini-2.5-flash")
#     except Exception as e:
#         st.error(f"❌ Gemini init error: {e}")
#         st.stop()

#     # ── session state ────────────────────────────────────────────
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # ── system prompt (base + class stats) ───────────────────────
#     base_sys = (
#         "You are EduSense AI Advisor — a compassionate, smart, and practical student academic counsellor. "
#         "You help students with study problems, stress, time management, career guidance, and performance improvement. "
#         "Be concise, warm, and actionable. Use bullet points for suggestions. Always be encouraging. "
#         "Never be discouraging. If a student seems distressed, acknowledge their feelings first before giving advice. "
#         "Format responses clearly. Keep replies under 300 words unless a detailed plan is specifically needed."
#     )

#     # ── class-level context ───────────────────────────────────────
#     df = db.get_dataframe()
#     if not df.empty:
#         class_ctx = (
#             f"\n\nClass Stats: {len(df)} students, avg CGPA {df['cgpa'].mean():.2f}/10, "
#             f"pass rate {(df['pass_fail']=='Pass').mean():.1%}, "
#             f"at-risk count {int(df['at_risk'].sum())}."
#         )
#     else:
#         class_ctx = "\n\nNo students registered yet."

#     # ── student profile context (if a student is linked) ─────────
#     if st.session_state.get("chat_student"):
#         s = st.session_state.chat_student
#         profile_ctx = (
#             f"\n\nStudent Profile:\n"
#             f"Name: {s['name']}, ID: #{s['student_id']}\n"
#             f"Domain: {s['domain']}, Branch: {s['branch']}\n"
#             f"Semester CGPA: {s['current_sem_cgpa']}/10, Overall CGPA: {s['cgpa']}/10, Grade: {s['grade']}\n"
#             f"Attendance: {s['attendance']:.0f}%, Study: {s['study_hours']}h/day, "
#             f"Screen: {s['screen_time']}h/day, Sleep: {s['sleep_hours']}h/night\n"
#             f"Absences: {s['absences']}, Stress: {s['stress_level']}, At-Risk: {'YES' if s['at_risk'] else 'NO'}\n"
#             f"Activities: {s.get('activities', 'None')}\n"
#             f"Subjects: {s.get('subjects', '')}\n"
#             "Use this profile to personalise every response."
#         )
#         sys_prompt = base_sys + class_ctx + profile_ctx
#     else:
#         sys_prompt = base_sys + class_ctx

#     # ── gemini call helper ────────────────────────────────────────
#     def call_gemini(history: list, system: str) -> str:
#         history_text = "\n".join(
#             f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
#             for m in history[:-1]
#         )
#         last_input = history[-1]["content"]
#         full_prompt = f"{system}\n\n{history_text}\nUser: {last_input}\nAssistant:"
#         try:
#             with st.spinner("Thinking..."):
#                 response = model.generate_content(full_prompt)
#                 return response.text
#         except Exception as e:
#             return f"⚠️ Error: {e}"

#     # ── welcome message or chat history display ───────────────────
#     if not st.session_state.chat_history:
#         st.markdown(
#             '<div class="cb-b"><div class="cb-name">EDUSENSE AI ADVISOR</div>'
#             "👋 Hi! I'm your EduSense AI Advisor. I can help with:<br><br>"
#             "📚 Study strategies &amp; CGPA improvement<br>"
#             "😓 Stress, burnout &amp; mental health<br>"
#             "📱 Screen time &amp; digital distraction<br>"
#             "⏱️ Time management &amp; daily routines<br>"
#             "🎮 Balancing gaming &amp; academics<br>"
#             "💼 Career guidance &amp; subject choices<br><br>"
#             "Just describe your problem naturally — I'll give you practical, personalised advice!<br>"
#             '<em style="color:#6B7FA3;font-size:.78rem">Tip: link your student profile above for personalised insights.</em>'
#             "</div>",
#             unsafe_allow_html=True,
#         )
#     else:
#         for msg in st.session_state.chat_history:
#             if msg["role"] == "user":
#                 st.markdown(
#                     f'<div class="cb-u"><div class="cb-name">YOU</div>{msg["content"]}</div>',
#                     unsafe_allow_html=True,
#                 )
#             else:
#                 content_fmt = msg["content"].replace("\n", "<br>")
#                 st.markdown(
#                     f'<div class="cb-b"><div class="cb-name">✦ EDUSENSE AI ADVISOR</div>'
#                     f'{content_fmt}</div>',
#                     unsafe_allow_html=True,
#                 )

#     st.markdown("<br>", unsafe_allow_html=True)

#     # ── chat form (input + send/clear buttons) ────────────────────
#     with st.form("chat_form", clear_on_submit=True):
#         user_input = st.text_area(
#             "Your message",
#             placeholder="e.g. I can't focus while studying, my CGPA dropped, I feel burnt out...",
#             height=80,
#             label_visibility="collapsed",
#         )
#         send_c, clear_c = st.columns([4, 1])
#         with send_c:
#             send_btn = st.form_submit_button("⚡ Send", use_container_width=True)
#         with clear_c:
#             clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

#     if clear_btn:
#         st.session_state.chat_history = []
#         st.rerun()

#     if send_btn and user_input.strip():
#         st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
#         reply = call_gemini(st.session_state.chat_history, sys_prompt)
#         st.session_state.chat_history.append({"role": "assistant", "content": reply})
#         st.rerun()

#     # ── quick prompt buttons ──────────────────────────────────────
#     dv()
#     st.markdown(
#         '<div style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3;'
#         'letter-spacing:2px;text-transform:uppercase;margin-bottom:.6rem">QUICK QUESTIONS</div>',
#         unsafe_allow_html=True,
#     )
#     quick_qs = [
#         "How can I improve my CGPA this semester?",
#         "I feel burnt out and can't study. Help!",
#         "How do I manage screen time better?",
#         "I'm stressed about exams. Any tips?",
#         "How many hours should I study daily?",
#         "How do I balance gaming and studies?",
#     ]
#     qcols = st.columns(3)
#     for i, q in enumerate(quick_qs):
#         with qcols[i % 3]:
#             if st.button(q, key=f"q{i}", use_container_width=True):
#                 st.session_state.chat_history.append({"role": "user", "content": q})
#                 reply = call_gemini(st.session_state.chat_history, sys_prompt)
#                 st.session_state.chat_history.append({"role": "assistant", "content": reply})
#                 st.rerun()
elif page == "🤖  AI Chatbot":
    hero("AI Chatbot", "Powered by Gemini · Ask anything about student performance")

    # ── init Gemini ──────────────────────────────────────────────
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("❌ GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml")
            st.stop()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        st.error(f"❌ Gemini init error: {e}")
        st.stop()

    # ── session state ────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_student" not in st.session_state:
        st.session_state.chat_student = None

    # ── student ID lookup panel ───────────────────────────────────
    st.markdown("#### 🔍 Link a Student Profile")
    id_col, btn_col, clear_col = st.columns([3, 1, 1])
    with id_col:
        student_id_input = st.text_input(
            "Enter Student ID",
            placeholder="e.g. 1001",
            label_visibility="collapsed",
        )
    with btn_col:
        link_btn = st.button("🔗 Link", use_container_width=True)
    with clear_col:
        unlink_btn = st.button("❌ Unlink", use_container_width=True)

    if link_btn and student_id_input.strip():
        df = db.get_dataframe()
        # try matching by student_id column (adjust column name if different)
        match = df[df["student_id"].astype(str) == student_id_input.strip()]
        if not match.empty:
            st.session_state.chat_student = match.iloc[0].to_dict()
            st.session_state.chat_history = []   # fresh chat for new student
            st.success(f"✅ Linked to **{st.session_state.chat_student['name']}** (ID: {student_id_input.strip()})")
        else:
            st.error(f"❌ No student found with ID '{student_id_input.strip()}'")

    if unlink_btn:
        st.session_state.chat_student = None
        st.session_state.chat_history = []
        st.rerun()

    # ── show linked student badge ─────────────────────────────────
    if st.session_state.chat_student:
        s = st.session_state.chat_student
        st.markdown(
            f'<div style="background:#1E2A3A;border-left:3px solid #4A90D9;padding:.6rem 1rem;'
            f'border-radius:6px;margin:.5rem 0;font-family:Space Mono;font-size:.78rem;color:#A8C4E0;">'
            f'🎓 <b>{s["name"]}</b> &nbsp;|&nbsp; ID: {s["student_id"]} &nbsp;|&nbsp; '
            f'CGPA: {s["cgpa"]}/10 &nbsp;|&nbsp; '
            f'{"🔴 At-Risk" if s["at_risk"] else "🟢 On Track"}'
            f'</div>',
            unsafe_allow_html=True,
        )

    dv()

    # ── build system prompt ───────────────────────────────────────
    base_sys = (
        "You are EduSense AI Advisor — a compassionate, smart, and practical student academic counsellor. "
        "You help students with study problems, stress, time management, career guidance, and performance improvement. "
        "Be concise, warm, and actionable. Use bullet points for suggestions. Always be encouraging. "
        "Never be discouraging. If a student seems distressed, acknowledge their feelings first before giving advice. "
        "Format responses clearly. Keep replies under 300 words unless a detailed plan is specifically needed."
    )

    # ── class-level context ───────────────────────────────────────
    df = db.get_dataframe()
    if not df.empty:
        class_ctx = (
            f"\n\nClass Stats: {len(df)} students, avg CGPA {df['cgpa'].mean():.2f}/10, "
            f"pass rate {(df['pass_fail']=='Pass').mean():.1%}, "
            f"at-risk count {int(df['at_risk'].sum())}."
        )
    else:
        class_ctx = "\n\nNo students registered yet."

    # ── student profile context ───────────────────────────────────
    if st.session_state.chat_student:
        s = st.session_state.chat_student
        profile_ctx = (
            f"\n\nYou are currently advising this specific student. Use their data to give "
            f"highly personalised suggestions in every response:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Name        : {s['name']}\n"
            f"Student ID  : {s['student_id']}\n"
            f"Domain      : {s.get('domain', 'N/A')}\n"
            f"Branch      : {s.get('branch', 'N/A')}\n"
            f"Semester CGPA : {s.get('current_sem_cgpa', 'N/A')}/10\n"
            f"Overall CGPA  : {s['cgpa']}/10\n"
            f"Grade         : {s.get('grade', 'N/A')}\n"
            f"Attendance    : {s.get('attendance', 'N/A')}%\n"
            f"Study Hours   : {s.get('study_hours', 'N/A')} hrs/day\n"
            f"Screen Time   : {s.get('screen_time', 'N/A')} hrs/day\n"
            f"Sleep Hours   : {s.get('sleep_hours', 'N/A')} hrs/night\n"
            f"Absences      : {s.get('absences', 'N/A')}\n"
            f"Stress Level  : {s.get('stress_level', 'N/A')}\n"
            f"At-Risk       : {'YES ⚠️' if s['at_risk'] else 'NO ✅'}\n"
            f"Activities    : {s.get('activities', 'None')}\n"
            f"Subjects      : {s.get('subjects', 'N/A')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Always refer to the student by their first name. Give specific, data-driven advice "
            f"based on their actual numbers above."
        )
        sys_prompt = base_sys + class_ctx + profile_ctx
    else:
        sys_prompt = base_sys + class_ctx + (
            "\n\nNo student profile is linked yet. You can give general academic advice, "
            "or ask the user to link a student ID for personalised suggestions."
        )

    # ── gemini call helper ────────────────────────────────────────
    def call_gemini(history: list, system: str) -> str:
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in history[:-1]
        )
        last_input = history[-1]["content"]
        full_prompt = f"{system}\n\n{history_text}\nUser: {last_input}\nAssistant:"
        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(full_prompt)
                return response.text
        except Exception as e:
            return f"⚠️ Error: {e}"

    # ── welcome message or chat history ──────────────────────────
    if not st.session_state.chat_history:
        welcome_name = (
            f" for <b>{st.session_state.chat_student['name']}</b>"
            if st.session_state.chat_student else ""
        )
        st.markdown(
            f'<div class="cb-b"><div class="cb-name">EDUSENSE AI ADVISOR</div>'
            f"👋 Hi! I'm your EduSense AI Advisor{welcome_name}. I can help with:<br><br>"
            "📚 Study strategies &amp; CGPA improvement<br>"
            "😓 Stress, burnout &amp; mental health<br>"
            "📱 Screen time &amp; digital distraction<br>"
            "⏱️ Time management &amp; daily routines<br>"
            "🎮 Balancing gaming &amp; academics<br>"
            "💼 Career guidance &amp; subject choices<br><br>"
            "Just describe your problem naturally — I'll give you practical, personalised advice!<br>"
            '<em style="color:#6B7FA3;font-size:.78rem">Tip: link a student ID above for personalised insights.</em>'
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="cb-u"><div class="cb-name">YOU</div>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                content_fmt = msg["content"].replace("\n", "<br>")
                st.markdown(
                    f'<div class="cb-b"><div class="cb-name">✦ EDUSENSE AI ADVISOR</div>'
                    f'{content_fmt}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── chat form ─────────────────────────────────────────────────
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message",
            placeholder="e.g. How can I improve my CGPA? I feel burnt out...",
            height=80,
            label_visibility="collapsed",
        )
        send_c, clear_c = st.columns([4, 1])
        with send_c:
            send_btn = st.form_submit_button("⚡ Send", use_container_width=True)
        with clear_c:
            clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.chat_history = []
        st.rerun()

    if send_btn and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        reply = call_gemini(st.session_state.chat_history, sys_prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    # ── quick prompt buttons ──────────────────────────────────────
    dv()
    st.markdown(
        '<div style="font-family:Space Mono;font-size:.58rem;color:#6B7FA3;'
        'letter-spacing:2px;text-transform:uppercase;margin-bottom:.6rem">QUICK QUESTIONS</div>',
        unsafe_allow_html=True,
    )
    quick_qs = [
        "How can I improve my CGPA this semester?",
        "I feel burnt out and can't study. Help!",
        "How do I manage screen time better?",
        "I'm stressed about exams. Any tips?",
        "How many hours should I study daily?",
        "How do I balance gaming and studies?",
    ]
    qcols = st.columns(3)
    for i, q in enumerate(quick_qs):
        with qcols[i % 3]:
            if st.button(q, key=f"q{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                reply = call_gemini(st.session_state.chat_history, sys_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()