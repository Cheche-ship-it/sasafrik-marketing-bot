# main.py
import os
import json
import random
import time
import mimetypes
import urllib.parse
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session, OAuth1
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env
load_dotenv()

# --- Configuration & Credentials ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROCESSED_FILE = os.getenv("PROCESSED_TOPICS_FILE", "processed_topics.json")
SETTINGS_FILE = os.getenv("POST_SETTINGS_FILE", "post_settings.json")

# BRANDING ASSET CONFIGURATION 
LOGO_ASSET_PATH = "logo.png" 

# FLUX Free Open-Source Cluster Router Matrix
FLUX_BASE_URL = os.getenv("FLUX_BASE_URL", "https://image.pollinations.ai/p/")

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "YOUR_FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "YOUR_FACEBOOK_ACCESS_TOKEN")

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "YOUR_TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "YOUR_TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "YOUR_TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "YOUR_TWITTER_ACCESS_TOKEN_SECRET")

# Predefined high-conversion local corporate marketing topics
TOPICS = [
    "Write a post targeting African enterprise CEOs explaining how SasAfrik's custom Software Engineering turns basic web portals into highly lucrative transactional sales engines.",
    "Draft a strategic corporate profile comparing slow, error-prone manual workflows vs. a streamlined, high-scale SasAfrik Automated Enterprise Ecosystem.",
    "Create a visionary Cloud Platform Engineering brief focused on Nairobi financial enterprise continuity and zero-downtime microservices.",
    "Write about high-yield Systems Integration bridging real-time M-Pesa B2B channels, custom accounting platforms, and local warehouse inventory layers.",
    "Draft an engineering spotlight on SasAfrik Mobile App Development, detailing resilient offline-first syncing architectures across rural Kenya and East Africa.",
    "Write a direct note to corporate founders explaining why business growth requires meticulous User Experience (UX) Architecture over clunky, chaotic feature dumping.",
    "Create an enterprise alert regarding modern System Security: protecting corporate databases in line with the Kenya Data Protection Act using robust cryptographic integrations.",
    "Draft an executive feature celebrating 'The Vanguard of African Tech'—how SasAfrik designs world-class cloud infrastructure right here in Nairobi for the global stage."
]

# Initialize Gemini Model Safely
model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Error initializing Gemini: {e}")

# --- Core Settings & Storage Utilities ---
def load_settings():
    default = {"restart": True}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return default
    except Exception:
        return default

def load_processed_topics():
    try:
        if os.path.exists(PROCESSED_FILE):
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception:
        return []

def save_processed_topics(topics_list):
    try:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(topics_list), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error preserving process states: {e}")

def add_processed_topic(topic):
    topics = load_processed_topics()
    if topic not in topics:
        topics.append(topic)
        save_processed_topics(topics)

def clear_processed_topics():
    save_processed_topics([])

# --- Graphics Design Prompt Engineering Studio ---
def generate_flux_masterpiece_prompt(topic):
    """
    Acts as an elite Art Director enforcing pure human photorealism.
    Strips away artificial sci-fi tropes to generate highly credible corporate lifestyle imagery.
    """
    if not model:
        return f"Candid commercial photography of professional tech workspace in Nairobi, natural daylight, real people, 4k. {topic[:50]}"

    prompt_builder = f"""
You are an elite Senior Art Director and Corporate Brand Strategist for SasAfrik, a premier enterprise software technology company in Nairobi, Kenya.

Your task is to transform the following raw marketing TOPIC into ONE incredibly detailed, hyper-realistic, human-centric image generation prompt (max 45 words) tailored for FLUX.1 Schnell.

TOPIC: "{topic}"

Strict Authenticity and Realism Rules:
- Visual Style: True candid commercial photography. It must look like a real photograph featuring actual human beings, not a 3D digital concept illustration.
- Scene Staging: Show professional, confident African corporate executives, software engineers, or founders actively collaborating in a sleek modern Nairobi tech office environment (e.g., Westlands window views).
- Focus on Realism: Specify crisp organic textures, real human hands holding a tablet or stylus, natural expressions, authentic clothing fabrics, and elegant depth of field. 
- Lighting: Beautiful warm corporate morning daylight, soft office ambient reflections, realistic shadows. Neutral, professional color grading.
- Absolute Prohibitions: NO glowing neon tracks, NO floating holographic screens, NO abstract cyberpunk geometric grids, and NO generic artificial sci-fi artifacts. 
- Exclusions: Never include references to text, badges, borders, or watermarked logo placement in the prompt.

Output ONLY the final prompt string. No chat or introductory text.
"""
    try:
        response = model.generate_content(prompt_builder)
        if response and response.text:
            return response.text.strip()
        return topic[:100]
    except Exception as e:
        print(f"Error generating visual prompt context: {e}")
        return topic[:100]

# --- Free Network Asset Transmit Engine ---
def call_flux_api_and_save(flux_prompt, filename="temp_flux_raw.jpg"):
    safe_prompt = urllib.parse.quote(flux_prompt)
    target_url = f"{FLUX_BASE_URL}{safe_prompt}?width=1024&height=1024&model=flux&seed={random.randint(1, 9999999)}"
    
    try:
        print("Contacting free open-source image generation pipeline cluster...")
        response = requests.get(target_url, timeout=45)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        print(f"API cluster issued incorrect server response status: {response.status_code}")
        return None
    except Exception as e:
        print(f"Exception encountered during asset streaming: {e}")
        return None

# --- Programmatic Branding Compositing Engine ---
def composite_masterpiece(base_image_path, logo_path=LOGO_ASSET_PATH, output_filename="masterpiece_final.jpg"):
    """
    Assembles premium corporate layouts. Incorporates an alpha-glass panel overlay
    and beautifully scales the centered corporate footer across the base landscape width.
    """
    print("Initiating expert graphic design canvas layout generation...")
    try:
        # 1. Load Background Canvas
        base = Image.open(base_image_path).convert("RGBA")
        base_w, base_h = base.size

        # Create overlay channel layer
        overlay_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay_layer)

        # Baseline vertical offset tracker to ensure no overlapping can happen
        logo_bottom_y = int(base_h * 0.05) 

        # 2. Overlay Logo Layer with Balanced Margins
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo_w, logo_h = logo.size
            
            target_w = int(base_w * 0.24)
            target_h = int(logo_h * (target_w / logo_w))
            logo_scaled = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            margin_offset = int(base_w * 0.05)
            base.alpha_composite(logo_scaled, (margin_offset, margin_offset))
            
            logo_bottom_y = margin_offset + target_h
            print("Successfully composited company brand logo asset layer.")
        else:
            print(f"Warning: Expected logo file missing at '{logo_path}'. Using dynamic fallback positioning bounds.")
            logo_bottom_y = int(base_h * 0.12)

        # 3. Dynamic Font Configuration Matrix
        try:
            font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.026))
            font_body = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.021))
            font_footer = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.020))
        except Exception:
            try:
                font_title = ImageFont.truetype("arial.ttf", int(base_h * 0.026))
                font_body = ImageFont.truetype("arial.ttf", int(base_h * 0.021))
                font_footer = ImageFont.truetype("arial.ttf", int(base_h * 0.020))
            except Exception:
                font_title = font_body = font_footer = ImageFont.load_default()

        # 4. Capability Panel Layout Setup ("WE DESIGN & DEVELOP")
        header_text = "WE DESIGN & DEVELOP"
        capabilities = [
            "• Web Platforms & Portals",
            "• Enterprise API Integrations",
            "• High-Scale Mobile Apps",
            "• Full-Stack Applications",
            "• Workflow Automation Engines",
            "• Custom AI Conversational Bots"
        ]
        
        # High-End Contact Layout definitions
        footer_line1 = "📞 Call / WhatsApp: +254 720 000 803"
        footer_line2 = "🌐 sasafrik.com  |  ✉️ hello@sasafrik.com"

        # Structural bounding box dimensions setup
        card_w = int(base_w * 0.50)
        card_h = int(base_h * 0.44)
        card_x1 = int(base_w * 0.05)
        card_y1 = logo_bottom_y + int(base_h * 0.03)
        
        text_padding_left = int(card_w * 0.06)

        # Apply premium frosted glass panel backdrop container
        draw_overlay.rounded_rectangle(
            [card_x1, card_y1, card_x1 + card_w, card_y1 + card_h],
            radius=16,
            fill=(10, 15, 30, 180),       # Deep corporate premium navy tint
            outline=(255, 255, 255, 45),  # Clean micro white reflection accent line
            width=2
        )

        # VISIBILITY FIX: Elite 4-Way Omni-Directional Deep Shield Drop Shadows
        def draw_high_contrast_text(draw_obj, position, text_str, text_color, font_obj, shadow_color=(0, 0, 0, 255)):
            x, y = position
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -2), (0, 2), (-2, 0), (2, 0)]:
                draw_obj.text((x + dx, y + dy), text_str, fill=shadow_color, font=font_obj)
            draw_obj.text((x, y), text_str, fill=text_color, font=font_obj)

        # Print Core "WE DESIGN & DEVELOP" Section Heading
        draw_high_contrast_text(
            draw_overlay,
            (card_x1 + text_padding_left, card_y1 + int(card_h * 0.08)), 
            header_text, 
            text_color=(56, 189, 248, 255),  # Sky blue tech accent
            font_obj=font_title
        )

        # Print Capabilities List
        y_cursor = card_y1 + int(card_h * 0.22)
        spacing_offset = int(card_h * 0.11)
        
        for item in capabilities:
            draw_high_contrast_text(
                draw_overlay,
                (card_x1 + text_padding_left, y_cursor), 
                item, 
                text_color=(255, 255, 255, 255), 
                font_obj=font_body
            )
            y_cursor += spacing_offset

        # 5. Position Centered Horizontal Bottom Corporate Contact Banner
        banner_w = int(base_w * 0.74)  
        banner_h = int(base_h * 0.095) 
        banner_x1 = int((base_w - banner_w) / 2)
        banner_y1 = int(base_h - banner_h - int(base_h * 0.04))

        # VISIBILITY FIX: Elevated opacity layer + stark border to make contact area clear
        draw_overlay.rounded_rectangle(
            [banner_x1, banner_y1, banner_x1 + banner_w, banner_y1 + banner_h],
            radius=12,
            fill=(10, 15, 30, 245),       
            outline=(56, 189, 248, 120),  # Sky blue ambient glow link border
            width=2
        )

        def get_text_w(text_str, font_obj):
            try:
                bbox = draw_overlay.textbbox((0, 0), text_str, font=font_obj)
                return bbox[2] - bbox[0]
            except AttributeError:
                return draw_overlay.textsize(text_str, font=font_obj)[0] if hasattr(draw_overlay, 'textsize') else int(banner_w * 0.8)

        w_f1 = get_text_w(footer_line1, font_footer)
        w_f2 = get_text_w(footer_line2, font_footer)

        # Centered text layouts across the full bar bounds now that QR code is removed
        draw_high_contrast_text(
            draw_overlay,
            (banner_x1 + int((banner_w - w_f1) / 2), banner_y1 + int(banner_h * 0.18)), 
            footer_line1, text_color=(255, 255, 255, 255), font_obj=font_footer
        )
        draw_high_contrast_text(
            draw_overlay,
            (banner_x1 + int((banner_w - w_f2) / 2), banner_y1 + int(banner_h * 0.54)), 
            footer_line2, text_color=(255, 255, 255, 255), font_obj=font_footer
        )

        # Perform master composition merge pass
        final_composite = Image.alpha_composite(base, overlay_layer)
        final_rgb = final_composite.convert("RGB")
        final_rgb.save(output_filename, "JPEG", quality=98)
        return output_filename

    except Exception as e:
        print(f"Error during Pillow graphic composition: {e}")
        return None

# --- Social Media Platform API Channels ---
def post_image_to_facebook_page(image_path, message):
    if not FACEBOOK_PAGE_ID or "YOUR_FACEBOOK" in FACEBOOK_ACCESS_TOKEN:
        print("Facebook token placeholders active. Skipping live publication upload step.")
        return True
    url = f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/photos"
    payload = {"caption": message, "access_token": FACEBOOK_ACCESS_TOKEN}
    try:
        with open(image_path, "rb") as img_file:
            res = requests.post(url, data=payload, files={"source": img_file}, timeout=25)
        if res.status_code == 200:
            print("Successfully published visual asset to Facebook Page Feed.")
            return True
        print(f"Facebook Graph API failure status ({res.status_code}): {res.text}")
        return False
    except Exception as e:
        print(f"Facebook request connection exception: {e}")
        return False

def post_image_to_twitter(image_path, message):
    if not TWITTER_API_KEY or "YOUR_TWITTER" in TWITTER_API_KEY:
        print("Twitter credentials left as placeholders. Skipping live publication upload step.")
        return True
    try:
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type: mime_type = "image/jpeg"
        
        with open(image_path, "rb") as img_file:
            files = [('media', (os.path.basename(image_path), img_file, mime_type))]
            upload_res = requests.post(upload_url, auth=auth, data={'media_category': 'tweet_image'}, files=files, timeout=25)
            
        media_id = upload_res.json().get("media_id_string")
        if not media_id:
            print(f"Twitter media asset registration rejected: {upload_res.text}")
            return False

        tweet_url = "https://api.twitter.com/2/tweets"
        oauth = OAuth1Session(TWITTER_API_KEY, client_secret=TWITTER_API_SECRET,
                              resource_owner_key=TWITTER_ACCESS_TOKEN, resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET)
        res = oauth.post(tweet_url, json={"text": message, "media": {"media_ids": [str(media_id)]}}, timeout=20)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"X/Twitter API connection failure: {e}")
        return False

def get_kenya_trends():
    url = "https://trends24.in/kenya/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            container = soup.find('div', class_='list-container')
            if container:
                return [tag.get_text(strip=True) for tag in container.find_all('a')][:5]
        return []
    except Exception:
        return []

def append_hashtags_to_message(message, hashtags):
    formatted = [h if h.startswith('#') else f'#{h}' for h in hashtags if h.strip()]
    full_msg = f"{message} " + " ".join(formatted).strip()
    while len(full_msg) > 278 and formatted:
        formatted.pop()
        full_msg = f"{message} " + " ".join(formatted).strip()
    return full_msg[:278]

def generate_facebook_ai_content(topic):
    if not model: 
        return f"Transform your operations with SasAfrik's enterprise infrastructure suites. Contact our Nairobi office on +254720000803 or click here to chat: https://wa.me/254720000803. {topic}"
    
    # ADVANCED COPYWRITING STUDIO: Length constraints completely lifted for maximum executive persuasion
    prompt = f"""
You are an elite, world-class Chief Marketing Officer and corporate copywriter for SasAfrik, a luxury-tier enterprise software consultancy in Nairobi. 
Write a deeply compelling, authoritative, long-form Facebook post designed to capture the attention of corporate founders, enterprise executives, and tech directors regarding: '{topic}'.

Strict Copywriting Guidelines:
1. Ignore all length or character limits entirely. Write a thorough, persuasive corporate case study and capability pitch. 
2. Open with a highly strategic, unforgettable business hook detailing structural operational issues or digital revenue scaling realities across modern enterprise environments in East Africa.
3. Dive into robust technical value insights—breaking down how custom cloud architecture, systems integration, and clean engineering logic directly amplify an enterprise's bottom-line.
4. Maintain a highly professional, expert, polished corporate tone throughout. Use clean layout paragraphs and elegant bullet structures to make reading smooth.
5. You MUST append this exact Call-To-Action signature block at the tail end of your copy:

🚀 INITIALIZE YOUR DIGITAL TRANSFORMATION:
🌐 Corporate Website: https://www.sasafrik.com
📞 Direct Office Hotline: +254 720 000 803
💬 Connect Instantly via WhatsApp: Click this official routing link to launch a direct technical consultation with our engineering desk right now: https://wa.me/254720000803?text=Hello%20SasAfrik%2C%20I%20am%20interested%20in%20your%20software%20engineering%20services.

Output ONLY the final post text. Do not introduce it with meta-comments.
"""
    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return "Optimize your systems with our premium engineering options. Visit www.sasafrik.com, call +254720000803, or chat directly on WhatsApp: https://wa.me/254720000803"

def generate_twitter_ai_content(topic):
    if not model: 
        return "Pioneering enterprise operations scaling from Nairobi to the global stage. Visit sasafrik.com or chat on WhatsApp: https://wa.me/254720000803"
    
    # SHORT-FORM CALL TO ACTION LINKS
    prompt = f"""
Write one concise, high-impact marketing tweet for X (max 180 characters) regarding: '{topic}'.
You MUST explicitly feature our website link (sasafrik.com) and our quick WhatsApp chat deep link (https://wa.me/254720000803) right inside the text.
"""
    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return "Scale your tech systems! Visit sasafrik.com or click here to chat on WhatsApp instantly: https://wa.me/254720000803"

# --- Orchestrated Execution Engine ---
def run_orchestrated_pipeline():
    print(f"\n=== Initializing Premium Marketing Production Loop: {time.ctime()} ===")
    
    settings = load_settings()
    processed = set(load_processed_topics())
    trends = get_kenya_trends()

    available_topics = [t for t in TOPICS if t not in processed]
    if not available_topics:
        if settings.get("restart", True):
            print("All predefined topics processed. Flushing tracking manifest to restart loop...")
            clear_processed_topics()
            available_topics = TOPICS.copy()
        else:
            print("All campaign lines fully executed. Halting runtime loop configuration.")
            return

    selected_topic = random.choice(available_topics)
    print(f"Target Campaign Directive Selected: '{selected_topic}'")

    raw_canvas = "temp_flux_raw.jpg"
    final_canvas = "masterpiece_final.jpg"
    
    try:
        # 1. Optimize image generation prompt using the strict brand photorealism rules
        optimized_prompt = generate_flux_masterpiece_prompt(selected_topic)
        print(f"Art Director Generated Visual Context: {optimized_prompt}")

        # 2. Call Free Image Generation Cluster 
        if not call_flux_api_and_save(optimized_prompt, raw_canvas):
            print("System Timeout: External API failed to emit graphic binaries. Ending cycle.")
            return

        # 3. Composite brand layers using Pillow locally
        if not composite_masterpiece(raw_canvas, LOGO_ASSET_PATH, final_canvas):
            print("Composition Error: Graphic compositor failed to watermark assets. Ending cycle.")
            return

        # 4. Generate optimized post text using Gemini
        fb_text = generate_facebook_ai_content(selected_topic)
        x_text = generate_twitter_ai_content(selected_topic)
        x_text_bundled = append_hashtags_to_message(x_text, trends)

        # 5. Broadcast final visual production to social feeds
        fb_status = post_image_to_facebook_page(final_canvas, fb_text)
        x_status = post_image_to_twitter(final_canvas, x_text_bundled)

        print(f"Network Broadcast Status -> Facebook: {fb_status} | X/Twitter: {x_status}")

        if fb_status or x_status:
            add_processed_topic(selected_topic)
            print("Campaign iteration marked successfully in local state histories tracking log.")

    finally:
        # Safely delete temporary image artifacts from disk space
        for path in [raw_canvas, final_canvas]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Cleaned up runtime workspace asset: {path}")
                except Exception:
                    pass
                    
    print("=== Production Pipeline Execution Completed Cleanly ===")

if __name__ == "__main__":
    run_orchestrated_pipeline()