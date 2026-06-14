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
try:
    from requests_oauthlib import OAuth1Session, OAuth1
    TWITTER_LIB_AVAILABLE = True
except Exception:
    OAuth1Session = None
    OAuth1 = None
    TWITTER_LIB_AVAILABLE = False
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()

# --- Configuration & Credentials ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROCESSED_FILE = os.getenv("PROCESSED_TOPICS_FILE", "processed_topics.json")
PROCESSED_REELS_FILE = os.getenv("PROCESSED_REELS_FILE", "processed_reels.json")
SETTINGS_FILE = os.getenv("POST_SETTINGS_FILE", "post_settings.json")

LOGO_ASSET_PATH = "logo.png" 
FLUX_BASE_URL = os.getenv("FLUX_BASE_URL", "https://image.pollinations.ai/p/")

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "YOUR_FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "YOUR_FACEBOOK_ACCESS_TOKEN")
PAUSE_TWITTER = os.getenv("PAUSE_TWITTER", "false").lower()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "YOUR_TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "YOUR_TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "YOUR_TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "YOUR_TWITTER_ACCESS_TOKEN_SECRET")

# --- Master 30-Day Reels Prompt Bank ---
REELS_PROMPTS = [
    # 🏗️ Category 1: Digital Product & UX Engineering ("Design is Revenue")
    {"day": 1, "title": "Aesthetics vs. Revenue Call", "hook": "Stop designing for aesthetics. Design for revenue.", "body": "SasAfrik maps seamless user journeys engineered to aggressively maximize retention and prevent cart abandonment on African networks.", "cta": "Stop losing traffic.\nEngineer your growth with SasAfrik."},
    {"day": 2, "title": "The Network Reality Check", "hook": "Is your app built for real-world African network conditions?", "body": "We optimize frameworks to execute lightweight queries smoothly under unstable connectivity. Usability testing is our secret.", "cta": "Build apps that convert seamlessly from day one.\nDrop us a message."},
    {"day": 3, "title": "MVP Journey to Millions", "hook": "The Million User Roadmap.", "body": "Move smoothly from discovery to robust technical architecture blueprints, agile execution delivery, and live enterprise production.", "cta": "Scale with zero compromises.\nVisit sasafrik.com."},
    {"day": 4, "title": "UX Friction Killers", "hook": "Every unnecessary step cuts your conversion by 20%.", "body": "Clunky registration forms kill enterprise conversions. We design clean, frictionless checkout flows that drive client sales.", "cta": "Eliminate user drop-offs.\nPartner with SasAfrik UX masters."},
    {"day": 5, "title": "The Mobile First Empire", "hook": "Desktop software is dying across East Africa.", "body": "Over 90% of your digital consumers access your systems via mobile. We engineer offline-first syncing mobile applications.", "cta": "Own the consumer screen.\nMessage SasAfrik today."},
    
    # 🤖 Category 2: Intelligent Business Workflows & AI Automation
    {"day": 6, "title": "Recapture 80% of Your Time", "hook": "Your team isn't lazy. They're trapped in manual workflows.", "body": "Bespoke AI automated scripts can easily run backend entries, reconcile invoices, and execute multi-step database syncs in milliseconds.", "cta": "Recapture 80% of operational bandwidth.\nAutomate with SasAfrik."},
    {"day": 7, "title": "Goodbye Manual Data Entry", "hook": "Manual data entry is a quiet corporate profit killer.", "body": "We build intelligent automation pipelines that transform unstructured inbound emails, PDFs, or forms into clean enterprise data arrays.", "cta": "Eliminate costly human errors.\nAutomate your business operations."},
    {"day": 8, "title": "Legacy Systems Modernization", "hook": "Is aging, slow legacy software holding your company back?", "body": "Don't tear it down. SasAfrik encapsulates old applications behind modern high-speed APIs to cleanly supercharge performance.", "cta": "Modernize without business downtime.\nContact SasAfrik."},
    {"day": 9, "title": "Intelligent Email Parsing", "hook": "Stop losing hours reading repetitive back-office emails.", "body": "Our customized AI workflow layers automatically parse attachments, validate contents, extract invoices, and update CRM records.", "cta": "Automate your communication stacks.\nTalk to SasAfrik."},
    {"day": 10, "title": "Automated Stock Audits", "hook": "Mismatched inventory and warehouse tracking costs millions.", "body": "We integrate distributed retail endpoints natively into unified backends, running automated stock adjustments 24/7.", "cta": "Gain real-time operational visibility.\nMessage SasAfrik."},

    # 🌍 Category 3: Unified African Market Integrations
    {"day": 11, "title": "The Localization Bridge", "hook": "Localizing your software infrastructure is how you survive.", "body": "We build bulletproof software bridges connecting custom backends natively to real-time M-Pesa channels and automated WhatsApp desks.", "cta": "Bridge your tech with African markets.\nTalk to SasAfrik."},
    {"day": 12, "title": "Power of USSD & SMS", "hook": "No reliable internet access? No problem for your business.", "body": "We design high-availability offline USSD systems backing high-tier web logic, keeping your platform accessible to every buyer.", "cta": "Build resilient digital tech ecosystems.\nConnect with us."},
    {"day": 13, "title": "Multi-Currency Banking Layers", "hook": "Cross-border payment infrastructure should never fail.", "body": "We bridge regional automated clearing houses and digital wallets, allowing seamless corporate scaling and collections across East Africa.", "cta": "Expand your financial network.\nPartner with SasAfrik."},
    {"day": 14, "title": "The WhatsApp Commerce Engine", "hook": "Your target customers spend their entire day on WhatsApp.", "body": "We replace complex registration forms with custom automated conversational engines that view inventory and process sales securely.", "cta": "Turn simple chats into real sales.\nContact SasAfrik today."},
    {"day": 15, "title": "Real-Time B2B Ledger Sync", "hook": "Manual statements reconciliation creates huge fraud risks.", "body": "We instantly link mobile merchant statements straight into production bookkeeping layers, validating your ledger accounts instantly.", "cta": "Secure your enterprise financial channels.\nConnect with us."},

    # ☁️ Category 4: Cloud Infrastructure & Platform Engineering
    {"day": 16, "title": "100% Uptime Guarantee", "hook": "What does just 10 minutes of server downtime cost you?", "body": "We engineer cloud infrastructure across AWS, Azure, and GCP using secure zero-trust containers to handle sudden traffic spikes.", "cta": "Build unbreakable 100% uptime systems.\nProtect with SasAfrik."},
    {"day": 17, "title": "What is FinOps?", "hook": "You are probably overpaying for your cloud setup.", "body": "We introduce automated cost-scaling FinOps metrics, gracefully scaling compute power down to absolute zero during quiet traffic hours.", "cta": "Stop wasting your technical runway.\nLet SasAfrik optimize cloud costs."},
    {"day": 18, "title": "The Database Disaster Test", "hook": "Could your business survive a sudden database wipe?", "body": "We deploy geographically isolated, auto-replicating backup pipelines to completely restore digital operations in minutes.", "cta": "Secure your corporate data fortress.\nTalk to SasAfrik."},
    {"day": 19, "title": "Containerized Scale", "hook": "Does your web application slow down during peak hours?", "body": "We transform monolithic applications into microservices that scale dynamically across automated clusters as usage grows.", "cta": "Deploy high-performance, unbreakable backends.\nReach out to us."},
    {"day": 20, "title": "The Security Shield Architecture", "hook": "Cyber threats target exposed company infrastructure ports.", "body": "We implement end-to-end firewalls and cryptographic data encryption layers fully compliant with the Kenya Data Protection Act.", "cta": "Protect your brand reputation.\nConsult with SasAfrik today."},

    # 📈 Category 5: Automated Social Growth & Marketing Engines
    {"day": 21, "title": "Hands-Free Marketing Engine", "hook": "Automate your lead generation pipelines completely.", "body": "We build software engines that distribute content, capture discovery logs, and route qualified enterprise prospects into your CRM.", "cta": "Turn profiles into automated sales pipelines.\nPartner with SasAfrik."},
    {"day": 22, "title": "Automated Content Funnels", "hook": "Stop publishing marketing campaigns manually.", "body": "Our bespoke automation systems dynamically format assets and trigger multichannels based on historical engagement patterns.", "cta": "Scale your brand pipeline automatically.\nTalk to SasAfrik."},
    {"day": 23, "title": "Dynamic Email Retargeting", "hook": "Cold website leads are forgotten enterprise cash assets.", "body": "We capture exact user platform context and instantly drop them into hyper-personalized, value-driven email nurture loops.", "cta": "Convert missed platform sessions smoothly.\nMessage SasAfrik."},
    {"day": 24, "title": "Real-time Customer Dashboards", "hook": "Stop managing your brand using outdated weekly reports.", "body": "We assemble live visual dashboards showing system behavior, server health, conversion streams, and bottom-line growth metrics.", "cta": "Lead with absolute empirical metrics.\nConnect with SasAfrik."},
    {"day": 25, "title": "Predictive Enterprise Churn", "hook": "Spot subscription and client cancellations before they happen.", "body": "Our custom predictive logic tracks behavioral anomalies, alerting your team to secure accounts before users leave.", "cta": "Protect your stable recurring revenues.\nChat with us today."},

    # 💼 Category 6: Corporate Authority & Social Proof
    {"day": 26, "title": "The B2B Redesign Rule", "hook": "An outdated platform actively drives away premium clients.", "body": "We build elite, strategic corporate websites that establish instant market authority and continuously turn visitors into leads.", "cta": "Transform your digital footprint.\nContact SasAfrik today."},
    {"day": 27, "title": "Making Complex Effortless", "hook": "Software should simplify your operations, not add bugs.", "body": "We wrap powerful database operations behind highly aesthetic, clean mobile windows, bringing complete clarity to supply chains.", "cta": "Launch world-class custom systems.\nPartner with SasAfrik."},
    {"day": 28, "title": "The Zero Tech Debt Mandate", "hook": "Cheap code is the single most expensive corporate mistake.", "body": "We write clean, strictly documented, object-oriented code backed by rigorous integration testing suites to allow smooth upgrades.", "cta": "Build digital company assets built to last.\nTalk to SasAfrik."},
    {"day": 29, "title": "Unified Operations Control", "hook": "Stop logging into ten different disconnected apps daily.", "body": "We unify your frontend checkouts, internal inventory registries, and financial tracking layers into one source of truth.", "cta": "Unify your fragmented software setup.\nMessage SasAfrik."},
    {"day": 30, "title": "Engineered for Global Scale", "hook": "Built in Nairobi. Scaled for the global stage.", "body": "SasAfrik engineers premium custom cloud applications and software backends designed to sustain millions of transactions easily.", "cta": "Accelerate your product development roadmap.\nPartner with SasAfrik."}
]

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

# Initialize Gemini Model
model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Error initializing Gemini: {e}")

# --- Storage Management Utilities ---
def load_processed_items(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception:
        return []

def save_processed_items(filepath, item_list):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(list(item_list), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error preserving process state file {filepath}: {e}")

# --- 100% Free Local Dynamic Video Reels Rendering Engine ---
def compile_reels_video_file(reels_dict, output_path="temp_reel.mp4"):
    print(f"Compiling Kinetic Video Reel locally (100% Free) for: {reels_dict['title']}")
    width, height = 1080, 1920
    fps = 24
    
    scenes = [
        {"text": reels_dict["hook"], "duration": 4, "text_color": (239, 68, 68)},  # Crimson Hook
        {"text": reels_dict["body"], "duration": 21, "text_color": (255, 255, 255)}, # Editorial White
        {"text": reels_dict["cta"], "duration": 5, "text_color": (56, 189, 248)}    # Sky Blue Callout
    ]

    try:
        font_main = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
        font_brand = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    except Exception:
        font_main = font_brand = ImageFont.load_default()

    def wrap_text_lines(text, font, max_w):
        words = text.split()
        lines = []
        current = []
        for word in words:
            test_line = ' '.join(current + [word]) if current else word
            try: bbox = font.getbbox(test_line); w = bbox[2] - bbox[0]
            except AttributeError: w = font.getsize(test_line)[0] if hasattr(font, 'getsize') else 500
            
            if w <= max_w:
                current.append(word)
            else:
                lines.append(' '.join(current))
                current = [word]
        if current: lines.append(' '.join(current))
        return lines

    # Initialize video output handle via OpenCV natively
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Generate a beautiful, math-vector midnight gradient background locally
    bg_array = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        r = int(10 + (y / height) * 15)
        g = int(15 + (y / height) * 20)
        b = int(32 + (y / height) * 25)
        bg_array[y, :] = [r, g, b]
    
    bg_base_pil = Image.fromarray(bg_array)
    frame_counter = 0

    for scene in scenes:
        total_frames = scene["duration"] * fps
        wrapped = wrap_text_lines(scene["text"], font_main, width - 180)
        line_height = 80
        total_h = len(wrapped) * line_height
        y_cursor_start = (height - total_h) // 2

        for f in range(total_frames):
            frame_counter += 1
            frame_canvas = bg_base_pil.copy()
            draw = ImageDraw.Draw(frame_canvas)

            # Interactive Background Dynamic Grid Animation Lines
            grid_spacing = 120
            grid_offset = int(frame_counter * 1.5) % grid_spacing
            
            for x in range(grid_offset, width, grid_spacing):
                draw.line([(x, 0), (x, height)], fill=(56, 189, 248, 12), width=1)
            for y_line in range(grid_offset, height, grid_spacing):
                draw.line([(0, y_line), (width, y_line)], fill=(56, 189, 248, 12), width=1)

            # Elegant Frame Accents
            draw.rectangle([50, 50, width - 50, height - 50], outline=(56, 189, 248, 25), width=3)
            draw.text((width // 2, 140), "SASAFRIK SOFTWARE CONSULTANCY", fill=(148, 163, 184), font=font_brand, anchor="mm")
            # Render the reel title prominently under the brand header
            try:
                title_text = reels_dict.get("title", "")
                if title_text:
                    draw.text((width // 2, 200), title_text, fill=(236, 240, 241), font=font_brand, anchor="mm")
            except Exception:
                pass
            draw.text((width // 2, height - 140), "💬 wa.me/254720000803 | hello@sasafrik.com", fill=(148, 163, 184), font=font_brand, anchor="mm")

            y_cursor = y_cursor_start
            for line in wrapped:
                for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3)]:
                    draw.text((width // 2 + dx, y_cursor + dy), line, fill=(0, 0, 0, 255), font=font_main, anchor="mm")
                draw.text((width // 2, y_cursor), line, fill=scene["text_color"], font=font_main, anchor="mm")
                y_cursor += line_height

            opencv_frame = cv2.cvtColor(np.array(frame_canvas), cv2.COLOR_RGB2BGR)
            video_writer.write(opencv_frame)

    video_writer.release()
    return output_path

# --- Facebook Reels Publishing API Engine ---
def upload_reel_to_facebook_page(video_path, description):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN.startswith("YOUR_") or "YOUR_FACEBOOK" in FACEBOOK_ACCESS_TOKEN:
        print("Facebook credentials missing or default. Skipping live Reels upload step.")
        return False

    print("Publishing video container directly to Facebook Reels ecosystem...")
    init_url = f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/video_reels"
    
    try:
        # Use uppercase phases as required by some Graph API versions
        init_res = requests.post(init_url, data={"upload_phase": "START", "access_token": FACEBOOK_ACCESS_TOKEN}, timeout=20)
        init_data = init_res.json()
        video_id = init_data.get("video_id") or init_data.get("id")
        upload_url = init_data.get("upload_url") or init_data.get("upload_url")

        # If initialization failed or didn't return an upload URL, fall back to single-request upload
        if not upload_url:
            print(f"Resumable init did not return upload_url (response: {init_res.text}). Falling back to direct multipart upload.")
            with open(video_path, "rb") as f:
                files = {"source": f}
                data = {"description": description, "access_token": FACEBOOK_ACCESS_TOKEN}
                direct_res = requests.post(f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/videos", files=files, data=data, timeout=120)
                if direct_res.status_code == 200 or direct_res.status_code == 201:
                    print("Direct multipart upload succeeded.")
                    return True
                else:
                    print(f"Direct multipart upload failed: {direct_res.status_code} {direct_res.text}")
                    return False

        # Read binary and send to provided upload_url
        with open(video_path, "rb") as f_file:
            video_binary = f_file.read()

        headers = {"Authorization": f"OAuth {FACEBOOK_ACCESS_TOKEN}", "offset": "0", "file_size": str(len(video_binary))}
        upload_res = requests.post(upload_url, data=video_binary, headers=headers, timeout=60)
        if upload_res.status_code != 200:
            print(f"Reels payload chunk rejected: {upload_res.text}")
            return False

        finish_payload = {"upload_phase": "FINISH", "video_id": video_id, "video_state": "PUBLISHED", "description": description, "access_token": FACEBOOK_ACCESS_TOKEN}
        finish_res = requests.post(f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/video_reels", data=finish_payload, timeout=20)
        if finish_res.status_code == 200:
            return True
        # Sometimes Graph returns JSON with success key
        try:
            return finish_res.json().get("success", False)
        except Exception:
            return False

    except Exception as e:
        print(f"Reels upload exception: {e}")
        return False

# --- Core Business Automation Channels (Image Posts) ---
def generate_flux_masterpiece_prompt(topic):
    if not model: return f"Candid photography of professional tech workspace in Nairobi. {topic[:50]}"
    prompt_builder = f"""
You are an elite Senior Art Director for SasAfrik, a premier technology company in Nairobi, Kenya.
Transform the following marketing TOPIC into ONE hyper-realistic, human-centric image generation prompt (max 45 words) tailored for FLUX.1 Schnell.
TOPIC: "{topic}"
Ensure style reflects true candid corporate lifestyle commercial photography. No neon tracks, and no floating holographic UI elements.
"""
    try: return model.generate_content(prompt_builder).text.strip()
    except Exception: return topic[:100]

def call_flux_api_and_save(flux_prompt, filename="temp_flux_raw.jpg"):
    safe_prompt = urllib.parse.quote(flux_prompt)
    target_url = f"{FLUX_BASE_URL}{safe_prompt}?width=1024&height=1024&model=flux&seed={random.randint(1, 9999999)}"
    try:
        print(f"Calling FLUX API: {target_url}")
        res = requests.get(target_url, timeout=45)
        if res.status_code == 200:
            with open(filename, 'wb') as f: f.write(res.content)
            return filename
        else:
            print(f"Flux API returned status {res.status_code}: {res.text}")
            # Fallback: use local logo as a placeholder if available so pipeline can continue
            if os.path.exists(LOGO_ASSET_PATH):
                try:
                    from shutil import copyfile
                    copyfile(LOGO_ASSET_PATH, filename)
                    print(f"Using local logo fallback for image: {LOGO_ASSET_PATH}")
                    return filename
                except Exception:
                    pass
            return None
    except Exception: return None

def composite_masterpiece(base_image_path, logo_path=LOGO_ASSET_PATH, output_filename="masterpiece_final.jpg"):
    try:
        base = Image.open(base_image_path).convert("RGBA")
        base_w, base_h = base.size
        overlay_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay_layer)
        logo_bottom_y = int(base_h * 0.05) 

        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo_w, logo_h = logo.size
            target_w = int(base_w * 0.24)
            target_h = int(logo_h * (target_w / logo_w))
            logo_scaled = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            base.alpha_composite(logo_scaled, (int(base_w * 0.05), int(base_w * 0.05)))
            logo_bottom_y = int(base_w * 0.05) + target_h

        try:
            font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.026))
            font_body = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.021))
            font_footer = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.020))
        except Exception:
            font_title = font_body = font_footer = ImageFont.load_default()

        card_w, card_h = int(base_w * 0.50), int(base_h * 0.44)
        card_x1, card_y1 = int(base_w * 0.05), logo_bottom_y + int(base_h * 0.03)
        draw_overlay.rounded_rectangle([card_x1, card_y1, card_x1 + card_w, card_y1 + card_h], radius=16, fill=(10, 15, 30, 180), outline=(255, 255, 255, 45), width=2)

        def draw_high_contrast_text(draw_obj, position, text_str, text_color, font_obj):
            x, y = position
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                draw_obj.text((x + dx, y + dy), text_str, fill=(0,0,0,255), font=font_obj)
            draw_obj.text((x, y), text_str, fill=text_color, font=font_obj)

        draw_high_contrast_text(draw_overlay, (card_x1 + int(card_w * 0.06), card_y1 + int(card_h * 0.08)), "WE DESIGN & DEVELOP", (56, 189, 248, 255), font_title)
        
        capabilities = ["• Web Platforms & Portals", "• Enterprise API Integrations", "• High-Scale Mobile Apps", "• Full-Stack Applications", "• Workflow Automation Engines", "• Custom AI Conversational Bots"]
        y_cursor = card_y1 + int(card_h * 0.22)
        for item in capabilities:
            draw_high_contrast_text(draw_overlay, (card_x1 + int(card_w * 0.06), y_cursor), item, (255, 255, 255, 255), font_body)
            y_cursor += int(card_h * 0.11)

        banner_w, banner_h = int(base_w * 0.74), int(base_h * 0.095)
        banner_x1, banner_y1 = int((base_w - banner_w) / 2), int(base_h - banner_h - int(base_h * 0.04))
        draw_overlay.rounded_rectangle([banner_x1, banner_y1, banner_x1 + banner_w, banner_y1 + banner_h], radius=12, fill=(10, 15, 30, 245), outline=(56, 189, 248, 120), width=2)

        f1 = "📞 Call / WhatsApp: +254 720 000 803"
        f2 = "🌐 sasafrik.com  |  ✉️ hello@sasafrik.com"
        draw_high_contrast_text(draw_overlay, (banner_x1 + 40, banner_y1 + int(banner_h * 0.18)), f1, (255, 255, 255, 255), font_footer)
        draw_high_contrast_text(draw_overlay, (banner_x1 + 40, banner_y1 + int(banner_h * 0.54)), f2, (255, 255, 255, 255), font_footer)

        final_composite = Image.alpha_composite(base, overlay_layer).convert("RGB")
        final_composite.save(output_filename, "JPEG", quality=98)
        return output_filename
    except Exception as e:
        print(f"Error compositing standard image graphic layout: {e}")
        return None

def post_image_to_facebook_page(image_path, message):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN.startswith("YOUR_") or "YOUR_FACEBOOK" in FACEBOOK_ACCESS_TOKEN:
        print("Facebook credentials missing or default. Skipping image post to Facebook.")
        return False
    url = f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/photos"
    try:
        with open(image_path, "rb") as img_file:
            res = requests.post(url, data={"caption": message, "access_token": FACEBOOK_ACCESS_TOKEN}, files={"source": img_file}, timeout=25)
        return res.status_code == 200
    except Exception: return False

def post_image_to_twitter(image_path, message):
    if PAUSE_TWITTER == 'true':
        print("Twitter posting is currently paused via PAUSE_TWITTER. Skipping Twitter upload.")
        return False
    if not TWITTER_LIB_AVAILABLE:
        print("Twitter client library 'requests_oauthlib' is not installed. Skipping Twitter upload.")
        return False
    if not TWITTER_API_KEY or "YOUR_TWITTER" in TWITTER_API_KEY: return True
    try:
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        with open(image_path, "rb") as img_file:
            upload_res = requests.post(upload_url, auth=auth, data={'media_category': 'tweet_image'}, files=[('media', (os.path.basename(image_path), img_file, 'image/jpeg'))], timeout=25)
        media_id = upload_res.json().get("media_id_string")
        if not media_id: return False
        oauth = OAuth1Session(TWITTER_API_KEY, client_secret=TWITTER_API_SECRET, resource_owner_key=TWITTER_ACCESS_TOKEN, resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET)
        res = oauth.post("https://api.twitter.com/2/tweets", json={"text": message, "media": {"media_ids": [str(media_id)]}}, timeout=20)
        return res.status_code in [200, 201]
    except Exception: return False

def generate_facebook_ai_content(topic):
    # Compact CTA to fit within the total character budget
    cta = "Chat: https://wa.me/254720000803 Web: https://sasafrik.com"

    def _trim_for_facebook(body, cta_text, max_len=155):
        # Reserve 1 space between body and CTA
        allowed = max_len - len(cta_text) - 1
        if allowed <= 0:
            # CTA itself exceeds budget; truncate CTA (rare)
            return cta_text[:max_len]
        if len(body) <= allowed:
            return f"{body} {cta_text}"
        # Truncate at word boundary
        truncated = body[:allowed].rsplit(' ', 1)[0]
        if not truncated:
            truncated = body[:allowed]
        return f"{truncated}… {cta_text}"

    if not model:
        body = "Scale your custom digital ecosystem instantly."
        return _trim_for_facebook(body, cta)

    # Ask the model to produce a concise body only (no CTA/signature)
    prompt = f"""
You are a senior corporate copywriter for SasAfrik.
Write a concise, high-impact Facebook post body (single paragraph, no CTA) for corporate founders and tech leaders about: {topic}
Keep the body short and focused — we will append a short CTA and enforce a 125-character limit overall.
Output ONLY the post body text.
"""
    try:
        body = model.generate_content(prompt).text.strip()
    except Exception:
        body = "Optimize your enterprise platforms."

    return _trim_for_facebook(body, cta)

def generate_twitter_ai_content(topic):
    if not model: return "Scale your tech systems! Visit sasafrik.com or click here to chat on WhatsApp instantly: https://wa.me/254720000803"
    prompt = f"Write one high-impact tweet for X (max 180 characters) about '{topic}' featuring sasafrik.com and https://wa.me/254720000803"
    try: return model.generate_content(prompt).text.strip()
    except Exception: return "Scale your tech systems! Visit sasafrik.com or chat live on WhatsApp instantly: https://wa.me/254720000803"

# --- Orchestrated Execution Engine ---
def execute_reels_pipeline():
    print(f"=== Starting Reels Automation Track: {time.ctime()} ===")
    processed = load_processed_items(PROCESSED_REELS_FILE)
    
    if len(processed) >= len(REELS_PROMPTS):
        print("All 30 master prompts executed cleanly. Flushing log history manifest to restart cycle loop.")
        processed = []
        save_processed_items(PROCESSED_REELS_FILE, [])

    target_reel = None
    for item in REELS_PROMPTS:
        if item["day"] not in processed:
            target_reel = item
            break

    if not target_reel:
        print("Reels queue state error. Ending execution pass.")
        return

    video_output = "reels_final_payload.mp4"
    # Initialize summary so we always write an output file even on early returns
    summary = {"mode": "REELS", "day": target_reel.get("day"), "title": target_reel.get("title"), "facebook_upload": False, "error": None}
    try:
        compiled_video = compile_reels_video_file(target_reel, video_output)
        if not compiled_video or not os.path.exists(compiled_video):
            summary["error"] = "video_compile_failed"
            print("Video compiler failed to output video binary stream object.")
            return

        description = f"🔥 {target_reel['hook']}\n\n{target_reel['body']}\n\n🚀 Partner with SasAfrik to transform your digital ecosystem: Click here to chat live with our technical engineers instantly via WhatsApp: wa.me/254720000803"
        success = upload_reel_to_facebook_page(compiled_video, description)
        
        if success:
            processed.append(target_reel["day"])
            save_processed_items(PROCESSED_REELS_FILE, processed)
            summary["facebook_upload"] = True
            print(f"Successfully tracked Day {target_reel['day']} inside production databases.")
    except Exception as e:
        summary["error"] = str(e)
    finally:
        # Emit summary regardless of early returns or errors
        try:
            with open("last_run_summary.json", "w", encoding="utf-8") as sf:
                json.dump(summary, sf, indent=2, ensure_ascii=False)
        except Exception:
            pass
        if os.path.exists(video_output):
            try: os.remove(video_output)
            except Exception: pass
    print("=== Reels Automation Segment Finished ===")

def execute_standard_post_pipeline():
    print(f"=== Starting Post Automation Track: {time.ctime()} ===")
    processed = set(load_processed_items(PROCESSED_FILE))
    available = [t for t in TOPICS if t not in processed]
    
    if not available:
        print("All predefined post topics processed. Flushing manifest to restart loop...")
        save_processed_items(PROCESSED_FILE, [])
        available = TOPICS.copy()

    selected_topic = random.choice(available)
    raw_canvas, final_canvas = "temp_flux_raw.jpg", "masterpiece_final.jpg"
    
    # Prepare summary early so it's always written
    summary = {"mode": "STANDARD_POST", "topic": selected_topic, "facebook_posted": False, "twitter_posted": False, "twitter_paused": (PAUSE_TWITTER == 'true'), "error": None}
    try:
        optimized_prompt = generate_flux_masterpiece_prompt(selected_topic)
        if not call_flux_api_and_save(optimized_prompt, raw_canvas):
            summary["error"] = "flux_api_failed"
            return
        if not composite_masterpiece(raw_canvas, LOGO_ASSET_PATH, final_canvas):
            summary["error"] = "composite_failed"
            return

        fb_text = generate_facebook_ai_content(selected_topic)
        x_text = generate_twitter_ai_content(selected_topic)

        fb_status = post_image_to_facebook_page(final_canvas, fb_text)
        x_status = post_image_to_twitter(final_canvas, x_text)
        # Summary and processing logic
        summary["facebook_posted"] = bool(fb_status)
        summary["twitter_posted"] = bool(x_status)

        if fb_status or x_status:
            processed.add(selected_topic)
            save_processed_items(PROCESSED_FILE, list(processed))
            print("Standard post marked successfully in local history.")

    except Exception as e:
        summary["error"] = str(e)
    finally:
        try:
            with open("last_run_summary.json", "w", encoding="utf-8") as sf:
                json.dump(summary, sf, indent=2, ensure_ascii=False)
        except Exception:
            pass
        for path in [raw_canvas, final_canvas]:
            if os.path.exists(path):
                try: os.remove(path)
                except Exception: pass
    print("=== Post Automation Segment Finished ===")

if __name__ == "__main__":
    mode = os.getenv("EXECUTION_MODE", "STANDARD_POST").upper()
    if mode == "REELS":
        execute_reels_pipeline()
    else:
        execute_standard_post_pipeline()