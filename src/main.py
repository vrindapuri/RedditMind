import os
import json
import requests
from reddit_scraper import scrape_user_data, extract_username_from_url
from persona_builder import extract_persona
from visual_persona_generator import generate_visual_card

def clean_text(data, max_chars=16000):  # ~6000 tokens max
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

    print(f"[INFO] Total characters used for prompt: {len(combined)}")
    return combined

if __name__ == "__main__":
    reddit_input = input("Enter Reddit profile URL or username: ").strip()
    username = extract_username_from_url(reddit_input)

    print(f"\n[DEBUG] Scraping Reddit data for: {username} ...")
    data = scrape_user_data(username)

    if not data["posts"] and not data["comments"]:
        print("[ERROR] No data scraped. Exiting.")
        exit()

    # Download profile picture
    profile_pic_url = data.get("icon_img")
    profile_pic_path = None
    if profile_pic_url:
        try:
            os.makedirs("data", exist_ok=True)
            profile_pic_path = f"data/{username}_profile.jpg"
            img_data = requests.get(profile_pic_url).content
            with open(profile_pic_path, "wb") as f:
                f.write(img_data)
            print("[INFO] Profile image saved.")
        except Exception as e:
            print(f"[WARNING] Couldn't download profile image: {e}")

    # Truncate text if needed
    combined_text = clean_text(data, max_chars=16000)

    # Save the cleaned prompt text for transparency
    text_path = f"data/{username}_raw_prompt.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(combined_text)
    print(f"[INFO] Prompt text saved to {text_path}")


    print("\n[INFO] Generating user persona using Groq...")
    try:
        persona_dict = extract_persona(combined_text, username)

        # Save JSON
        os.makedirs("data", exist_ok=True)
        json_path = f"data/{username}_persona.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(persona_dict, f, indent=2)
        print(f"[INFO] Persona JSON saved to {json_path}")

        # Visual
        image_path = f"data/{username}_persona_visual.png"
        generate_visual_card(
            username=username,
            persona_json_path=json_path,
            output_image_path=image_path,
            profile_pic_path=profile_pic_path
        )

    except Exception as e:
        print(f"[ERROR] Failed to generate persona: {e}")
