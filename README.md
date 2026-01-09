🧠 Intelligent Candidate Profiling & Resume Evaluation Engine

An AI-powered resume analysis and career intelligence platform built using Streamlit that helps candidates analyze, optimize, match, and improve resumes using ATS logic, skill intelligence, and AI-assisted tools — all in a single unified dashboard.

🚀 Designed as a mini project with real-world relevance, production-grade UI, and modular backend architecture.

📌 Project Overview

The Intelligent Candidate Profiling & Resume Evaluation Engine is a comprehensive career-support system that enables users to:

Analyze resumes for ATS compatibility

Rewrite resumes using AI-based enhancements

Match resumes against job descriptions

Generate LinkedIn “About” sections

Discover domain-specific skills

Track saved analysis reports

Access a built-in AI career chatbot

The application is built on Streamlit, ensuring fast iteration, clean UI, and session-based interactivity.

🎯 Key Objectives

Help candidates beat Applicant Tracking Systems (ATS)

Provide data-driven resume insights

Assist freshers and professionals with career guidance

Demonstrate full-stack Streamlit app development

Showcase modular Python architecture

🖥️ Application Modules & Features
1️⃣ Dashboard (Overview)

Displays:

Total saved resume reports

Average ATS score

Visual trend chart of past ATS scores

Acts as a central analytics hub

2️⃣ Resume Analysis

📄 Upload resume (PDF / TXT) and optionally specify a target role.

Features:

ATS keyword scoring

Domain-aware analysis

Resume snippet quick check

Role-based insights (e.g., Cyber Security, AWS DevOps)

3️⃣ Resume Rewrite (AI)

✍️ AI-assisted resume rewriting module.

Capabilities:

Rewrite resume for a specific role

Professional tone optimization

ATS-friendly formatting

Optional AI usage (API-based if enabled)

4️⃣ Job Match Engine

🔍 Compare resume against a Job Description (JD).

Outputs:

Resume–JD match percentage

Missing keywords

Improvement suggestions

Skill gap identification

5️⃣ Saved Reports

📊 Persistent storage of resume analyses.

Details stored:

Report ID

Target role

Timestamp

ATS score

Enables progress tracking over time.

6️⃣ Tools Section

🛠️ Productivity and branding tools.

🔹 LinkedIn About Generator

Generates professional LinkedIn summaries

Inputs:

Full name

Top skills

Target industry / role

7️⃣ Skills Intelligence

🧩 Domain-based skill discovery system.

Use cases:

Identify must-have skills for a job role

Explore trending technical + soft skills

Career planning support

8️⃣ Resume Improvement Lab

📘 Guided resume-building assistance.

Includes:

Ideal resume structure

Section-by-section explanations

Domain-specific resume templates

External curated resume resources

9️⃣ CoreMind AI (Chatbot)

🤖 Built-in AI assistant for:

Resume questions

Career advice

Interview prep

AI & project guidance

🗂️ Project Structure
beginner_ai_project2_a/
│
├── project2/
│   ├── main.py
│   ├── project_lookup.py
│   ├── resume_guide.py
│   ├── resume_videos.py
│   ├── soft_skills_videos.py
│   ├── skills_lookup.py
│   ├── skills.json
│   ├── domains.json
│   ├── domains_cache.json
│   ├── resume_guide_dataset.json
│   ├── resume_reports.json
│   ├── README.md
│   ├── pyproject.toml
│   ├── .env
│   └── uv.lock
│
├── .venv/
└── .gitignore

⚙️ Core Technical Highlights
🔹 Streamlit Widget Policy Enforcement (main.py)

Your main.py contains advanced Streamlit internal policy handling, including:

✅ Widget callback validation

✅ Session state write protection

✅ Cached function widget misuse detection

✅ Fragment path enforcement

✅ Accessibility warnings for labels

This ensures:

Predictable reruns

Clean session state

Safe caching behavior

Production-grade widget usage

📌 This goes beyond beginner Streamlit usage and demonstrates deep framework understanding.

🧠 Technologies Used

Python 3.10+

Streamlit

JSON-based datasets

Session State Management

Modular Python Architecture

Optional AI API integration

Dark-mode optimized UI

🚀 How to Run the Project
1️⃣ Clone the Repository
git clone <your-repo-url>
cd beginner_ai_project2_a

2️⃣ Create Virtual Environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Streamlit App
streamlit run project2/main.py

📈 Use Cases

🎓 Final-year students

👨‍💼 Job seekers

🧑‍💻 Career switchers

🏫 Academic mini-project submission

📊 Resume optimization practice

🏆 Project Strengths

✔ Real-world problem solving
✔ Professional UI/UX
✔ Modular and scalable backend
✔ Advanced Streamlit usage
✔ Resume + career intelligence combined
✔ Ideal for mini project / internship evaluation

🔮 Future Enhancements

AI interview question generator

Resume PDF export

Multi-language resume support

Recruiter dashboard

User authentication & profiles

👨‍💻 Author

Made by Ahamad

Passionate about AI, career tech, and intelligent systems.

📜 License
This project is licensed under the MIT License.