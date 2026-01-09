import streamlit as st
import re
import requests


SOFT_SKILLS_VIDEO_LINKS = [
    ("Simplilearn", "Top 5 Tips to Improve Communication Skills | Soft Skills For Beginners | Simplilearn",
     "https://youtu.be/pJ7RgUCEd5M"),
    ("TutorialsPoint", "Soft Skills (Playlist)",
     "https://youtube.com/playlist?list=PLWPirh4EWFpFIElSxplDlEhRDZHkBD-0n"),
    ("Engineers ki Pathshala by Umesh Dhande", "Communication & Soft Skills LIVE Classes By Disha Mam (Playlist)",
     "https://youtube.com/playlist?list=PL9RcWoqXmzaLt7FMmdDK8SoM5X63cPytf"),
    ("Sandeep Maheshwari", "How to improve Communication Skills? By Sandeep Maheshwari | Hindi",
     "https://youtu.be/hE6I9apUvrk"),
    ("Simerjeet Singh", "Soft Skills & Communication Development (Playlist)",
     "https://youtube.com/playlist?list=PLOaeOd121eBEEWP14TYgSnFsvaTIjPD22"),
    ("warikoo", "Top 30 Soft Skills for a Better Career in 2021!",
     "https://youtu.be/0gUgm4zB2F4"),
    ("Vinh Giang", "30 Day Plan to Master Communication + FREE Workbook",
     "https://youtu.be/U40qvUiefQo"),
    ("DigiSkills 2.0", "English Communication & Soft Skills Urdu/Hindi (Playlist)",
     "https://youtube.com/playlist?list=PLl68ArKrFfmeejVb-zD4CHQU5cDKdWZ1j"),
    ("Communication Coach Alexander Lyon", "What Are Soft Skills? Top 8",
     "https://youtu.be/hZSARM4VaVs"),
    ("Communication Coach Alexander Lyon", "How to Speak Clearly and Confidently (Playlist)",
     "https://youtube.com/playlist?list=PLiObSxAItudKyvecnL7MduYeSzjgbQuwU")
]


# 🔥 check whether thumbnail exists
def check_image_exists(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except:
        return False


# 🔥 improved thumbnail logic
def get_thumbnail(url):

    # 1️⃣ normal YouTube video
    match = re.search(r"(?:v=|be/)([^?&]+)", url)
    if match:
        id = match.group(1)

        # Try maxres — may be blocked
        maxres = f"https://img.youtube.com/vi/{id}/maxresdefault.jpg"
        if check_image_exists(maxres):
            return maxres

        # Try standard resolution
        hq = f"https://img.youtube.com/vi/{id}/hqdefault.jpg"
        if check_image_exists(hq):
            return hq

        # Try medium resolution
        mq = f"https://img.youtube.com/vi/{id}/mqdefault.jpg"
        if check_image_exists(mq):
            return mq

        # Try fallback from webp
        fallback = f"https://i.ytimg.com/vi_webp/{id}/maxresdefault.webp"
        return fallback

    # 2️⃣ playlist — get via YouTube oEmbed (Best!)
    if "list=" in url:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        try:
            data = requests.get(oembed_url).json()
            return data.get("thumbnail_url", "https://i.imgur.com/n9z3sLg.jpeg")
        except:
            return "https://i.imgur.com/n9z3sLg.jpeg"

    return "https://i.imgur.com/n9z3sLg.jpeg"


# UI Render
def render_soft_skills_videos():
    st.markdown(
        """
        <style>
            .video-block {
                margin-bottom: 25px;
                padding: 10px;
                background: rgba(255, 200, 30, 0.08);
                border-radius: 12px;
                box-shadow: 0px 0px 18px rgba(255, 200, 30, 0.35);
                transition: transform 0.25s ease, box-shadow 0.25s ease;
                width: 78%;
            }
            .video-block:hover {
                transform: scale(1.015);
                box-shadow: 0px 0px 28px rgba(255, 200, 30, 0.55);
            }
            .video-thumb {
                border-radius: 10px;
                width: 100%;
                height: auto;
                object-fit: cover;
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
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🎥 Top Soft Skills & Communication Development Resources")

    for channel, title, url in SOFT_SKILLS_VIDEO_LINKS:
        thumb = get_thumbnail(url)

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
