#Hacktoberfest Project "

import html
import io
import json
import os
import re

import ollama
import streamlit as st
from PIL import Image

MODEL = "gemma3:4b"  # local multimodal open-weight model, runs through Ollama
GEMMA4_API = "gemma-4-26b-a4b-it"  # Gemma 4 served through the Gemini API
BACKENDS = ["Gemma 4 (Gemini API)", "Local: Gemma 3 via Ollama"]

CATEGORIES = {
    "Wet": ("#15803D", "#DCFCE7", "🍌"),
    "Dry": ("#1D4ED8", "#DBEAFE", "📦"),
    "Hazardous": ("#B91C1C", "#FEE2E2", "☣️"),
    "E-waste": ("#6D28D9", "#EDE9FE", "🔌"),
    "Sanitary": ("#BE185D", "#FCE7F3", "🧻"),
    "Other": ("#4B5563", "#F3F4F6", "🗑️"),
}

PROMPT = """You are a waste management expert for Indian cities.
Look at the photo and identify every distinct waste item visible (maximum 5).
Classify each item into exactly one category:
- Wet: food scraps, peels, garden waste (organic, compostable)
- Dry: paper, cardboard, plastic, metal, glass, cloth
- Hazardous: batteries, paint, chemicals, medicines, bulbs, aerosols, pesticides
- E-waste: phones, chargers, cables, electronics, appliances
- Sanitary: diapers, sanitary pads, masks, used bandages
- Other: anything that does not fit above
Return ONLY valid JSON in exactly this format:
{"items": [{"name": "Plastic water bottle", "category": "Dry", "material": "PET plastic",
"recyclable": true, "single_use_plastic": true, "hazardous": false,
"disposal": "One or two clear sentences on how to dispose of it correctly.",
"tip": "One short tip to reuse or reduce this kind of waste.",
"confidence": "high"}]}
confidence must be low, medium or high. If no waste item is visible, return {"items": []}."""


def prepare(raw):
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((896, 896))  # smaller image = faster analysis on a laptop CPU
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return img, buf.getvalue()


def run_gemma4(img_bytes, api_key):
    if not api_key:
        raise ValueError("Please enter your Gemini API key in the sidebar.")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=GEMMA4_API,
        contents=[types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"), PROMPT],
    )
    return resp.text or ""


def run_local(img_bytes):
    reply = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT, "images": [img_bytes]}],
        format="json",
        options={"temperature": 0.2},
    )
    return reply["message"]["content"]


def analyze(img_bytes, backend, api_key):
    text = run_gemma4(img_bytes, api_key) if backend == BACKENDS[0] else run_local(img_bytes)
    match = re.search(r"\{.*\}", text, re.S)  # tolerate extra text or code fences around the JSON
    data = json.loads(match.group(0)) if match else {"items": []}
    items = data.get("items", []) if isinstance(data, dict) else data
    return [i for i in items if isinstance(i, dict)]


def yes(v):
    return v is True or str(v).strip().lower() in ("true", "yes")


def esc(v):
    return html.escape(str(v or "-"))


def card(it):
    cat = it.get("category", "Other")
    if cat not in CATEGORIES:
        cat = "Other"
    color, bg, icon = CATEGORIES[cat]
    risky = yes(it.get("hazardous")) or cat in ("Hazardous", "E-waste")
    badges = [
        f'<span class="badge" style="background:{"#DCFCE7" if yes(it.get("recyclable")) else "#FEE2E2"}">'
        f'{"♻️ Recyclable" if yes(it.get("recyclable")) else "🚫 Not recyclable"}</span>'
    ]
    if yes(it.get("single_use_plastic")):
        badges.append('<span class="badge" style="background:#FEF3C7">⚠️ Single-use plastic</span>')
    if risky:
        badges.append('<span class="badge" style="background:#FECACA">☣️ Special handling</span>')
    warn = ('<div class="warn">Do NOT mix with regular household waste. '
            'Hand it over at an authorised collection point.</div>') if risky else ""
    return f"""
<div class="item" style="border-left:10px solid {color}; background:{bg}">
  <div class="title">{icon} {esc(it.get("name"))}</div>
  <div class="cat" style="color:{color}">{cat.upper()} WASTE &nbsp;|&nbsp; {esc(it.get("material"))}
  &nbsp;|&nbsp; Confidence: {esc(it.get("confidence"))}</div>
  <div class="badges">{"".join(badges)}</div>
  <p><b>How to dispose:</b> {esc(it.get("disposal"))}</p>
  <p><b>Tip:</b> {esc(it.get("tip"))}</p>
  {warn}
</div>"""


st.set_page_config(page_title="WasteWise AI", page_icon="♻️", layout="wide")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #F0FDF4 0%, #FEFCE8 100%); }
.stApp, .stApp p, .stApp label, .stApp li, .stApp span, .stApp h1, .stApp h2, .stApp h3,
[data-testid="stWidgetLabel"] p { color: #111111 !important; }
header[data-testid="stHeader"] { background: transparent; }
.hero { background: linear-gradient(120deg, #16A34A, #65A30D 60%, #FACC15); padding: 26px 32px;
  border-radius: 18px; margin-bottom: 18px; box-shadow: 0 8px 22px rgba(0,0,0,0.15); }
.hero h1 { margin: 0; color: #111111 !important; font-size: 2.2rem; font-weight: 800; }
.hero p { margin: 6px 0 0 0; color: #111111 !important; font-size: 1.05rem; }
.stat { background: #FFFFFF; border-radius: 14px; padding: 14px 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat .l { font-size: 0.78rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
.stat .v { font-size: 1.8rem; font-weight: 800; }
.item { border-radius: 14px; padding: 16px 22px; margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.12); color: #111111; }
.item .title { font-size: 1.25rem; font-weight: 800; }
.item .cat { font-size: 0.8rem; font-weight: 800; letter-spacing: 1px; margin: 2px 0 8px 0; }
.badge { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 0.82rem; font-weight: 700; margin: 0 6px 8px 0; color: #111111; }
.item p { margin: 4px 0; color: #111111 !important; }
.warn { background: #B91C1C; color: #FFFFFF; border-radius: 10px; padding: 10px 14px; margin-top: 8px; font-weight: 700; }
.stButton > button { background: #FACC15; color: #111111 !important; border: 1px solid #CA8A04;
  border-radius: 10px; font-weight: 700; padding: 0.55rem 1.4rem; }
</style>
<div class="hero">
  <h1>♻️ WasteWise AI</h1>
  <p>Snap. Scan. Segregate. Take a photo of any waste and get an instant classification and disposal guide, powered by open-weight Gemma models.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("AI engine")
    backend = st.radio("Model", BACKENDS)
    api_key = ""
    if backend == BACKENDS[0]:
        api_key = st.text_input("Gemini API key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
        st.caption("Gemma 4 is an open-weight model served through the Gemini API.")
    else:
        st.caption("Runs fully on this device through Ollama. No internet needed.")

st.session_state.setdefault("scanned", 0)
st.session_state.setdefault("special", 0)

s1, s2, s3 = st.columns(3)
s1.markdown(f'<div class="stat"><div class="l">Items identified</div><div class="v">{st.session_state.scanned}</div></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="stat"><div class="l">Special-handling items caught</div><div class="v">{st.session_state.special}</div></div>', unsafe_allow_html=True)
engine_name = "Gemma 4" if backend == BACKENDS[0] else "Gemma 3 (local)"
s3.markdown(f'<div class="stat"><div class="l">AI engine</div><div class="v">{engine_name}</div></div>', unsafe_allow_html=True)
st.write("")

left, right = st.columns([1, 1.3])
with left:
    mode = st.radio("Input", ["Upload a photo", "Use camera"], horizontal=True)
    src = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp"]) if mode == "Upload a photo" \
        else st.camera_input("Take a photo of the waste")
    go = st.button("Analyse waste 🔍")

with right:
    if src is not None:
        img, img_bytes = prepare(src.getvalue())
        with left:
            st.image(img, width=360)
        if go:
            with st.spinner("Analysing the image... this can take up to a minute on a laptop."):
                try:
                    items = analyze(img_bytes, backend, api_key)
                except Exception as err:
                    items = None
                    st.error(f"Analysis failed: {err}")
            if items is not None:
                if not items:
                    st.warning("No waste item was detected. Try a clearer, closer photo.")
                for it in items:
                    st.markdown(card(it), unsafe_allow_html=True)
                st.session_state.scanned += len(items)
                st.session_state.special += sum(
                    1 for it in items
                    if yes(it.get("hazardous")) or it.get("category") in ("Hazardous", "E-waste"))
    else:
        st.info("Upload or capture a photo to begin.")

st.caption("Guidance is general. Always follow your local municipal waste rules.")




