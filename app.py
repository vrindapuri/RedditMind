import os
import json
import requests
import streamlit as st
from PIL import Image
from src.reddit_scraper import scrape_user_data, extract_username_from_url
from src.persona_builder import extract_persona
from src.visual_persona_generator import generate_visual_card

# Config
st.set_page_config(
    page_title="REDDITMIND",
    page_icon="🧠",
    layout="centered"
)

st.markdown(
    """
    <style>
        .main {
            background: #f6f8fa;
        }
        .title {
            font-size: 3em;
            font-weight: bold;
            color: #FF4500;
        }
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 20px;
            color: #FFFFFF;
        }
        .css-1q8dd3e {
            padding: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>REDDITMIND</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Decode digital identities — one Redditor at a time!</div>", unsafe_allow_html=True)

# Input
reddit_input = st.text_input("Please enter Reddit username or profile URL:", "")

if reddit_input:
    with st.spinner("Okay...Scraping Reddit data..."):
        username = extract_username_from_url(reddit_input)
        data = scrape_user_data(username)

    if not data["posts"] and not data["comments"]:
        st.error("Oops! No data found for this user.")
        st.stop()

    # Download profile image
    profile_pic_url = data.get("icon_img")
    profile_pic_path = None
    if profile_pic_url:
        profile_pic_path = f"data/{username}_profile.jpg"
        try:
            os.makedirs("data", exist_ok=True)
            img_data = requests.get(profile_pic_url).content
            with open(profile_pic_path, "wb") as f:
                f.write(img_data)
        except:
            profile_pic_path = None

    # Text truncation
    def clean_text(data, max_chars=16000):
        combined = ""
        for post in data["posts"]:
            text = f"\n[POST]\nTitle: {post['title']}\nBody: {post['body']}\nURL: {post['url']}\n"
            if len(combined + text) > max_chars:
                break
            combined += text
        for comment in data["comments"]:
            text = f"\n[COMMENT]\nBody: {comment['body']}\nURL: {comment['url']}\n"
            if len(combined + text) > max_chars:
                break
            combined += text
        return combined

    combined_text = clean_text(data)

    with st.spinner("Thinking... Generating Persona using Groq..."):
        try:
            persona = extract_persona(combined_text, username)

            # Save JSON
            json_path = f"data/{username}_persona.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(persona, f, indent=2)

            # Generate visual card
            output_image_path = f"data/{username}_persona_visual.png"
            generate_visual_card(
                username=username,
                persona_json_path=json_path,
                output_image_path=output_image_path,
                profile_pic_path=profile_pic_path
            )

            st.success("Wohoo! Persona generated successfully!")

            # Show Image
            st.image(output_image_path, use_container_width=True)

            # Download options
            with open(output_image_path, "rb") as img_file:
                st.download_button("Download Persona Visual", img_file, f"{username}_persona.png")

            with open(json_path, "r", encoding="utf-8") as json_file:
                st.download_button("Download Persona JSON", json_file, f"{username}_persona.json")

        except Exception as e:
            st.error(f"Sorry! Failed to generate persona: {e}")
