# app.py
import streamlit as st
import PyPDF2
import io
import os
import re
import time
import base64
from dotenv import load_dotenv
from datetime import datetime
from tinydb import TinyDB
import pandas as pd
import plotly.graph_objects as go
import difflib
from project_lookup import get_projects_for_domain
from soft_skills_videos import render_soft_skills_videos


# Optional Groq client (only used for textual AI analysis if you set GROQ_API_KEY)
try:
    from groq import Groq
except Exception:
    Groq = None

# -------------------------
# CONFIG & INIT
# -------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
client = Groq(api_key=GROQ_API_KEY) if (GROQ_API_KEY and Groq is not None) else None

DB_PATH = "resume_reports.json"
db = TinyDB(DB_PATH)

st.set_page_config(page_title="AI Resume Dashboard — Universal ATS (20 domains)", page_icon="🛰️", layout="wide")

# -------------------------
# HIGH-GRAPHICS CSS / JS (CDNs)
# -------------------------
st.markdown(
    """
<link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.1/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">

<style>
:root{
  --bg1:#040614; --card:#061026; --glass:rgba(255,255,255,0.03);
  --accent1:#2dd4bf; --accent2:#7c3aed; --muted:#8fa7bd;
}
body, .stApp{ background: radial-gradient(800px 400px at 10% 8%, rgba(124,58,237,0.02), transparent), linear-gradient(180deg,var(--bg1),#061129 80%); color:#e6eef8; font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto; }
.topbar{ padding:16px 22px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.03); }
.brand{ font-weight:900; font-size:18px; background:linear-gradient(90deg,var(--accent1),var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.sidebar-card{ background:var(--card); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.02); box-shadow:0 8px 30px rgba(0,0,0,0.5); }
.glass-card{ background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:18px; border-radius:12px; border:1px solid rgba(255,255,255,0.03); }
.kpi{ font-weight:800; font-size:20px; color:#e9fbff; }
.muted{ color:var(--muted); font-size:13px; }
.result-box{ background: rgba(6,10,18,0.6); padding:14px; border-radius:10px; border-left:3px solid var(--accent1); white-space:pre-wrap; font-family: ui-monospace, monospace; color:#dff6ff; }
.small{ font-size:12px; color:#9fb0c9 }
.footer{ text-align:center; color:#7f9bb0; padding:14px 0; margin-top:12px; }

/* responsive */
@media (max-width:900px){
  .brand{ font-size:16px; }
}
</style>

<!-- JS libs -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.7.2/vanilla-tilt.min.js"></script>

<script>
setTimeout(()=> {
  try {
    document.querySelectorAll('.glass-card').forEach((el,i)=> {
      el.style.transformOrigin = "center center";
      el.style.transition = "transform 0.5s ease, box-shadow 0.5s ease";
      el.onmouseover = ()=> el.style.transform = "translateY(-6px) scale(1.01)";
      el.onmouseleave = ()=> el.style.transform = "none";
    });
  } catch(e){}
}, 400);
</script>
""", unsafe_allow_html=True)

# -------------------------
# DOMAIN SKILL DICTIONARIES (20 domains)
# Add or edit keywords as needed.
# -------------------------
DOMAINS = {
    "cyber_security": {
        "label": "Cyber Security",
        "core": ["cyber security","cybersecurity","security engineer","security analyst","incident response","soc","siem","threat intelligence","forensics","intrusion detection","red team","blue team"],
        "tools": ["nmap","nessus","qualys","metasploit","burp","wireshark","snort","suricata","splunk","elk","ids","ips","firewall","vpn"],
        "certs": ["cissp","oscp","ceh","security+","cism","cisa"]
    },
    "devops_aws": {
        "label": "AWS / DevOps",
        "core": ["devops","aws","cloud","ci/cd","infrastructure as code","infrastructure-as-code","pipeline","automation","sre"],
        "tools": ["ec2","s3","lambda","vpc","cloudformation","terraform","ansible","docker","kubernetes","jenkins","github-actions","gitlab-ci"],
        "certs": ["aws certified","aws certification","cka","ckad"]
    },
    "cloud_architect": {
        "label": "Cloud Architect",
        "core": ["cloud architect","cloud solutions","cloud architecture","scalability","high availability"],
        "tools": ["aws","azure","gcp","terraform","cloudformation","kubernetes","vpc","load balancer"],
        "certs": ["aws certified solutions architect","google cloud professional cloud architect","azure solutions architect"]
    },
    "ai_ml": {
        "label": "AI / ML",
        "core": ["machine learning","ml","deep learning","neural network","modeling","prediction","training","computer vision","nlp"],
        "tools": ["tensorflow","pytorch","scikit-learn","keras","opencv","transformers","pandas","numpy"],
        "certs": ["none"]
    },
    "data_analyst": {
        "label": "Data Analyst",
        "core": ["data analyst","analysis","analytics","business intelligence","reporting","dashboard","insights"],
        "tools": ["sql","excel","powerbi","tableau","looker","python","pandas","r"],
        "certs": ["google data analytics","tableau certified"]
    },
    "data_engineer": {
        "label": "Data Engineer",
        "core": ["data engineering","etl","pipeline","data pipeline","big data","data lake","batch processing"],
        "tools": ["spark","hadoop","airflow","kafka","mysql","postgres","redshift","bigquery"],
        "certs": ["google cloud data engineer","aws data engineer"]
    },
    "backend": {
        "label": "Backend Developer",
        "core": ["backend","api","microservice","rest api","restful","server-side","server side"],
        "tools": ["python","java","node","express","spring","django","flask","go","sql","nosql"],
        "certs": []
    },
    "frontend": {
        "label": "Frontend Developer",
        "core": ["frontend","front end","ui developer","web developer","react developer","angular developer","vue"],
        "tools": ["html","css","javascript","react","angular","vue","typescript","webpack"],
        "certs": []
    },
    "fullstack": {
        "label": "Fullstack Developer",
        "core": ["fullstack","full-stack","end-to-end","frontend and backend","full stack"],
        "tools": ["react","node","django","flask","sql","mongodb","docker"],
        "certs": []
    },
    "ui_ux": {
        "label": "UI/UX Designer",
        "core": ["ui ux","ui/ux","user research","interaction design","wireframe","prototyping"],
        "tools": ["figma","sketch","adobe xd","invision","zeplin"],
        "certs": []
    },
    "qa_testing": {
        "label": "QA / Testing",
        "core": ["qa","quality assurance","testing","test automation","sdet"],
        "tools": ["selenium","pytest","jmeter","cucumber","postman"],
        "certs": []
    },
    "network_engineer": {
        "label": "Network Engineer",
        "core": ["network engineer","routing","switching","ospf","bgp","lan wan"],
        "tools": ["cisco","juniper","iptables","wireshark"],
        "certs": ["ccna","ccnp"]
    },
    "project_manager": {
        "label": "Project Manager",
        "core": ["project manager","project management","stakeholder","scrum master","agile"],
        "tools": ["jira","confluence","ms project"],
        "certs": ["pmp","scrum master"]
    },
    "business_analyst": {
        "label": "Business Analyst",
        "core": ["business analyst","requirements","stakeholder","process mapping"],
        "tools": ["excel","powerbi","tableau","sql"],
        "certs": []
    },
    "hr": {
        "label": "HR",
        "core": ["human resources","hr","recruitment","talent acquisition","onboarding"],
        "tools": ["workday","bamboohr"],
        "certs": []
    },
    "finance": {
        "label": "Finance",
        "core": ["finance","financial analysis","fp&a","forecasting","budgeting"],
        "tools": ["excel","sap","oracle","quickbooks"],
        "certs": ["cfa","cpa"]
    },
    "accounting": {
        "label": "Accounting",
        "core": ["accountant","accounting","bookkeeping","auditing","tax"],
        "tools": ["quickbooks","sap","tally"],
        "certs": ["cpa"]
    },
    "marketing": {
        "label": "Marketing",
        "core": ["marketing","seo","content marketing","social media","campaign"],
        "tools": ["google analytics","facebook ads","seo","sem","mailchimp"],
        "certs": []
    },
    "sales": {
        "label": "Sales",
        "core": ["sales","business development","bd","account executive","closing"],
        "tools": ["crm","salesforce","hubspot"],
        "certs": []
    },
    "product_manager": {
        "label": "Product Manager",
        "core": ["product manager","product management","roadmap","prioritization","product strategy"],
        "tools": ["jira","monday","productboard"],
        "certs": []
    }

}

# -------------------------
# Helper functions
# -------------------------
def tokenize(text: str):
    return re.findall(r"\w+", (text or "").lower())

def extract_text_from_pdf_bytes(b: bytes):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(b))
        txt = ""
        for p in reader.pages:
            txt += (p.extract_text() or "") + "\n"
        return txt
    except Exception:
        return ""

def extract_uploaded_text(uploaded):
    if not uploaded:
        return ""
    if hasattr(uploaded, "type") and uploaded.type == "application/pdf":
        return extract_text_from_pdf_bytes(uploaded.read())
    try:
        return uploaded.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""

def detect_domain_from_title(title):
    """Simple domain detection from target job role text."""
    if not title:
        return None
    t = title.lower()
    # map keywords to domain keys (search order matters)
    mapping = {
        "cyber": "cyber_security",
        "security": "cyber_security",
        "devops": "devops_aws",
        "aws": "devops_aws",
        "cloud architect": "cloud_architect",
        "cloud": "cloud_architect",
        "machine learning": "ai_ml",
        "ml engineer": "ai_ml",
        "data scientist": "ai_ml",
        "data analyst": "data_analyst",
        "data engineer": "data_engineer",
        "backend": "backend",
        "frontend": "frontend",
        "fullstack": "fullstack",
        "ui/ux": "ui_ux",
        "ux": "ui_ux",
        "qa": "qa_testing",
        "test": "qa_testing",
        "network": "network_engineer",
        "project manager": "project_manager",
        "product manager": "product_manager",
        "business analyst": "business_analyst",
        "hr": "hr",
        "finance": "finance",
        "accountant": "accounting",
        "marketing": "marketing",
        "sales": "sales"
    }
    for k, v in mapping.items():
        if k in t:
            return v
    return None

def detect_domain_from_resume(resume_text):
    """Fallback: choose domain with highest core keyword matches in resume."""
    resume = (resume_text or "").lower()
    best = None
    best_count = 0
    for key, val in DOMAINS.items():
        core = val.get("core", [])
        count = sum(1 for token in core if token in resume)
        if count > best_count:
            best_count = count
            best = key
    return best if best_count > 0 else None

def count_matches_in_text(word_list, text):
    t = (text or "").lower()
    return sum(1 for w in word_list if w in t)

def tokenize(text: str):
    return re.findall(r"\w+", (text or "").lower())


def smart_match(keyword, text):
    text_tokens = tokenize(text)
    kw_tokens = keyword.lower().split()
    for t in text_tokens:
        if difflib.SequenceMatcher(None, t, keyword.lower()).ratio() > 0.70:
            return True
        for k in kw_tokens:
            if difflib.SequenceMatcher(None, t, k).ratio() > 0.75:
                return True
    return False


def count_matches(word_list, text):
    return sum(1 for word in word_list if smart_match(word, text))


def compute_domain_ats(resume_text: str, jd_text: str = ""):
    resume = re.sub(r"[^a-z0-9]+", " ", resume_text.lower())
    jd = re.sub(r"[^a-z0-9]+", " ", jd_text.lower())

    # detect domain
    domain_key_resume = detect_domain_from_resume(resume_text)
    domain_key_target = detect_domain_from_title(jd_text)

    # if user explicitly types role → respect it
    domain_key = domain_key_target or domain_key_resume or "fullstack"
    domain = DOMAINS.get(domain_key, DOMAINS["fullstack"])

    # core/tool/cert matches
    core_hits = count_matches(domain["core"], resume)
    tool_hits = count_matches(domain["tools"], resume)
    cert_hits = count_matches(domain.get("certs", []), resume)

    # resume match score
    resume_match = (
        (core_hits / max(1, len(domain["core"]))) * 0.75 +
        (tool_hits / max(1, len(domain["tools"]))) * 0.25
    )

    # job role relevance scoring
    job_role_relevance = 0.0
    if jd_text:
        for kw in domain["core"] + domain["tools"]:
            if kw in jd:
                job_role_relevance += 1

        job_role_relevance = min(1.0, job_role_relevance / 20.0)

    # final weighted score
    final_score = (
        resume_match * 0.75 +
        job_role_relevance * 0.25
    ) * 100

    # compute alt scores
    alt_scores = {}
    for k, d in DOMAINS.items():
        core_h = count_matches(d["core"], resume)
        tool_h = count_matches(d["tools"], resume)
        base = (core_h / max(1, len(d["core"]))) * 0.7 + (tool_h / max(1, len(d["tools"]))) * 0.3
        alt_scores[k] = int(round(base * 100))

    return {
        "domain_key": domain_key,
        "domain_label": domain["label"],
        "score": int(round(final_score)),
        "core_hits": core_hits,
        "tool_hits": tool_hits,
        "cert_hits": cert_hits,
        "length": len(tokenize(resume)),
        "alt_scores": alt_scores
    }




# -------------------------
# Optional Groq wrapper for AI analysis (keeps safe)
# -------------------------
def safe_ai_analysis(resume_text, role_text, max_tokens=700):
    if client is None:
        return "AI analysis not available (GROQ_API_KEY not set). The ATS scoring is still functional."
    try:
        prompt = f"""You are a senior experienced recruiter. Given the resume text below and the target role, provide:
- Short summary (1-2 lines)
- Top 5 strengths
- Top 5 actionable improvements (concrete edits, wording suggestions)
Return as plain text with headings.
Target role: {role_text}

Resume:
{resume_text}
"""
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            temperature=0.6,
            max_completion_tokens=max_tokens,
            stream=False
        )
        try:
            return resp.choices[0].message.content
        except Exception:
            return str(resp)
    except Exception as e:
        return f"AI error: {e}"

# -------------------------
# Utilities: HTML export
# -------------------------
def make_html_report(title, role, resume_text, ai_analysis, ats_result):
    now = datetime.now().isoformat(timespec="seconds")
    html = f"""<!doctype html>
    <html>
    <head><meta charset="utf-8"><title>{title}</title>
    <style>body{{font-family:Inter,Arial; background:#051026;color:#e8f4ff;padding:20px}} .card{{background:#071428;padding:20px;border-radius:10px}}</style>
    </head><body>
    <div class="card"><h1>{title}</h1><p><b>Target:</b> {role}</p><p><b>ATS score:</b> {ats_result['score']}/100</p><h3>AI Analysis</h3><pre>{ai_analysis}</pre><h3>Resume</h3><pre>{resume_text}</pre><hr/><small>Generated: {now}</small></div></body></html>"""
    return html

def html_download_link(content, filename="report.html"):
    b = base64.b64encode(content.encode("utf-8")).decode()
    return f"data:text/html;base64,{b}"

# -------------------------
# Soft Skills Importance Description (GLOBAL TEXT)
# -------------------------
SOFT_SKILLS_DESCRIPTION = """
🌟 The Critical Importance of Soft Skills in Any Job Sector

1️⃣ Soft Skills Drive Human Interaction Beyond Technical Knowledge -
Soft skills enable individuals to communicate, collaborate, and connect effectively on a human level, something that cannot be substituted by technical expertise alone. Jobs today are not just about executing tasks, but about interacting with teams, clients, managers, and systems of people. A person might have the highest technical capability, but without empathy, clarity of speech, and listening ability, the effectiveness of their contribution diminishes significantly. Human workplaces thrive on emotional resonance, mutual respect, and shared understanding. Soft skills are what shape the emotional climate of an organization. They are the glue that binds team effort into collective achievement. Ultimately, soft skills transform knowledge into impact.

2️⃣ Soft Skills Build Leadership Potential and Career Growth - 
Soft-skill-driven individuals naturally become leaders even without formal titles, because people respect their attitude, communication, and reliability. Leadership is not about giving commands, but about inspiring vision, direction, and confidence. A technically skilled person may perform work effectively, but a person with strong interpersonal awareness can influence others to join in, align, and execute objectives together. Over time, soft skills accelerate promotions and reputation more significantly than technical abilities alone. Those with leadership-grade soft skills become trusted decision-makers, mentors, and innovators. They create psychological safety around them, allowing others to express ideas openly. Ultimately, soft skills unlock upward mobility across the organizational ladder.

3️⃣ Soft Skills Strengthen Collaboration and Reduce Workplace Friction - 
Workplaces are full of different personalities, cultural backgrounds, communication styles, and behavioral patterns. Soft skills enable understanding instead of conflict, cooperation instead of confrontation. Professionals with diplomacy and patience de-escalate tensions and prevent emotional overspill. This leads to smoother meetings, faster decisions, and clearer expectations. When employees work harmoniously, project progress accelerates naturally. Soft skills create environments where people feel heard, valued, and supported. Unlike technical skills, which help an individual perform tasks, soft skills help entire groups function as synchronized units. The absence of soft skills leads to misunderstandings, resentment, and organizational stagnation.

4️⃣ Soft Skills Enable Effective Communication of Ideas and Expertise - 
Being knowledgeable is one thing—clearly articulating knowledge is another. A person may have a brilliant idea, but if they cannot explain it concisely, confidently, and persuasively, the idea remains dormant and invisible. Soft skills enable professionals to express themselves with clarity, adapt their message to different audiences, and provide compelling context. This applies to executives presenting strategies, programmers explaining technical issues, teachers conveying concepts, and marketers influencing customers. Communication is the vehicle of influence. It determines whether your message inspires action or falls unnoticed. Ultimately, soft skills allow your voice to become a tool of impact.

5️⃣ Soft Skills Increase Adaptability in a Continuously Changing Workplace -
Modern industries evolve rapidly, with technologies, priorities, and workflows shifting frequently. Professionals with adaptable mindsets absorb change with resilience rather than resistance. Such individuals embrace learning, quickly adjust to new conditions, and maintain performance even during transformational periods. Soft skills help them remain motivated, flexible, and optimistic instead of anxious or stagnant. When organizations restructure or pivot strategies, adaptable individuals become valuable anchors of stability. They overcome obstacles creatively and refrain from emotional paralysis. Ultimately, soft skills equip professionals to remain relevant in environments where yesterday’s skills may not match tomorrow’s demands.

6️⃣ Soft Skills Contribute to Customer and Client Satisfaction -
Jobs that involve customers—whether internal or external—depend heavily on trust, empathy, and reassurance. Soft skills allow professionals to understand customer expectations, manage disappointments, and articulate solutions. A client may forgive a technical mistake, but rarely forgives disrespect, impatience, or disinterest. Soft skills make customers feel respected and cared for, strengthening loyalty and long-term relationship value. In business, relationships are assets. The ability to handle people gracefully can be more valuable than any tool or algorithm. Ultimately, soft skills are the foundation of customer experience and brand perception.

7️⃣ Soft Skills Support Emotional Stability and Professional Behavior -
Work environments come with pressure, deadlines, obstacles, and interpersonal challenges. Emotional intelligence enables individuals to remain composed rather than reactive. Professionals with emotional discipline do not allow stress to influence their tone, relationship dynamics, or judgment. They maintain maturity even in tense moments. This emotional stability fosters reliability and confidence—others know they can depend on this person during crises. Instead of contributing to emotional turbulence, these individuals neutralize negativity and sustain clarity. Ultimately, emotional soft skills create resilient professionals capable of acting thoughtfully instead of impulsively.

8️⃣ Soft Skills Improve Problem-Solving and Creative Thinking -
Technical problem-solving is logical, but soft-skill-based problem-solving is intuitive and people-aware. Many workplace problems are not purely technical but social—miscommunication, unclear expectations, workflow inefficiencies, delayed responses, and interpersonal stagnation. Individuals with critical thinking, empathy, and communication skills can see problems holistically instead of mechanically. They involve the right people, gather perspectives, weigh impacts, and propose actionable solutions. Soft skills encourage curiosity rather than blame, and root-cause analysis rather than superficial conclusions. Ultimately, soft skills enhance not just how problems are solved—but how problems are perceived and understood.

9️⃣ Soft Skills Create Positive Organization Culture and Morale - 
Workplaces with strong soft-skill engagement feel collaborative rather than competitive, uplifting rather than stressful, and inclusive rather than fragmented. Employees show respect, gratitude, and recognition for each other’s effort. This improves morale, job satisfaction, and productivity. Culture determines how employees think, behave, and contribute beyond assigned duties. When people feel psychologically safe and valued, they innovate naturally—not because they must, but because they want to. Ultimately, soft skills define the emotional architecture of the company far more than corporate policies ever can.

🔟 Soft Skills Future-Proof Your Career in the Age of AI & Automation -
Technical skills can be automated — AI can code, analyze data, write reports, and process information at scale. But AI cannot replace empathy, leadership, ethics, persuasion, or emotional reasoning. Soft skills are uniquely human and cannot be digitized or outsourced. As automation accelerates, technical tasks will increasingly be delegated to machines, while humans will be valued for interpersonal, strategic, and creative abilities. Professionals who cultivate soft skills will remain irreplaceable and in demand. Ultimately, soft skills are the one domain where human ability will always surpass AI."""

# -------------------------
# UI Layout
# -------------------------
st.markdown("<div class='topbar'><div class='brand'>Intelligent Candidate Profiling & Resume Evaluation Engine</div><div class='small'>📄MADE BY AHAMAD </div></div>", unsafe_allow_html=True)
colL, colR = st.columns([0.34, 0.66])

with colL:
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("### Navigator")
    page = st.radio("", ["Dashboard", "Analyze", "Rewrite", "Job Match", "Saved", "Tools", "Skills Intelligence", "Resume Improvement Lab", "CoreMind AI"], index=1)
    st.markdown("---")
    st.markdown("#### Quick actions")
    if st.button("New Analysis"):
        page = "Analyze"
    st.markdown("---")
    st.markdown("#### Saved reports")
    st.write(len(db.all()))
    st.markdown("<small class='muted'>Keep API key secret. AI analysis optional.</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colR:
    # ----- Dashboard -----
    if page == "Dashboard":
        st.markdown('<div class="glass-card"><h3>Overview</h3><p class="muted">Summary of saved reports and recent ATS trends</p></div>', unsafe_allow_html=True)
        reports = db.all()
        total_reports = len(reports)
        avg_score = int(sum([r.get("ats", {}).get("score", 0) for r in reports]) / max(1, total_reports))
        c1, c2 = st.columns(2)
        c1.metric("Saved reports", total_reports)
        c2.metric("Avg ATS (saved)", f"{avg_score}/100")
        if reports:
            last = reports[-8:]
            scores = [r.get("ats", {}).get("score", 0) for r in last]
            fig = go.Figure(data=go.Scatter(y=scores, mode="lines+markers", line=dict(color="#7c3aed")))
            fig.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=8,b=8))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No saved reports yet.")

    # ----- Analyze -----
    if page == "Analyze":
        st.markdown('<div class="glass-card"><h3>Resume Analysis</h3><p class="muted">Upload resume, choose target role (optional), and run domain-aware ATS + optional AI analysis.</p></div>', unsafe_allow_html=True)
        colA, colB = st.columns([0.62, 0.38])
        with colA:
            uploaded = st.file_uploader("Upload resume (PDF/TXT)", type=["pdf", "txt"], key="upload_main")
            role_input = st.text_input("Target job role (optional)", placeholder="e.g., Cyber Security Engineer or AWS DevOps Engineer")
            run = st.button("Run Analysis", key="run_analysis")
            if run:
                if not uploaded:
                    st.warning("Please upload a resume file.")
                else:
                    resume_text = extract_uploaded_text(uploaded)
                    if not resume_text.strip():
                        st.error("Could not extract text from file.")
                    else:
                        with st.spinner("Computing ATS and calling AI (optional)..."):
                            ats = compute_domain_ats(resume_text, jd_text=role_input)
                            ai_text = safe_ai_analysis(resume_text, role_input) if client else "AI analysis skipped (no API key configured)."
                            # save to DB
                            name = f"report_{int(time.time())}"
                            db.insert({
                                "name": name,
                                "role": role_input,
                                "resume_text": resume_text,
                                "ai_analysis": ai_text,
                                "ats": ats,
                                "created": datetime.now().isoformat()
                            })
                        st.success("Analysis complete — saved locally.")
                        # Show gauge
                        st.markdown("<h4>ATS Match</h4>", unsafe_allow_html=True)
                        gauge_val = ats["score"]
                        fig_g = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=gauge_val,
                            number={'suffix': "%"},
                            gauge={'axis': {'range': [None, 100]},
                                   'bar': {'color': "#2dd4bf"},
                                   'steps': [{'range':[0,40],'color':"#2b2b33"},{'range':[40,70],'color':"#374151"},{'range':[70,100],'color':"#052f2f"}]}
                        ))
                        fig_g.update_layout(height=300, margin=dict(t=4,b=4,l=4,r=4), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_g, use_container_width=True)
                        # Radar with domain vs alt scores
                        st.markdown("<h4>Domain Radar (selected vs top alternatives)</h4>", unsafe_allow_html=True)
                        selected_label = ats["domain_label"]
                        alt = ats.get("alt_scores", {})
                        # pick top 5 alternative domains by score
                        sorted_alt = sorted(alt.items(), key=lambda x: x[1], reverse=True)[:5]
                        labels = [DOMAINS[k]["label"] for k,_ in sorted_alt]
                        values = [v for _,v in sorted_alt]
                        fig_r = go.Figure(data=go.Scatterpolar(r=values, theta=labels, fill='toself', line_color="#7c3aed"))
                        fig_r.update_layout(height=320, polar=dict(radialaxis=dict(range=[0,100])), paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=8,b=8))
                        st.plotly_chart(fig_r, use_container_width=True)
                        # AI analysis output
                        st.markdown("<h4>AI Analysis</h4>", unsafe_allow_html=True)
                        st.markdown(f"<div class='result-box'>{ai_text}</div>", unsafe_allow_html=True)
                        st.markdown("<h4>ATS Breakdown</h4>", unsafe_allow_html=True)
                        st.json({
                            "domain": selected_label,
                            "score": ats["score"],
                            "core_hits": ats["core_hits"],
                            "tool_hits": ats["tool_hits"],
                            "cert_hits": ats["cert_hits"],
                            "length_words": ats["length"]
                        })
                        # export links
                        html = make_html_report(name, role_input, resume_text, ai_text, ats)
                        href = html_download_link(html, f"{name}.html")
                        st.markdown(f"[Download HTML report]({href})", unsafe_allow_html=True)
                        st.download_button("Download TXT analysis", data=ai_text, file_name=f"{name}_analysis.txt")
        with colB:
            st.markdown('<div class="glass-card"><h5>Quick ATS Insight</h5><p class="muted">Paste a small resume snippet to see on-the-fly domain hits</p></div>', unsafe_allow_html=True)
            snippet = st.text_area("Resume snippet (optional)", height=260)
            if st.button("Analyze Snippet", key="snippet_btn"):
                if not snippet.strip():
                    st.warning("Paste a snippet first.")
                else:
                    s_ats = compute_domain_ats(snippet)
                    st.metric("Snippet ATS Score", f"{s_ats['score']}/100")
                    st.write("Detected domain:", s_ats["domain_label"])
                    st.write("Core hits:", s_ats["core_hits"], "Tool hits:", s_ats["tool_hits"], "Cert hits:", s_ats["cert_hits"])

    # ----- Rewrite -----
    if page == "Rewrite":
        st.markdown('<div class="glass-card"><h3>Rewrite Resume (AI)</h3><p class="muted">Optional: uses Groq if API key is set. Otherwise only the ATS scoring is available.</p></div>', unsafe_allow_html=True)
        up = st.file_uploader("Upload resume (PDF/TXT) to rewrite", type=["pdf","txt"], key="rw_up")
        target = st.text_input("Rewrite for role (optional)", key="rw_role")
        tone = st.selectbox("Tone", ["Professional", "Concise", "Enthusiastic"], index=0)
        if st.button("Rewrite Resume"):
            if not up:
                st.warning("Upload a resume first.")
            else:
                t = extract_uploaded_text(up)
                if not t.strip():
                    st.error("No text extracted.")
                else:
                    if client:
                        with st.spinner("Calling AI for rewrite..."):
                            prompt = f"Rewrite this resume to be achievement-focused, ATS-friendly, tailored to {target or 'General'}. Tone: {tone}\n\n{t}"
                            out = safe_ai_analysis(t, target or "General")
                            st.markdown("<h4>Rewritten Resume</h4>", unsafe_allow_html=True)
                            st.code(out)
                            st.download_button("Download rewritten TXT", data=out, file_name="rewritten_resume.txt")
                    else:
                        st.info("AI rewrite unavailable (GROQ_API_KEY missing).")

    # ----- Job Match -----
    if page == "Job Match":
        st.markdown('<div class="glass-card"><h3>Job Match</h3><p class="muted">Compare resume to JD and get targeted suggestions & missing keywords.</p></div>', unsafe_allow_html=True)
        up = st.file_uploader("Upload resume (PDF/TXT)", type=["pdf","txt"], key="jm_up")
        jd = st.text_area("Paste Job Description", height=260, key="jm_jd")
        if st.button("Compute Match"):
            if not up:
                st.warning("Upload resume first.")
            elif not jd.strip():
                st.warning("Paste the job description.")
            else:
                rtext = extract_uploaded_text(up)
                ats = compute_domain_ats(rtext, jd)
                st.metric("Match Score (domain-aware)", f"{ats['score']}/100")
                st.write("Detected domain:", ats["domain_label"])
                jd_tokens = set(tokenize(jd))
                resume_tokens = set(tokenize(rtext))
                missing = sorted(list(jd_tokens - resume_tokens))[:40]
                st.write("Top missing keywords:", ", ".join(missing) if missing else "None")
                if client:
                    with st.spinner("Generating AI suggestions..."):
                        ai_suggestions = safe_ai_analysis(rtext, jd)
                    st.markdown("<h4>AI Suggestions</h4>", unsafe_allow_html=True)
                    st.markdown(f"<div class='result-box'>{ai_suggestions}</div>", unsafe_allow_html=True)

    # ----- Saved -----
    if page == "Saved":
        st.markdown('<div class="glass-card"><h3>Saved Reports</h3></div>', unsafe_allow_html=True)
        rows = db.all()
        if not rows:
            st.info("No saved reports yet.")
        else:
            df = pd.DataFrame(rows)
            st.dataframe(df[["name", "role", "created"]].rename(columns={"name":"Report","role":"Role","created":"Saved At"}))
            sel = st.selectbox("Pick a report", options=[r.doc_id for r in rows], format_func=lambda did: db.get(doc_id=did)["name"])
            if sel:
                r = db.get(doc_id=sel)
                st.markdown(f"### {r['name']} — {r.get('role','')}")
                st.markdown(f"<div class='result-box'>{r.get('ai_analysis','')}</div>", unsafe_allow_html=True)
                if st.button("Export HTML"):
                    html = make_html_report(r['name'], r.get("role",""), r.get("resume_text",""), r.get("ai_analysis",""), r.get("ats",{}))
                    href = html_download_link(html, f"{r['name']}.html")
                    st.markdown(f"[Download HTML]({href})", unsafe_allow_html=True)
                if st.button("Delete Report"):
                    db.remove(doc_ids=[sel])
                    st.experimental_rerun()

    # ----- Tools -----
    if page == "Tools":
        st.markdown('<div class="glass-card"><h3>Tools</h3></div>', unsafe_allow_html=True)
        st.subheader("LinkedIn About Generator (AI)")
        name = st.text_input("Full name", key="li_name")
        skills = st.text_input("Top skills (comma-separated)", key="li_skills")
        industry = st.text_input("Target industry / role", key="li_ind")
        if st.button("Generate LinkedIn About"):
            persona = f"{name} — {industry}. Skills: {skills}"
            if client:
                out = safe_ai_analysis(persona, industry)
                st.write(out)
                st.download_button("Download bio", data=out, file_name="linkedin_bio.txt")
            else:
                st.info("AI not configured. Provide GROQ_API_KEY to enable.")

            # ---------------------------------------------------
            # 🚀 ADD THIS BLOCK HERE
            # ---------------------------------------------------
        st.markdown("---")
        st.subheader("Project Idea Finder")

        domain_query = st.text_input("Enter domain / job role")

        if st.button("Get Project Ideas"):
            domain, projects = get_projects_for_domain(domain_query)
            if not projects:
                st.warning("No matching domain found.")
            else:
                st.success(f"Projects for: {domain}")
                for p in projects:
                    st.write(f"### {p['title']}")
                    st.write(p['desc'])
                    st.markdown("---")

    if page == "Skills Intelligence":
        st.markdown(
            '<div class="glass-card"><h3>Skills Intelligence</h3><p class="muted">Find the most important skills required for various job domains</p></div>',
            unsafe_allow_html=True)

        from skills_lookup import get_skills_for_domain

        skill_query = st.text_input("Enter domain or job role")

        if st.button("Get Skills"):
            domain, skills = get_skills_for_domain(skill_query)
            if not skills:
                st.warning("No matching domain found.")
            else:
                st.success(f"Skills for: {domain}")
                for s in skills:
                    st.write(f"### 🧠 {s['skill']}")
                    st.write(s['description'])
                    st.markdown("---")

        st.markdown("## 🎯 Soft Skills Mastery — Must for Every Career")
        st.write(SOFT_SKILLS_DESCRIPTION)

        st.markdown("## 🎥 Soft Skills Training Videos & Communication Guides")
        render_soft_skills_videos()

    # ----- Resume Guide -----
    if page == "Resume Improvement Lab":
        st.markdown(
            '<div class="glass-card"><h3>Resume Guide</h3><p class="muted">Get ideal resume structure & section descriptions for your role</p></div>',
            unsafe_allow_html=True)

        from resume_guide import get_resume_guide_for_domain

        q = st.text_input("Enter your job role / domain", placeholder="Example: AWS, Cyber, frontend, ML")

        if st.button("Get Resume Guide"):
            domain, info = get_resume_guide_for_domain(q)
            if not domain:
                st.error("No matching domain found.")
            else:
                st.success(f"Found domain: {domain}")
                for section, bullets in info.items():
                    st.write(f"## 📌 {section}")

                    # If bullets is a dict → get bullets["description"]
                    if isinstance(bullets, dict) and "description" in bullets:
                        bullets = bullets["description"]

                    for b in bullets:
                        st.write(f"- {b}")
                    st.markdown("---")

        # NOW ADD THIS
        from resume_videos import render_resume_videos
        render_resume_videos()

    # ----- Chatbot -----
    if page == "CoreMind AI":
        st.markdown(
            '<div class="glass-card"><h3>AI Chatbot</h3><p class="muted">Ask anything — resume, career, AI, projects, interview, and more</p></div>',
            unsafe_allow_html=True)

        if client is None:
            st.error("GROQ API not configured — Chatbot unavailable.")
        else:
            # Initialize session chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Text input
            user_msg = st.text_input("Ask anything…", key="chat_input")

            # Send
            if st.button("Send"):
                if user_msg.strip():
                    # Save user msg
                    st.session_state.chat_history.append(("user", user_msg))

                    with st.spinner("Thinking..."):
                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system",
                                       "content": "You are an intelligent AI assistant. Give helpful, accurate answers. When asked for N items, always provide ALL N items completely, never shorten the list."}]
                                     + [{"role": role, "content": msg} for role, msg in st.session_state.chat_history],
                            temperature=0.4,
                            max_completion_tokens=3000,
                            stream=False
                        )
                        reply = resp.choices[0].message.content

                    # Append bot reply
                    st.session_state.chat_history.append(("assistant", reply))
                else:
                    st.warning("Please type something.")

            st.markdown("""
            <style>
            .chat-bubble-user {
                background: linear-gradient(90deg, #2dd4bf22, #7c3aed22);
                padding: 12px 14px;
                border-radius: 12px;
                margin: 8px 0;
                text-align: right;
                border: 1px solid rgba(255,255,255,0.06);
            }

            .chat-bubble-ai {
                background: rgba(255,255,255,0.05);
                padding: 12px 14px;
                border-radius: 12px;
                margin: 8px 0;
                border-left: 3px solid #7c3aed;
                text-align: left;
                color: #e6eef8;
            }

            .chat-avatar {
                font-size: 20px;
                margin: 4px;
                vertical-align: middle;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("### 💬 Conversation")

            for role, msg in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f"<div class='chat-bubble-user'><span class='chat-avatar'>🧑</span> {msg}</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-bubble-ai'><span class='chat-avatar'>🤖</span> {msg}</div>",
                                unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2025 AI Resume Studio BY AHAMAD</div>", unsafe_allow_html=True)
