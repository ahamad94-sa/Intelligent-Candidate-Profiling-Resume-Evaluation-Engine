import streamlit as st
import re

RESUME_VIDEO_LINKS = [
    ("Apna College", "How to make Ultimate Resume ? Step by step guide for Software Engineers",
     "https://youtu.be/y3R9e2L8I9E?si=MlfJzRWO0_ZYe3r-"),
    ("EZSNIPPET (Neeraj Walia)", "My Resume | EZSNIPPET | Neeraj Walia",
     "https://youtu.be/SHT0y9Gq_rk?si=HF-976_i7sAN_YtC"),
    ("Shweta Arora", "Freshers Resume Template: What to Write in Resume with NO Experience.",
     "https://youtu.be/G2_0kqrwAAw?si=UdbanMvbKAuZ1ifa"),
    ("ResumeSector", "How to Make Resume in Microsoft Word | Resume for Job Application",
     "https://youtu.be/3JIvPEgc8oQ?si=44lqZxe4TSiP1cx5"),
    ("Utkarshhh", "How to make a resume for freshers | Canva Resume",
     "https://youtu.be/ZwP7kv0zHiY?si=dp-Yzx6dedhDu8-_"),
    ("Apna College", "Why my Resume got selected in Google / Microsoft / Amazon",
     "https://youtu.be/KZehm-meGMg?si=ZZIQl-dI03TbW3S0"),
    ("GenieAshwani", "Best RESUME to Get JOB - Complete Guide & ATS Resume Format",
     "https://youtu.be/NooFfEDWIEw?si=Pck9HE4xYkVlxfjO"),
    ("AshishPS", "My Resume That Got Selected at GOOGLE, AMAZON, MICROSOFT & META",
     "https://youtu.be/qhocVNbvNHs?si=1RA3t9ufDSL4Mk6e"),
    ("JeffSu", "Write an Incredible Resume: 5 Golden Rules!",
     "https://youtu.be/Tt08KmFfIYQ?si=-pCV9JAixEkUQxwl"),
    ("Jeremy Tutorials", "How to Make a Google Docs Professional Resume in 5 Minutes!",
     "https://youtu.be/qPPuW013F-A?si=96HFF0lCXaJm51Uk")
]

def extract_video_id(url: str):
    match = re.search(r"(?:v=|be/)([^?&]+)", url)
    return match.group(1) if match else None

def render_resume_videos():
    st.markdown(
        """
        <style>
            .video-block {
                margin-bottom: 26px;
                padding: 10px;
                background: rgba(0, 122, 255, 0.08);
                border-radius: 12px;
                box-shadow: 0px 0px 18px rgba(0, 200, 255, 0.35);
                transition: transform 0.25s ease, box-shadow 0.25s ease;
                width: 78%;
            }
            .video-block:hover {
                transform: scale(1.015);
                box-shadow: 0px 0px 28px rgba(78, 201, 255, 0.55);
            }
            .video-thumb {
                border-radius: 10px;
                width: 100%;
            }
            .channel-name {
                font-size: 17px;
                font-weight: 650;
                color: #f3f4f6;
                margin-top: 8px;
            }
            .video-title {
                font-size: 15px;
                color: #cdd5e0;
                margin-bottom: 4px;
            }
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown("### 🎥 Top Resume Building Resources")

    for channel, title, url in RESUME_VIDEO_LINKS:
        video_id = extract_video_id(url)
        thumb = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        st.markdown(
            f"""
            <a href="{url}" target="_blank" style="text-decoration:none;">
                <div class="video-block">
                    <img src="{thumb}" class="video-thumb">
                    <div class="channel-name">{channel}</div>
                    <div class="video-title">{title}</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
