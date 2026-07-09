# main.py
import os
import json
import random
import time
import mimetypes
import re
import textwrap
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import cv2
    import numpy as np

    REELS_LIBS_AVAILABLE = True
except Exception:
    cv2 = None
    np = None
    REELS_LIBS_AVAILABLE = False

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

# --- Master 30-Day Content Bank ---
REELS_PROMPTS = [
    # 🏗️ Category 1: Digital Product & UX Engineering ("Design is Revenue")
    {"day": 1, "title": "Aesthetics vs. Revenue Call", "hook": "Stop designing for aesthetics. Design for revenue.",
     "body": "SasAfrik maps seamless user journeys engineered to aggressively maximize retention and prevent cart abandonment on African networks.",
     "cta": "Stop losing traffic.\nEngineer your growth with SasAfrik."},
    {"day": 2, "title": "The Network Reality Check",
     "hook": "Is your app built for real-world African network conditions?",
     "body": "We optimize frameworks to execute lightweight queries smoothly under unstable connectivity. Usability testing is our secret.",
     "cta": "Build apps that convert seamlessly from day one.\nDrop us a message."},
    {"day": 3, "title": "MVP Journey to Millions", "hook": "The Million User Roadmap.",
     "body": "Move smoothly from discovery to robust technical architecture blueprints, agile execution delivery, and live enterprise production.",
     "cta": "Scale with zero compromises.\nVisit sasafrik.com."},
    {"day": 4, "title": "UX Friction Killers", "hook": "Every unnecessary step cuts your conversion by 20%.",
     "body": "Clunky registration forms kill enterprise conversions. We design clean, frictionless checkout flows that drive client sales.",
     "cta": "Eliminate user drop-offs.\nPartner with SasAfrik UX masters."},
    {"day": 5, "title": "The Mobile First Empire", "hook": "Desktop software is dying across East Africa.",
     "body": "Over 90% of your digital consumers access your systems via mobile. We engineer offline-first syncing mobile applications.",
     "cta": "Own the consumer screen.\nMessage SasAfrik today."},

    # 🤖 Category 2: Intelligent Business Workflows & AI Automation
    {"day": 6, "title": "Recapture 80% of Your Time",
     "hook": "Your team isn't lazy. They're trapped in manual workflows.",
     "body": "Bespoke AI automated scripts can easily run backend entries, reconcile invoices, and execute multi-step database syncs in milliseconds.",
     "cta": "Recapture 80% of operational bandwidth.\nAutomate with SasAfrik."},
    {"day": 7, "title": "Goodbye Manual Data Entry", "hook": "Manual data entry is a quiet corporate profit killer.",
     "body": "We build intelligent automation pipelines that transform unstructured inbound emails, PDFs, or forms into clean enterprise data arrays.",
     "cta": "Eliminate costly human errors.\nAutomate your business operations."},
    {"day": 8, "title": "Legacy Systems Modernization",
     "hook": "Is aging, slow legacy software holding your company back?",
     "body": "Don't tear it down. SasAfrik encapsulates old applications behind modern high-speed APIs to cleanly supercharge performance.",
     "cta": "Modernize without business downtime.\nContact SasAfrik."},
    {"day": 9, "title": "Intelligent Email Parsing", "hook": "Stop losing hours reading repetitive back-office emails.",
     "body": "Our customized AI workflow layers automatically parse attachments, validate contents, extract invoices, and update CRM records.",
     "cta": "Automate your communication stacks.\nTalk to SasAfrik."},
    {"day": 10, "title": "Automated Stock Audits",
     "hook": "Mismatched inventory and warehouse tracking costs millions.",
     "body": "We integrate distributed retail endpoints natively into unified backends, running automated stock adjustments 24/7.",
     "cta": "Gain real-time operational visibility.\nMessage SasAfrik."},

    # 🌍 Category 3: Unified African Market Integrations
    {"day": 11, "title": "The Localization Bridge",
     "hook": "Localizing your software infrastructure is how you survive.",
     "body": "We build bulletproof software bridges connecting custom backends natively to real-time M-Pesa channels and automated WhatsApp desks.",
     "cta": "Bridge your tech with African markets.\nTalk to SasAfrik."},
    {"day": 12, "title": "Power of USSD & SMS", "hook": "No reliable internet access? No problem for your business.",
     "body": "We design high-availability offline USSD systems backing high-tier web logic, keeping your platform accessible to every buyer.",
     "cta": "Build resilient digital tech ecosystems.\nConnect with us."},
    {"day": 13, "title": "Multi-Currency Banking Layers",
     "hook": "Cross-border payment infrastructure should never fail.",
     "body": "We bridge regional automated clearing houses and digital wallets, allowing seamless corporate scaling and collections across East Africa.",
     "cta": "Expand your financial network.\nPartner with SasAfrik."},
    {"day": 14, "title": "The WhatsApp Commerce Engine",
     "hook": "Your target customers spend their entire day on WhatsApp.",
     "body": "We replace complex registration forms with custom automated conversational engines that view inventory and process sales securely.",
     "cta": "Turn simple chats into real sales.\nContact SasAfrik today."},
    {"day": 15, "title": "Real-Time B2B Ledger Sync",
     "hook": "Manual statements reconciliation creates huge fraud risks.",
     "body": "We instantly link mobile merchant statements straight into production bookkeeping layers, validating your ledger accounts instantly.",
     "cta": "Secure your enterprise financial channels.\nConnect with us."},

    # ☁️ Category 4: Cloud Infrastructure & Platform Engineering
    {"day": 16, "title": "100% Uptime Guarantee", "hook": "What does just 10 minutes of server downtime cost you?",
     "body": "We engineer cloud infrastructure across AWS, Azure, and GCP using secure zero-trust containers to handle sudden traffic spikes.",
     "cta": "Build unbreakable 100% uptime systems.\nProtect with SasAfrik."},
    {"day": 17, "title": "What is FinOps?", "hook": "You are probably overpaying for your cloud setup.",
     "body": "We introduce automated cost-scaling FinOps metrics, gracefully scaling compute power down to absolute zero during quiet traffic hours.",
     "cta": "Stop wasting your technical runway.\nLet SasAfrik optimize cloud costs."},
    {"day": 18, "title": "The Database Disaster Test", "hook": "Could your business survive a sudden database wipe?",
     "body": "We deploy geographically isolated, auto-replicating backup pipelines to completely restore digital operations in minutes.",
     "cta": "Secure your corporate data fortress.\nTalk to SasAfrik."},
    {"day": 19, "title": "Containerized Scale", "hook": "Does your web application slow down during peak hours?",
     "body": "We transform monolithic applications into microservices that scale dynamically across automated clusters as usage grows.",
     "cta": "Deploy high-performance, unbreakable backends.\nReach out to us."},
    {"day": 20, "title": "The Security Shield Architecture",
     "hook": "Cyber threats target exposed company infrastructure ports.",
     "body": "We implement end-to-end firewalls and cryptographic data encryption layers fully compliant with the Kenya Data Protection Act.",
     "cta": "Protect your brand reputation.\nConsult with SasAfrik today."},

    # 🤖 Category 5: Automated Social Growth & Marketing Engines
    {"day": 21, "title": "Hands-Free Marketing Engine", "hook": "Automate your lead generation pipelines completely.",
     "body": "We build software engines that distribute content, capture discovery logs, and route qualified enterprise prospects into your CRM.",
     "cta": "Turn profiles into automated sales pipelines.\nPartner with SasAfrik."},
    {"day": 22, "title": "Automated Content Funnels", "hook": "Stop publishing marketing campaigns manually.",
     "body": "Our bespoke automation systems dynamically format assets and trigger multichannels based on historical engagement patterns.",
     "cta": "Scale your brand pipeline automatically.\nTalk to SasAfrik."},
    {"day": 23, "title": "Dynamic Email Retargeting",
     "hook": "Cold website leads are forgotten enterprise cash assets.",
     "body": "We capture exact user platform context and instantly drop them into hyper-personalized, value-driven email nurture loops.",
     "cta": "Convert missed platform sessions smoothly.\nMessage SasAfrik."},
    {"day": 24, "title": "Real-time Customer Dashboards",
     "hook": "Stop managing your brand using outdated weekly reports.",
     "body": "We assemble live visual dashboards showing system behavior, server health, conversion streams, and bottom-line growth metrics.",
     "cta": "Lead with absolute empirical metrics.\nConnect with SasAfrik."},
    {"day": 25, "title": "Predictive Enterprise Churn",
     "hook": "Spot subscription and client cancellations before they happen.",
     "body": "Our custom predictive logic tracks behavioral anomalies, alerting your team to secure accounts before users leave.",
     "cta": "Protect your stable recurring revenues.\nChat with us today."},

    # 💼 Category 6: Corporate Authority & Social Proof
    {"day": 26, "title": "The B2B Redesign Rule", "hook": "An outdated platform actively drives away premium clients.",
     "body": "We build elite, strategic corporate websites that establish instant market authority and continuously turn visitors into leads.",
     "cta": "Transform your digital footprint.\nContact SasAfrik today."},
    {"day": 27, "title": "Making Complex Effortless", "hook": "Software should simplify your operations, not add bugs.",
     "body": "We wrap powerful database operations behind highly aesthetic, clean mobile windows, bringing complete clarity to supply chains.",
     "cta": "Launch world-class custom systems.\nPartner with SasAfrik."},
    {"day": 28, "title": "The Zero Tech Debt Mandate",
     "hook": "Cheap code is the single most expensive corporate mistake.",
     "body": "We write clean, strictly documented, object-oriented code backed by rigorous integration testing suites to allow smooth upgrades.",
     "cta": "Build digital company assets built to last.\nTalk to SasAfrik."},
    {"day": 29, "title": "Unified Operations Control",
     "hook": "Stop logging into ten different disconnected apps daily.",
     "body": "We unify your frontend checkouts, internal inventory registries, and financial tracking layers into one source of truth.",
     "cta": "Unify your fragmented software setup.\nMessage SasAfrik."},
    {"day": 30, "title": "Engineered for Global Scale", "hook": "Built in Nairobi. Scaled for the global stage.",
     "body": "SasAfrik engineers premium custom cloud applications and software backends designed to sustain millions of transactions easily.",
     "cta": "Accelerate your product development roadmap.\nPartner with SasAfrik."}
]

# Initialize Gemini Model
model = None
if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("YOUR_"):
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Gemini API initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing Gemini: {e}")
else:
    print("⚠️ Warning: GEMINI_API_KEY is missing or set to default values.")


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


def sanitize_generated_copy(text):
    if not text:
        return ""

    cleaned = str(text)
    patterns = [
        r"https?://wa\.me/\S+",
        r"(?i)\bgenerated by ai\b",
        r"(?i)\bai-generated\b",
        r"(?i)\bas an ai\b",
        r"(?i)\bas a language model\b",
        r"(?i)\bchatgpt\b",
        r"(?i)\bopenai\b",
        r"(?i)\bmodel output\b",
        r"(?i)\bgenerated content\b",
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip(" \n\t-:;,.")
    cleaned = cleaned.replace(" ,", ",")
    return cleaned


def fetch_trending_song_audio(query, output_mp3_path):
    """
    Searches for and downloads the current top trending song in Kenya.
    Falls back gracefully to a royalty-free energetic Afrobeat track if yt-dlp is not present.
    """
    print(f"🎵 Searching and fetching trending sound matching: '{query}'...")

    # Method 1: Try using yt_dlp if available in the environment
    try:
        import yt_dlp
        print("⚡ yt_dlp detected. Extracting audio from YouTube search results...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_mp3_path.replace('.mp3', ''),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])
            temp_expected = output_mp3_path.replace('.mp3', '') + '.mp3'
            if os.path.exists(temp_expected) and temp_expected != output_mp3_path:
                os.rename(temp_expected, output_mp3_path)
            if os.path.exists(output_mp3_path):
                print(f"✅ Successfully fetched live trending audio: {output_mp3_path}")
                return True
    except Exception as e:
        print(f"⚠️ YouTube direct extraction bypassed (yt_dlp not installed/configured): {e}")

    # Method 2: Bulletproof Fallback to premium copyright-free energetic upbeat Afrobeat audio
    print("⏳ Downloading high-tempo copyright-free Afrobeat track for background audio...")
    fallback_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(fallback_url, headers=headers, stream=True, timeout=30)
        if res.status_code == 200:
            with open(output_mp3_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
            print("✅ Successfully fetched fallback high-energy background audio!")
            return True
    except Exception as fallback_err:
        print(f"❌ Failed to obtain fallback audio track: {fallback_err}")

    return False


def merge_audio_video(silent_video_path, audio_path, output_path):
    """
    Invokes ffmpeg as a lightweight subprocess to merge the compiled
    OpenCV video track with the fetched background music.
    """
    print("🎬 Merging generated Kinetic Visuals with trending audio using ffmpeg...")
    try:
        import subprocess
        cmd = [
            "ffmpeg", "-y",
            "-i", silent_video_path,
            "-i", audio_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("✅ Audios blended flawlessly with Kinematics!")
        return True
    except Exception as e:
        print(f"⚠️ ffmpeg merging bypassed or not installed on server: {e}")
        # Graceful degradation fallback: copy silent video to target output path directly
        try:
            import shutil
            shutil.copyfile(silent_video_path, output_path)
            print("⚠️ Proceeding with clean silent video to avoid execution crashes.")
            return True
        except Exception as copy_err:
            print(f"❌ Critical copy fallback error: {copy_err}")
            return False


def compile_reels_video_file(reels_dict, output_path="temp_reel.mp4"):
    print(f"Compiling Kinetic Video Reel locally (100% Free) for: {reels_dict['title']}")
    if not REELS_LIBS_AVAILABLE:
        print("Required libs for REELS (opencv-python, numpy) are missing. Install them to enable reel compilation.")
        return None
    width, height = 1080, 1920
    fps = 24

    scenes = [
        {"text": reels_dict["hook"], "duration": 4, "text_color": (239, 68, 68)},  # Crimson Hook
        {"text": reels_dict["body"], "duration": 21, "text_color": (255, 255, 255)},  # Editorial White
        {"text": reels_dict["cta"], "duration": 5, "text_color": (56, 189, 248)}  # Sky Blue Callout
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
            try:
                bbox = font.getbbox(test_line);
                w = bbox[2] - bbox[0]
            except AttributeError:
                w = font.getsize(test_line)[0] if hasattr(font, 'getsize') else 500

            if w <= max_w:
                current.append(word)
            else:
                lines.append(' '.join(current))
                current = [word]
        if current: lines.append(' '.join(current))
        return lines

    # Write visual-only output to a silent video container first
    silent_temp_video = "temp_silent_reel.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(silent_temp_video, fourcc, fps, (width, height))

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
            draw.text((width // 2, 140), "SASAFRIK SOFTWARE CONSULTANCY", fill=(148, 163, 184), font=font_brand,
                      anchor="mm")
            try:
                title_text = reels_dict.get("title", "")
                if title_text:
                    draw.text((width // 2, 200), title_text, fill=(236, 240, 241), font=font_brand, anchor="mm")
            except Exception:
                pass
            draw.text((width // 2, height - 140), "💬 wa.me/254720000803 | hello@sasafrik.com", fill=(148, 163, 184),
                      font=font_brand, anchor="mm")

            y_cursor = y_cursor_start
            for line in wrapped:
                for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3)]:
                    draw.text((width // 2 + dx, y_cursor + dy), line, fill=(0, 0, 0, 255), font=font_main, anchor="mm")
                draw.text((width // 2, y_cursor), line, fill=scene["text_color"], font=font_main, anchor="mm")
                y_cursor += line_height

            opencv_frame = cv2.cvtColor(np.array(frame_canvas), cv2.COLOR_RGB2BGR)
            video_writer.write(opencv_frame)

    video_writer.release()

    # --- Fetch Trending Audio & Merge ---
    temp_background_song = "temp_background_song.mp3"
    trending_song_query = "Bien x Alikiba Finale Official Audio"

    audio_fetched = fetch_trending_song_audio(trending_song_query, temp_background_song)

    if audio_fetched and os.path.exists(temp_background_song):
        merge_audio_video(silent_temp_video, temp_background_song, output_path)
    else:
        import shutil
        shutil.copyfile(silent_temp_video, output_path)
        print("⚠️ Directing clean silent video output container to endpoint.")

    # Cleanup temporary local asset files
    for temp_file in [silent_temp_video, temp_background_song]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

    return output_path


def upload_reel_to_facebook_page(video_path, description):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN.startswith(
            "YOUR_") or "YOUR_FACEBOOK" in FACEBOOK_ACCESS_TOKEN:
        print("Facebook credentials missing or default. Skipping live Reels upload step.")
        return None

    print("Publishing video container directly to Facebook Reels ecosystem...")
    init_url = f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/video_reels"

    try:
        init_res = requests.post(init_url, data={"upload_phase": "START", "access_token": FACEBOOK_ACCESS_TOKEN},
                                 timeout=20)
        init_data = init_res.json()
        video_id = init_data.get("video_id") or init_data.get("id")
        upload_url = init_data.get("upload_url")

        if not upload_url:
            print(f"Resumable init did not return upload_url. Falling back to direct multipart upload.")
            with open(video_path, "rb") as f:
                files = {"source": f}
                data = {"description": description, "access_token": FACEBOOK_ACCESS_TOKEN}
                direct_res = requests.post(f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/videos", files=files,
                                           data=data, timeout=120)
                if direct_res.status_code in [200, 201]:
                    print("Direct multipart upload succeeded.")
                    return direct_res.json().get("id") or direct_res.json().get("post_id")
                else:
                    print(f"Direct multipart upload failed: {direct_res.status_code} {direct_res.text}")
                    return None

        with open(video_path, "rb") as f_file:
            video_binary = f_file.read()

        headers = {"Authorization": f"OAuth {FACEBOOK_ACCESS_TOKEN}", "offset": "0",
                   "file_size": str(len(video_binary))}
        upload_res = requests.post(upload_url, data=video_binary, headers=headers, timeout=60)
        if upload_res.status_code != 200:
            print(f"Reels payload chunk rejected: {upload_res.text}")
            return None

        finish_payload = {"upload_phase": "FINISH", "video_id": video_id, "video_state": "PUBLISHED",
                          "description": description, "access_token": FACEBOOK_ACCESS_TOKEN}
        finish_res = requests.post(f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/video_reels",
                                   data=finish_payload, timeout=20)

        if finish_res.status_code == 200:
            return video_id
        return None

    except Exception as e:
        print(f"Reels upload exception: {e}")
        return None


def call_flux_api_and_save(flux_prompt, filename="temp_flux_raw.jpg"):
    safe_prompt = urllib.parse.quote(flux_prompt)
    target_url = f"{FLUX_BASE_URL}{safe_prompt}?width=1024&height=1024&model=flux&seed={random.randint(1, 9999999)}"
    try:
        print(f"Calling FLUX API: {target_url}")
        res = requests.get(target_url, timeout=45)
        if res.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(res.content)
            return filename
        else:
            print(f"Flux API returned status {res.status_code}: {res.text}")
            if os.path.exists(LOGO_ASSET_PATH):
                try:
                    from shutil import copyfile
                    copyfile(LOGO_ASSET_PATH, filename)
                    print(f"Using local logo fallback for image: {LOGO_ASSET_PATH}")
                    return filename
                except Exception:
                    pass
            return None
    except Exception:
        return None


def build_flyer_copy(topic, post_caption=None):
    combined = f"{topic} {post_caption or ''}".lower()
    headline = "Custom software built for real business results."
    if any(word in combined for word in ("cloud", "uptime", "security", "infra", "server", "finops", "disaster")):
        headline = "Reliable digital systems that stay ready."
    elif any(word in combined for word in ("mobile", "app", "ux", "user", "portal", "mvp", "aesthetics")):
        headline = "Digital products people actually use."
    elif any(word in combined for word in
             ("automation", "workflow", "process", "email", "invoice", "parsing", "manual")):
        headline = "Automation that removes daily manual work."
    elif any(word in combined for word in ("marketing", "retarget", "content", "funnel", "churn")):
        headline = "Marketing systems that drive growth."
    elif any(word in combined for word in
             ("payment", "mpesa", "ledger", "wallet", "integration", "banking", "ussd", "localization")):
        headline = "Connected operations across every channel."

    service_sets = [
        ("web", [
            "Web platforms and portals",
            "Enterprise API integrations",
            "High-scale mobile apps",
            "Full-stack applications",
        ]),
        ("automation", [
            "Workflow automation engines",
            "Process dashboards",
            "Operational reporting",
            "Custom conversational bots",
        ]),
        ("cloud", [
            "Cloud architecture",
            "Security hardening",
            "Zero-downtime operations",
            "Scalable infrastructure",
        ]),
        ("payments", [
            "Payment integrations",
            "Ledgers and reconciliation",
            "Business system sync",
            "Transaction visibility",
        ]),
        ("marketing", [
            "Content systems",
            "Funnels and retargeting",
            "Campaign automation",
            "Lead capture",
        ]),
    ]

    benefits = []
    for keywords, items in service_sets:
        if any(k in combined for k in keywords):
            benefits.extend(items)
    if not benefits:
        benefits = service_sets[0][1]

    benefits = benefits[:4]
    subhead = "A leading ICT partner helping businesses build reliable digital systems that scale."
    if post_caption:
        post_bits = sanitize_generated_copy(post_caption)
        if post_bits:
            subhead = post_bits

    return headline, subhead, benefits


def _load_font(size, bold=False):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _text_size(font, text):
    try:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        try:
            return font.getsize(text)
        except Exception:
            return (len(text) * 10, 20)


def _wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        test_line = " ".join(current + [word]) if current else word
        if _text_size(font, test_line)[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [text]


def _draw_wrapped_text(draw, text, font, fill, x, y, max_width, line_gap=8):
    for line in _wrap_text(text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += _text_size(font, line)[1] + line_gap
    return y


def _draw_fit_text(draw, text, fill, x, y, max_width, max_size, min_size=22, bold=True, line_gap=5):
    size = max_size
    while size >= min_size:
        font = _load_font(size, bold)
        lines = _wrap_text(text, font, max_width)
        if max(_text_size(font, line)[0] for line in lines) <= max_width:
            for line in lines:
                draw.text((x, y), line, font=font, fill=fill)
                y += _text_size(font, line)[1] + line_gap
            return y
        size -= 2
    font = _load_font(min_size, bold)
    return _draw_wrapped_text(draw, text, font, fill, x, y, max_width, line_gap=line_gap)


def _rounded_rect_with_shadow(base, rect, fill, outline, radius=24, shadow_alpha=38, shadow_blur=16,
                              shadow_offset=(0, 8), outline_width=2):
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = rect
    ox, oy = shadow_offset
    sd.rounded_rectangle([x1 + ox, y1 + oy, x2 + ox, y2 + oy], radius=radius, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    base.alpha_composite(shadow)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=outline_width)


def composite_masterpiece(base_image_path, logo_path=LOGO_ASSET_PATH, output_filename="masterpiece_final.jpg",
                          topic=None, post_caption=None):
    try:
        base = Image.open(base_image_path).convert("RGBA")
        base_w, base_h = base.size
        overlay_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay_layer)
        logo_bottom_y = int(base_h * 0.05)

        # [ANTI-DETECTION] Dynamic Positioning Randomization
        side_choice = random.choice(["LEFT", "RIGHT"])
        if side_choice == "LEFT":
            card_x1 = int(base_w * 0.05)
            logo_x = int(base_w * 0.05)
        else:
            card_x1 = int(base_w * 0.45)
            logo_x = int(base_w * 0.45)

        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo_w, logo_h = logo.size
            target_w = int(base_w * 0.24)
            target_h = int(logo_h * (target_w / logo_w))
            logo_scaled = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            base.alpha_composite(logo_scaled, (logo_x, int(base_w * 0.05)))
            logo_bottom_y = int(base_w * 0.05) + target_h

        try:
            font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.026))
            font_body = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.021))
            font_footer = ImageFont.truetype("DejaVuSans-Bold.ttf", int(base_h * 0.020))
        except Exception:
            font_title = font_body = font_footer = ImageFont.load_default()

        flyer_topic = topic or "Custom software built for real business results."
        headline, subhead, capabilities = build_flyer_copy(flyer_topic, post_caption)

        card_w, card_h = int(base_w * 0.50), int(base_h * 0.44)
        card_y1 = logo_bottom_y + int(base_h * 0.03)
        draw_overlay.rounded_rectangle([card_x1, card_y1, card_x1 + card_w, card_y1 + card_h], radius=16,
                                       fill=(10, 15, 30, 180), outline=(255, 255, 255, 45), width=2)

        def draw_high_contrast_text(draw_obj, position, text_str, text_color, font_obj):
            x, y = position
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                draw_obj.text((x + dx, y + dy), text_str, fill=(0, 0, 0, 255), font=font_obj)
            draw_obj.text((x, y), text_str, fill=text_color, font=font_obj)

        draw_high_contrast_text(draw_overlay, (card_x1 + int(card_w * 0.06), card_y1 + int(card_h * 0.08)),
                                "WE DESIGN & DEVELOP", (56, 189, 248, 255), font_title)
        draw_high_contrast_text(draw_overlay, (card_x1 + int(card_w * 0.06), card_y1 + int(card_h * 0.16)),
                                headline, (255, 255, 255, 255), font_body)

        wrapped_subhead = textwrap.wrap(subhead, width=30)
        y_sub = card_y1 + int(card_h * 0.24)
        for line in wrapped_subhead[:3]:
            draw_high_contrast_text(draw_overlay, (card_x1 + int(card_w * 0.06), y_sub),
                                    line, (220, 228, 239, 255), font_footer)
            y_sub += int(card_h * 0.06)

        y_cursor = card_y1 + int(card_h * 0.40)
        for item in capabilities[:4]:
            draw_high_contrast_text(draw_overlay, (card_x1 + int(card_w * 0.06), y_cursor),
                                    f"• {item}", (255, 255, 255, 255), font_body)
            y_cursor += int(card_h * 0.12)

        banner_w, banner_h = int(base_w * 0.74), int(base_h * 0.095)
        banner_x1, banner_y1 = int((base_w - banner_w) / 2), int(base_h - banner_h - int(base_h * 0.04))
        draw_overlay.rounded_rectangle([banner_x1, banner_y1, banner_x1 + banner_w, banner_y1 + banner_h], radius=12,
                                       fill=(10, 15, 30, 245), outline=(56, 189, 248, 120), width=2)

        f1 = "📞 Call: +254 720 000 803"
        f2 = "🌐 sasafrik.com  |  ✉️ hello@sasafrik.com"
        draw_high_contrast_text(draw_overlay, (banner_x1 + 40, banner_y1 + int(banner_h * 0.18)), f1,
                                (255, 255, 255, 255), font_footer)
        draw_high_contrast_text(draw_overlay, (banner_x1 + 40, banner_y1 + int(banner_h * 0.54)), f2,
                                (255, 255, 255, 255), font_footer)

        intermediary_composite = Image.alpha_composite(base, overlay_layer)
        sanitized_canvas = Image.new("RGB", intermediary_composite.size)
        sanitized_canvas.paste(intermediary_composite)

        sanitized_canvas.save(output_filename, "JPEG", quality=98)
        return output_filename
    except Exception as e:
        print(f"Error compositing standard image graphic layout: {e}")
        return None


def post_image_to_facebook_page(image_path, message):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN.startswith(
            "YOUR_") or "YOUR_FACEBOOK" in FACEBOOK_ACCESS_TOKEN:
        print("Facebook credentials missing or default. Skipping image post to Facebook.")
        return None

    photo_url = f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/photos"
    feed_url = f"https://graph.facebook.com/v24.0/{FACEBOOK_PAGE_ID}/feed"

    try:
        with open(image_path, "rb") as img_file:
            res = requests.post(
                photo_url,
                data={"caption": message, "access_token": FACEBOOK_ACCESS_TOKEN, "published": "true"},
                files={"source": img_file},
                timeout=25,
            )
        if res.status_code in [200, 201]:
            try:
                return res.json().get("post_id") or res.json().get("id")
            except Exception:
                pass

        print(f"Facebook photo post failed with status {res.status_code}: {res.text}")
        feed_res = requests.post(
            feed_url,
            data={"message": message, "access_token": FACEBOOK_ACCESS_TOKEN, "published": "true"},
            timeout=25,
        )
        if feed_res.status_code in [200, 201]:
            try:
                return feed_res.json().get("id") or feed_res.json().get("post_id")
            except Exception:
                pass
        print(f"Facebook feed post failed with status {feed_res.status_code}: {feed_res.text}")
        return None
    except Exception as e:
        print(f"Facebook post exception: {e}")
        return None


def post_comment_to_facebook_post(post_id, comment_text):
    if not post_id:
        print("No Facebook node ID provided. Skipping comment execution sequence.")
        return False
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN.startswith(
            "YOUR_") or "YOUR_FACEBOOK" in FACEBOOK_ACCESS_TOKEN:
        print("Facebook credentials missing or default. Skipping comment post to Facebook.")
        return False

    comment_url = f"https://graph.facebook.com/v24.0/{post_id}/comments"
    try:
        res = requests.post(
            comment_url,
            data={"message": comment_text, "access_token": FACEBOOK_ACCESS_TOKEN},
            timeout=25,
        )
        if res.status_code in [200, 201]:
            return True
        print(f"Facebook comment layer rejected payload: {res.status_code} - {res.text}")
        return False
    except Exception as e:
        print(f"Facebook comment exception: {e}")
        return False


def post_image_to_twitter(image_path, message):
    if PAUSE_TWITTER == 'true':
        print("Twitter posting is currently paused via PAUSE_TWITTER. Skipping Twitter upload.")
        return False
    if not TWITTER_LIB_AVAILABLE:
        print("Twitter client library 'requests_oauthlib' is not installed. Skipping Twitter upload.")
        return False
    if not TWITTER_API_KEY or "YOUR_TWITTER" in TWITTER_API_KEY:
        print("Twitter API credentials missing or default. Skipping Twitter upload.")
        return False
    try:
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        with open(image_path, "rb") as img_file:
            upload_res = requests.post(upload_url, auth=auth, data={'media_category': 'tweet_image'},
                                       files=[('media', (os.path.basename(image_path), img_file, 'image/jpeg'))],
                                       timeout=25)
        media_id = upload_res.json().get("media_id_string")
        if not media_id: return False
        oauth = OAuth1Session(TWITTER_API_KEY, client_secret=TWITTER_API_SECRET,
                              resource_owner_key=TWITTER_ACCESS_TOKEN,
                              resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET)
        res = oauth.post("https://api.twitter.com/2/tweets",
                         json={"text": message, "media": {"media_ids": [str(media_id)]}}, timeout=20)
        return res.status_code in [200, 201]
    except Exception:
        return False


def generate_content_with_retry(prompt, max_retries=3):
    """
    Intelligent exponential backoff helper that catches rate limits (429),
    dynamically parses the requested cooldown delay if returned by Gemini,
    and retries the API sequence safely.
    """
    if not model:
        print("❌ Gemini model reference missing. Retrying aborted.")
        return None

    for attempt in range(1, max_retries + 1):
        try:
            response_wrapper = model.generate_content(prompt)
            return response_wrapper.text.strip()
        except Exception as e:
            err_msg = str(e)
            print(f"⚠️ Gemini API execution failed [Attempt {attempt}/{max_retries}]: {err_msg}")

            # Identify rate limiting or quota exhaustion conditions
            if "429" in err_msg or "quota" in err_msg.lower():
                # Attempt to extract precise API retry time frames
                retry_match = re.search(r"retry in ([\d\.]+)\s*s", err_msg, re.IGNORECASE)
                seconds_match = re.search(r"seconds:\s*(\d+)", err_msg, re.IGNORECASE)

                sleep_time = 60  # Safe default sleep if unparsed
                if retry_match:
                    sleep_time = int(float(retry_match.group(1))) + 3
                elif seconds_match:
                    sleep_time = int(seconds_match.group(1)) + 3

                # Limit safety bounds
                sleep_time = max(5, min(sleep_time, 120))

                if attempt < max_retries:
                    print(
                        f"⏳ Spike rate limit hit. Pausing execution track for {sleep_time}s before automatic retry...")
                    time.sleep(sleep_time)
                else:
                    print("❌ Max retry limit reached. Safely raising exception to guardrail engine.")
                    raise e
            else:
                # Basic non-quota failures backoff
                if attempt < max_retries:
                    time.sleep(5)
                else:
                    raise e
    return None


def generate_all_ai_assets(topic):
    """
    Consolidates AI text generation into exactly one single prompt request
    to drop daily Free Tier Gemini API call consumption by up to 75%.
    """
    if not model:
        print("❌ Gemini model reference missing. Cannot proceed with consolidated generation.")
        return None

    prompt = f"""
You are an elite senior corporate copywriter and art director for SasAfrik, a premium technology consulting firm in Nairobi, Kenya.
Analyze this technical/business topic context: "{topic}"

Generate a valid JSON object containing exactly these four keys. Do not return any other text or markdown wrappers, only the raw JSON.

1. "facebook_body": A professional, high-impact Facebook post (400-600 characters). Explain the business pain-point, the SasAfrik technical solution, and real enterprise ROI. Use 2-3 structured paragraph breaks and 2-3 relevant emojis natively for structural layout. Do not include CTAs, hashtags, or WhatsApp references.
2. "twitter_body": A punchy tweet (max 220 characters) featuring "sasafrik.com". No hashtags.
3. "flux_prompt": A hyper-realistic, human-centric image generation prompt (max 45 words) reflecting corporate commercial photography in Nairobi. No floating holographic elements or artificial neon tracks.
4. "facebook_comment": A detailed conversational engagement comment (200-350 characters) expanding on the topic from a tactical angle. End with a sharp, open-ended question using 1-2 emojis (e.g. 💡, 👇) to pull CEOs, tech leaders, or managers into the replies.

Strict JSON Output format schema:
{{
  "facebook_body": "string",
  "twitter_body": "string",
  "flux_prompt": "string",
  "facebook_comment": "string"
}}
"""
    try:
        response_text = generate_content_with_retry(prompt)
        if not response_text:
            return None

        # Strip markdown syntax markers if model inserts them
        if response_text.startswith("```"):
            response_text = re.sub(r"^```(?:json)?\n|```$", "", response_text, flags=re.MULTILINE)

        data = json.loads(response_text)

        fb_copy = sanitize_generated_copy(data.get("facebook_body", ""))
        x_copy = sanitize_generated_copy(data.get("twitter_body", ""))
        comment_copy = sanitize_generated_copy(data.get("facebook_comment", ""))
        flux_p = data.get("flux_prompt", "").strip()

        # [GUARDRAIL CHECK] Ensure no empty values or silent fallback content is passed
        if not fb_copy or not x_copy or not comment_copy or not flux_p:
            print("❌ Guardrail Exception: Gemini returned incomplete metadata assets.")
            return None

        return {
            "facebook": fb_copy,
            "twitter": x_copy,
            "comment": comment_copy,
            "flux": flux_p
        }
    except Exception as e:
        print(f"❌ Gemini Exception encountered inside consolidated post assets builder: {e}")
        return None


def generate_facebook_comment(topic, post_caption):
    """Fallback comment generator used strictly for independent Reels pipeline engagement comments."""
    if not model:
        print("❌ Gemini model initialization check failed. Cannot build independent Reel comment.")
        return None

    prompt = f"""
You are writing an interactive, high-engagement Facebook comment on behalf of SasAfrik to pin under our latest video Reel.
Context Topic: {topic}
Video Caption/Post: {post_caption}

Write a highly creative, detailed comment (200-350 characters) that expands the conversation.
Guidelines:
- Do not repeat the post caption. Add a fresh tactical angle, implementation tip, or engineering reality check.
- Use 1-2 conversational emojis naturally (e.g., 💡, 👇, 🤔).
- End with a sharp, open-ended question that directly encourages tech leaders, managers, or CEOs to share their own experiences, challenges, or opinions in the replies.
- Do not use generic sales jargon or formal CTA links.
- Output ONLY the comment text. Do not wrap in quotes.
"""
    try:
        comment = generate_content_with_retry(prompt)
        if not comment:
            return None
        comment = sanitize_generated_copy(" ".join(comment.split()))
        if len(comment) > 400:
            comment = comment[:397].rsplit(" ", 1)[0] + "..."
        return comment
    except Exception as gemini_err:
        print(f"❌ Gemini error while building independent Reels comment: {gemini_err}")
        return None


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
    summary = {"mode": "REELS", "day": target_reel.get("day"), "title": target_reel.get("title"),
               "facebook_upload": False, "facebook_comment_posted": False, "facebook_comment_text": None, "error": None}
    try:
        compiled_video = compile_reels_video_file(target_reel, video_output)
        if not compiled_video or not os.path.exists(compiled_video):
            summary["error"] = "video_compile_failed"
            print("Video compiler failed to output video binary stream object.")
            return

        description = f"🔥 {target_reel['hook']}\n\n{target_reel['body']}\n\n🚀 Partner with SasAfrik to transform your digital ecosystem. Learn more at sasafrik.com."
        reel_id = upload_reel_to_facebook_page(compiled_video, description)

        if reel_id:
            processed.append(target_reel["day"])
            save_processed_items(PROCESSED_REELS_FILE, processed)
            summary["facebook_upload"] = True
            print(f"Successfully tracked Day {target_reel['day']} inside production databases. Video Node: {reel_id}")

            # [ENGAGEMENT] Generate and pin a creative contextual follow-up comment directly to the newly posted video reel
            reel_topic_context = f"Reel Day {target_reel['day']} - {target_reel['title']}: {target_reel['hook']} {target_reel['body']}"
            fb_comment = generate_facebook_comment(reel_topic_context, description)
            if fb_comment:
                comment_status = post_comment_to_facebook_post(reel_id, fb_comment)
                if comment_status:
                    summary["facebook_comment_posted"] = True
                    summary["facebook_comment_text"] = fb_comment
                    print("✅ Pinned engagement conversational follow-up comment to the newly published Reel thread.")
                else:
                    print("❌ Graph API rejected posting comment under newly published Reel container.")
            else:
                print("❌ Skipped Reel comment: Gemini failed to generate comment content safely.")

    except Exception as e:
        summary["error"] = str(e)
        print(f"❌ Exception in Reels Pipeline: {e}")
    finally:
        try:
            with open("last_run_summary.json", "w", encoding="utf-8") as sf:
                json.dump(summary, sf, indent=2, ensure_ascii=False)
        except Exception:
            pass
        if os.path.exists(video_output):
            try:
                os.remove(video_output)
            except Exception:
                pass
    print("=== Reels Automation Segment Finished ===")


def execute_standard_post_pipeline():
    print(f"=== Starting Post Automation Track: {time.ctime()} ===")
    processed = set(load_processed_items(PROCESSED_FILE))

    # Map the master REELS_PROMPTS bank directly into keys for standard image post generation matching
    topic_map = {
        f"Reel Day {item['day']} - {item['title']}: {item['hook']} {item['body']}": item
        for item in REELS_PROMPTS
    }
    available = [t for t in topic_map if t not in processed]

    if not available:
        print("All predefined post topics processed. Flushing manifest to restart loop...")
        save_processed_items(PROCESSED_FILE, [])
        available = list(topic_map.keys())

    selected_topic = random.choice(available)
    print(f"🎯 Selected Topic for this pass: {selected_topic}")
    raw_canvas, final_canvas = "temp_flux_raw.jpg", "masterpiece_final.jpg"

    summary = {
        "mode": "STANDARD_POST",
        "topic": selected_topic,
        "facebook_posted": False,
        "facebook_comment_posted": False,
        "facebook_comment_text": None,
        "twitter_posted": False,
        "twitter_paused": (PAUSE_TWITTER == 'true'),
        "error": None,
    }
    try:
        # [QUOTA REDUCTION] Call Gemini exactly once to get all metadata, text captions, prompts, and comments
        assets = generate_all_ai_assets(selected_topic)
        if not assets:
            summary["error"] = "gemini_unified_generation_failed"
            print(
                "❌ Guardrail Triggered: Gemini failed to generate standard post content. Exiting pipeline loop safely.")
            return

        fb_text = assets["facebook"]
        x_text = assets["twitter"]
        optimized_prompt = assets["flux"]
        fb_comment = assets["comment"]

        if not call_flux_api_and_save(optimized_prompt, raw_canvas):
            summary["error"] = "flux_api_failed"
            return
        if not composite_masterpiece(raw_canvas, LOGO_ASSET_PATH, final_canvas, topic=selected_topic,
                                     post_caption=fb_text):
            summary["error"] = "composite_failed"
            return

        fb_post_id = post_image_to_facebook_page(final_canvas, fb_text)
        x_status = post_image_to_twitter(final_canvas, x_text)
        summary["facebook_posted"] = bool(fb_post_id)
        summary["twitter_posted"] = bool(x_status)

        if fb_post_id:
            comment_status = post_comment_to_facebook_post(fb_post_id, fb_comment)
            summary["facebook_comment_posted"] = bool(comment_status)
            summary["facebook_comment_text"] = fb_comment
            if comment_status:
                print("✅ Successfully established dynamic comment thread under Standard Facebook Post node.")

        if fb_post_id or x_status:
            processed.add(selected_topic)
            save_processed_items(PROCESSED_FILE, list(processed))
            print("Standard post marked successfully in local history.")

    except Exception as e:
        summary["error"] = str(e)
        print(f"❌ Exception during Standard Post Pipeline: {e}")
    finally:
        try:
            with open("last_run_summary.json", "w", encoding="utf-8") as sf:
                json.dump(summary, sf, indent=2, ensure_ascii=False)
        except Exception:
            pass
        for path in [raw_canvas, final_canvas]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
    print("=== Post Automation Segment Finished ===")


# [ANTI-DETECTION] Human-like Execution Jitter Setup
def apply_execution_jitter(min_mins=5, max_mins=45):
    """Introduces a randomized sleep cycle right before execution loops trigger."""
    jitter_seconds = random.randint(min_mins * 60, max_mins * 60)
    print(f"🕒 [Anti-Detection] Injecting {jitter_seconds // 60} minutes of random timing jitter...")
    time.sleep(jitter_seconds)


if __name__ == "__main__":
    apply_execution_jitter(5, 45)

    mode = os.getenv("EXECUTION_MODE", "STANDARD_POST").upper()
    if mode == "REELS":
        execute_reels_pipeline()
    else:
        execute_standard_post_pipeline()