import os
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

# Helper to draw bar chart
def draw_bar_chart(data_dict, title, output_path):
    keys = list(data_dict.keys())
    values = list(data_dict.values())

    plt.figure(figsize=(4, 2.5))
    plt.barh(keys, values, color="#00FF11")
    plt.title(title)
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path

# Main function: Generate visual card with profile picture
def generate_visual_card(username, persona_json_path, output_image_path, profile_pic_path=None):
    with open(persona_json_path, "r", encoding="utf-8") as f:
        persona = json.load(f)

    W, H = 1200, 800
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 36)
        subhead_font = ImageFont.truetype("arialbd.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subhead_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Header
    draw.text((40, 30), f"{username}'s Persona", fill="#00D0FF", font=title_font)
    draw.text((40, 80), f"Location: {persona.get('location', 'N/A')}", fill="black", font=subhead_font)
    draw.text((40, 110), f"Archetype: {persona.get('archetype', 'N/A')}", fill="black", font=subhead_font)

    # Profile pic if available
    if profile_pic_path and os.path.exists(profile_pic_path):
        try:
            pfp = Image.open(profile_pic_path).resize((120, 120)).convert("RGB")
            img.paste(pfp, (1020, 30))  # top-right corner
        except Exception as e:
            print(f"[WARNING] Couldn't render profile image: {e}")

    # Quote
    draw.text((420, 160), f"\"{persona.get('quote', '')}\"", fill="gray", font=subhead_font)

    # Charts
    os.makedirs("output", exist_ok=True)
    chart1_path = draw_bar_chart(persona.get("motivations", {}), "Motivations", "output/motivations.png")
    chart2_path = draw_bar_chart(persona.get("personality", {}), "Personality", "output/personality.png")

    img.paste(Image.open(chart1_path).resize((350, 200)), (40, 160))
    img.paste(Image.open(chart2_path).resize((350, 200)), (40, 390))

    # Behaviors, Goals, Frustrations
    y = 240
    x = 420
    for section, items in {
        "Behaviors": persona.get("behaviors", []),
        "Goals": persona.get("goals", []),
        "Frustrations": persona.get("frustrations", [])
    }.items():
        draw.text((x, y), section, fill="black", font=subhead_font)
        y += 30
        for item in items:
            draw.text((x + 10, y), f"- {item}", fill="black", font=text_font)
            y += 25
        y += 15

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    img.save(output_image_path)
    print(f"[✅] Persona visual saved to {output_image_path}")
