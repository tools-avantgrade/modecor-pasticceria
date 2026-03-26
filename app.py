import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import base64
from openai import OpenAI
import json
from typing import List, Dict, Optional
import os

# -------------------------------------------------
# CONFIGURAZIONE
# -------------------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(
    page_title="Modecor AI Assistant",
    page_icon="🎂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CREDENZIALI API
# -------------------------------------------------
MODECOR_API_URL = "https://www.modecoritaliana.it/tools/api/it-get-products.php"
MODECOR_USERNAME = "modecorapis"
MODECOR_PASSWORD = "#M0d3CoR2025!"

OPENAI_API_KEY = None
try:
    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass
if not OPENAI_API_KEY:
    try:
        if "default" in st.secrets:
            OPENAI_API_KEY = st.secrets["default"]["OPENAI_API_KEY"]
    except Exception:
        pass
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@400;500;600;700&display=swap');
    
    :root {
        --modecor-red: #DC2626;
        --modecor-red-dark: #991B1B;
        --modecor-gold: #D4A853;
        --modecor-gold-light: #F5E6C8;
        --cream: #FFF8F0;
        --cream-dark: #EDE5DA;
        --charcoal: #1A1A1A;
        --warm-gray: #6B5E54;
        --soft-pink: #F9E8E8;
        --text-dark: #2D2420;
        --text-body: #4A403A;
    }
    
    /* ===== GLOBAL ===== */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--cream) !important;
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-dark) !important;
    }
    
    /* Centered narrow column */
    .main .block-container {
        max-width: 680px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        margin: 0 auto !important;
    }
    
    /* ===== ALL TEXT DARK ===== */
    p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown p, .stMarkdown span,
    [data-testid="stText"], [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li {
        color: var(--text-dark) !important;
    }
    
    /* ===== FILE UPLOADER - READABLE ===== */
    [data-testid="stFileUploader"] {
        margin: 1rem auto !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: white !important;
        border: 2px dashed var(--cream-dark) !important;
        border-radius: 14px !important;
        padding: 1rem !important;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--modecor-gold) !important;
        background: #FFFDF9 !important;
    }
    
    /* Force ALL text inside uploader to be dark */
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"],
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-body) !important;
    }
    
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stCaption"] {
        color: var(--warm-gray) !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: var(--cream) !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--cream-dark) !important;
        border-radius: 8px !important;
    }
    
    /* Uploaded file name chip */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        color: var(--text-dark) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] small {
        color: var(--text-body) !important;
    }
    
    /* ===== HEADER ===== */
    .app-header {
        text-align: center;
        padding: 2.5rem 0 0.5rem;
    }
    
    .header-decoration {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .header-line {
        width: 50px;
        height: 1px;
        background: var(--modecor-gold);
    }
    
    .header-dot {
        width: 6px;
        height: 6px;
        background: var(--modecor-red);
        border-radius: 50%;
    }
    
    .brand-name {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--charcoal) !important;
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    
    .brand-name em {
        color: var(--modecor-red) !important;
        font-style: normal;
    }
    
    .brand-tagline {
        font-size: 0.8rem;
        color: var(--warm-gray) !important;
        margin-top: 0.4rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        font-weight: 500;
    }
    
    /* ===== UPLOAD HERO ===== */
    .upload-hero {
        background: white;
        border: 2px dashed var(--modecor-gold);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin: 1.5rem auto;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 2px 16px rgba(212, 168, 83, 0.08);
    }
    
    .upload-hero:hover {
        border-color: var(--modecor-red);
        box-shadow: 0 4px 24px rgba(220, 38, 38, 0.08);
    }
    
    .upload-hero::before {
        content: '';
        position: absolute;
        top: -40px;
        right: -40px;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, var(--soft-pink) 0%, transparent 70%);
        opacity: 0.6;
    }
    
    .upload-hero::after {
        content: '';
        position: absolute;
        bottom: -30px;
        left: -30px;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, var(--modecor-gold-light) 0%, transparent 70%);
        opacity: 0.5;
    }
    
    .upload-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.4rem;
        animation: gentleFloat 4s ease-in-out infinite;
    }
    
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    
    .upload-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.35rem;
        color: var(--charcoal) !important;
        margin: 0.4rem 0;
        font-weight: 600;
    }
    
    .upload-subtitle {
        font-size: 0.85rem;
        color: var(--warm-gray) !important;
        margin: 0;
        line-height: 1.5;
    }
    
    /* ===== CAKE CARD ===== */
    .cake-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        margin: 1.2rem auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid var(--cream-dark);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .cake-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--modecor-gold), var(--modecor-red), var(--modecor-gold));
    }
    
    .cake-card-label {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.75rem;
        padding: 0.35rem 1rem;
        background: var(--cream);
        border-radius: 30px;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--warm-gray) !important;
        letter-spacing: 0.04em;
    }
    
    .ready-badge {
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5) !important;
        color: #065F46 !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--modecor-red) 0%, var(--modecor-red-dark) 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        font-family: 'DM Sans', sans-serif !important;
        letter-spacing: 0.02em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.2) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 8px 28px rgba(220, 38, 38, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Sidebar button = secondary style */
    [data-testid="stSidebar"] .stButton > button {
        background: white !important;
        color: var(--modecor-red) !important;
        border: 1.5px solid var(--modecor-red) !important;
        box-shadow: none !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1.5rem !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #FFF5F5 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    /* ===== CHAT MESSAGES ===== */
    [data-testid="stChatMessage"] {
        background: white !important;
        border: 1px solid var(--cream-dark) !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
        margin-bottom: 0.6rem !important;
    }
    
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] td,
    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessage"] div {
        color: var(--text-body) !important;
    }
    
    /* Chat input */
    [data-testid="stChatInput"] textarea {
        color: var(--text-dark) !important;
        font-family: 'DM Sans', sans-serif !important;
        background: white !important;
    }
    
    [data-testid="stChatInput"] {
        border-color: var(--cream-dark) !important;
    }
    
    /* ===== PHASE BADGE ===== */
    .phase-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: white;
        color: var(--warm-gray) !important;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.72rem;
        margin-bottom: 0.75rem;
        border: 1px solid var(--cream-dark);
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid var(--cream-dark) !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: var(--text-dark) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        max-height: 250px !important;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    [data-testid="stSidebar"] [data-testid="stCaption"],
    [data-testid="stSidebar"] .stCaption {
        color: var(--warm-gray) !important;
    }
    
    /* ===== DIVIDER ===== */
    .gold-divider {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        margin: 1.2rem 0;
    }
    .gold-divider .line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--modecor-gold), transparent);
    }
    .gold-divider .diamond {
        width: 5px;
        height: 5px;
        background: var(--modecor-gold);
        transform: rotate(45deg);
    }
    
    /* ===== GENERATE SECTION ===== */
    .generate-section {
        text-align: center;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        border-radius: 16px;
        border: 1px solid var(--cream-dark);
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .generate-section p {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.05rem !important;
        color: var(--charcoal) !important;
        margin-bottom: 0.3rem !important;
    }
    .generate-section .sub {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem !important;
        color: var(--warm-gray) !important;
    }
    
    /* ===== FINAL GUIDE ===== */
    .final-guide {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid var(--cream-dark);
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
    .final-guide h1 {
        font-family: 'Playfair Display', serif;
        color: var(--charcoal) !important;
        font-size: 1.7rem;
        font-weight: 700;
        border-bottom: 2px solid var(--modecor-gold);
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
    }
    .final-guide h2 {
        font-family: 'Playfair Display', serif;
        color: var(--modecor-red-dark) !important;
        font-size: 1.25rem;
        margin-top: 1.8rem;
        margin-bottom: 0.8rem;
        font-weight: 600;
    }
    .final-guide h3 {
        color: var(--charcoal) !important;
        font-size: 1rem;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .final-guide p, .final-guide li, .final-guide td {
        color: var(--text-body) !important;
        line-height: 1.75;
    }
    .final-guide table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.2rem 0;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .final-guide th {
        background: var(--charcoal) !important;
        color: white !important;
        padding: 0.8rem 0.9rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .final-guide td {
        padding: 0.7rem 0.9rem;
        border-bottom: 1px solid var(--cream-dark);
        font-size: 0.88rem;
    }
    .final-guide tr:nth-child(even) { background: var(--cream); }
    .final-guide tr:hover td { background: var(--modecor-gold-light); }
    .final-guide a { color: var(--modecor-red) !important; text-decoration: none; font-weight: 500; }
    .final-guide a:hover { text-decoration: underline; }
    .final-guide hr { border: none; border-top: 1px solid var(--cream-dark); margin: 1.8rem 0; }
    
    /* ===== FOOTER ===== */
    .app-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        color: var(--warm-gray) !important;
    }
    .app-footer a { color: var(--modecor-red) !important; text-decoration: none; }
    
    /* ===== MISC ===== */
    [data-testid="stMetric"] label { color: var(--text-dark) !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text-dark) !important; }
    .stCaption, [data-testid="stCaption"] { color: var(--warm-gray) !important; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--cream); }
    ::-webkit-scrollbar-thumb { background: var(--cream-dark); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--modecor-gold); }
    
    /* Responsive */
    @media (max-width: 768px) {
        .brand-name { font-size: 1.9rem; }
        .upload-hero { padding: 2rem 1.2rem; }
        .final-guide { padding: 1.2rem; }
        .final-guide h1 { font-size: 1.3rem; }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# STATO
# -------------------------------------------------
for key, default in [
    ("messages", []), ("cake_image", None), ("image_base64", None),
    ("products_catalog", None), ("products_index", {}),
    ("phase", "upload"), ("guide_generated", False), ("all_info_collected", False)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------------------------------------
# FUNZIONI API
# -------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_modecor_products():
    try:
        r = requests.get(MODECOR_API_URL, auth=HTTPBasicAuth(MODECOR_USERNAME, MODECOR_PASSWORD),
                         headers=HEADERS, timeout=60, verify=False)
        return json.loads(r.text) if r.status_code == 200 else None
    except Exception as e:
        print(f"Errore API: {e}")
        return None


def build_products_index(products):
    index = {}
    for prod in products:
        if not isinstance(prod, dict):
            continue
        title = prod.get("titolo", "").strip()
        if title:
            index[title.lower()] = {
                "titolo": title,
                "url": prod.get("url", ""),
                "sku": prod.get("sku", prod.get("codice", "")),
            }
    return index


def prepare_products_for_ai(products, max_products=1500):
    if not products:
        return "Nessun prodotto disponibile."
    catalog = "# CATALOGO UFFICIALE PRODOTTI MODECOR (FONTE VERIFICATA)\n"
    catalog += "# SOLO questi prodotti possono essere suggeriti.\n\n"
    for i, prod in enumerate(products[:max_products], 1):
        if not isinstance(prod, dict):
            continue
        title = prod.get("titolo", "").strip()
        url = prod.get("url", "").strip()
        sku = (prod.get("sku") or prod.get("codice") or "").strip()
        if not title:
            continue
        catalog += f"{i}. {title}"
        if sku:
            catalog += f" [SKU: {sku}]"
        catalog += f"\n   URL: {url}\n\n"
    return catalog

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
SYSTEM_RULES = """
## REGOLE INVIOLABILI

1. **VINCOLO CATALOGO**: Suggerisci ESCLUSIVAMENTE prodotti presenti nel catalogo ufficiale.
   NON inventare nomi di prodotti. NON immaginare varianti inesistenti.

2. **DIVIETO GENERAZIONE CODICI**: NON generare MAI codici prodotto/SKU.
   Usa solo quelli dal catalogo. Se mancano, mostra il prodotto senza codice.

3. **VALIDAZIONE**: Verifica che nome e URL corrispondano ESATTAMENTE al catalogo
   prima di mostrare qualsiasi prodotto. Se non sei certo, NON mostrarlo.

4. **BLOCCO COMPETITOR**: BRAND-LOCKED su Modecor. MAI suggerire altri brand.
   Se l'utente chiede di un competitor, proponi l'equivalente Modecor o rispondi in modo generico.

5. **LINGUA**: Rispondi nella lingua dell'utente.

6. **DISCLAIMER**: La procedura e' indicativa. La realizzazione spetta al pasticcere.
"""


def create_initial_analysis_prompt(products_catalog):
    return f"""Sei l'assistente AI ufficiale di Modecor per decorazioni da pasticceria.

{SYSTEM_RULES}

Analizza questa foto (max 100 parole): tipo di dolce, colori, decorazioni, stile, complessita'.
Poi chiedi: "Questa e' la torta che vuoi realizzare? Dimmi qualcosa in piu' e ti guido passo passo!"
NON suggerire prodotti ora.

{products_catalog}"""


def create_conversation_prompt(history, products_catalog):
    return f"""Sei l'assistente AI ufficiale di Modecor.

{SYSTEM_RULES}

Domande da fare (UNA alla volta):
1. Per quante persone? 2. Occasione? 3. Decorazioni: zucchero, cialda o cioccolato?
4. Colori specifici? 5. Gusto base? 6. Allergie?

UNA domanda alla volta. Breve e cordiale. NON suggerire prodotti.
Se l'utente chiede di altri brand, proponi Modecor.
Quando hai TUTTE le info, termina con: [INFO_COMPLETE]

CONVERSAZIONE:
{history}

CATALOGO (interno):
{products_catalog}"""


def create_final_output_prompt(summary, products_catalog):
    return f"""Genera guida completa per la torta.

{SYSTEM_RULES}

REGOLE GUIDA:
- SOLO prodotti ESATTAMENTE nel catalogo. Nome e URL ESATTI.
- SKU solo se dal catalogo. Mai inventare.
- 4-8 prodotti verificati. Se non trovi, scrivi "Consulta modecoritaliana.it".

FORMATO (Markdown con wrapper):

<div class="final-guide">

# [Nome Torta]
[Descrizione 2-3 frasi]

---

## Prodotti Modecor consigliati
| Prodotto | Utilizzo | Link |
|----------|----------|------|
| [Nome ESATTO] | [Come si usa] | [URL ESATTO] |

---

## Ingredienti da acquistare separatamente
- [Ingrediente con quantita']

---

## Procedura step-by-step
### 1. Preparazione base
### 2. Copertura
### 3. Decorazioni
### 4. Assemblaggio
### 5. Finitura e conservazione

---
*Procedura indicativa. Prodotti dal catalogo ufficiale Modecor.*

</div>

Dosi precise, tempi precisi, NO emoji.

CONVERSAZIONE:
{summary}

CATALOGO (UNICA FONTE):
{products_catalog}"""


# -------------------------------------------------
# OPENAI
# -------------------------------------------------
def init_openai_client():
    if not OPENAI_API_KEY:
        st.error("Chiave API OpenAI non configurata. Imposta `OPENAI_API_KEY` nei Secrets.")
        st.stop()
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Errore OpenAI: {e}")
        return None


def encode_image_to_base64(f):
    return base64.b64encode(f.getvalue()).decode("utf-8")


def call_gpt_vision(client, image_base64, prompt):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "auto"}}
            ]}],
            max_tokens=1024, temperature=0.5)
        return r.choices[0].message.content
    except Exception as e:
        st.error(f"Errore analisi: {e}")
        return None


def call_gpt_conversation(client, messages):
    try:
        r = client.chat.completions.create(model="gpt-4o-mini", messages=messages,
                                            max_tokens=2048, temperature=0.5)
        return r.choices[0].message.content
    except Exception as e:
        st.error(f"Errore GPT: {e}")
        return None


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_conversation_history():
    return "\n\n".join(
        f"{'Utente' if m['role'] == 'user' else 'Modecor AI'}: {m['content']}"
        for m in st.session_state.messages
    )

def create_gpt_messages_history():
    return [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

def check_if_info_complete(r):
    return "[INFO_COMPLETE]" in r

def display_message_content(content):
    content = content.replace("[INFO_COMPLETE]", "").strip()
    tag = '<div class="final-guide">'
    if tag in content:
        si = content.find(tag)
        inner = content[si + len(tag):]
        ei = inner.rfind("</div>")
        st.markdown(inner[:ei].strip() if ei != -1 else inner.strip())
    else:
        st.markdown(content)

def generate_final_guide(client, products_text):
    summary = get_conversation_history()
    prompt = create_final_output_prompt(summary, products_text)
    output = call_gpt_conversation(client, [{"role": "user", "content": prompt}])
    if output:
        st.session_state.messages.append({"role": "assistant", "content": output})
        st.session_state.guide_generated = True
        return output
    return None


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    # Header
    st.markdown("""
    <div class="app-header">
        <div class="header-decoration">
            <div class="header-line"></div>
            <div class="header-dot"></div>
            <div class="header-line"></div>
        </div>
        <p class="brand-name">Modecor <em>AI</em> Assistant</p>
        <p class="brand-tagline">Decorazioni professionali per pasticceria</p>
    </div>
    """, unsafe_allow_html=True)
    
    client = init_openai_client()
    if not client:
        st.stop()
    
    # Catalogo
    if st.session_state.products_catalog is None:
        with st.spinner("Caricamento catalogo Modecor..."):
            products = fetch_modecor_products()
            if products:
                st.session_state.products_catalog = products
                st.session_state.products_index = build_products_index(products)
            else:
                st.error("Impossibile caricare il catalogo.")
                st.stop()
    
    # ===== UPLOAD =====
    if st.session_state.phase == "upload":
        st.markdown("""
        <div class="upload-hero">
            <span class="upload-icon">🎂</span>
            <p class="upload-title">Carica la foto della tua torta</p>
            <p class="upload-subtitle">
                Analizzeremo l'immagine e ti guideremo nella realizzazione<br>
                con i prodotti del catalogo ufficiale Modecor
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Seleziona immagine", type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.markdown('<div class="cake-card">', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)
            st.markdown('<div class="cake-card-label ready-badge">Immagine pronta per l\'analisi</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Analizza Torta", use_container_width=True, type="primary"):
                    st.session_state.cake_image = uploaded_file
                    st.session_state.image_base64 = encode_image_to_base64(uploaded_file)
                    with st.spinner("Analisi in corso..."):
                        products_text = prepare_products_for_ai(st.session_state.products_catalog)
                        analysis = call_gpt_vision(client, st.session_state.image_base64,
                                                   create_initial_analysis_prompt(products_text))
                        if analysis:
                            st.session_state.messages.append({"role": "assistant", "content": analysis})
                            st.session_state.phase = "conversation"
                            st.rerun()
                        else:
                            st.error("Analisi non riuscita. Riprova.")
        
        # Divider + footer
        st.markdown("""
        <div class="gold-divider"><div class="line"></div><div class="diamond"></div><div class="line"></div></div>
        <div class="app-footer">
            Powered by Modecor Italiana &middot; 
            <a href="https://www.modecoritaliana.it" target="_blank">modecoritaliana.it</a>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== CONVERSAZIONE =====
    elif st.session_state.phase == "conversation":
        # Sidebar
        with st.sidebar:
            st.markdown('<p style="font-family:Playfair Display,serif;font-size:1rem;font-weight:600;">Modecor AI</p>',
                        unsafe_allow_html=True)
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, use_container_width=True)
            st.markdown("---")
            n = len(st.session_state.products_catalog) if st.session_state.products_catalog else 0
            st.caption(f"Catalogo: {n} prodotti")
            st.caption(f"Messaggi: {len(st.session_state.messages)}")
            st.markdown("---")
            if st.button("Nuova analisi", use_container_width=True):
                for k in ["messages", "cake_image", "image_base64", "products_catalog",
                           "products_index", "phase", "guide_generated", "all_info_collected"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
        
        # Foto torta visibile nel body principale
        if st.session_state.cake_image:
            st.markdown('<div class="cake-card">', unsafe_allow_html=True)
            st.image(st.session_state.cake_image, use_container_width=True)
            st.markdown('<div class="cake-card-label">Torta in analisi</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Badge
        badge = "Guida completa generata" if st.session_state.guide_generated else "Conversazione in corso"
        st.markdown(f'<div class="phase-badge">{badge}</div>', unsafe_allow_html=True)
        
        # Messaggi
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🎂"):
                display_message_content(msg["content"])
        
        # Genera guida
        if st.session_state.all_info_collected and not st.session_state.guide_generated:
            st.markdown("""
            <div class="generate-section">
                <p>Tutte le informazioni raccolte!</p>
                <p class="sub">Genera la guida personalizzata con prodotti Modecor</p>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Genera Guida Completa", use_container_width=True, type="primary"):
                    with st.spinner("Creazione guida personalizzata..."):
                        output = generate_final_guide(client,
                                    prepare_products_for_ai(st.session_state.products_catalog))
                        if output:
                            st.rerun()
        
        # Input
        prompt = st.chat_input("Scrivi qui la tua risposta...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar="🎂"):
                with st.spinner(""):
                    products_text = prepare_products_for_ai(st.session_state.products_catalog)
                    conv_prompt = create_conversation_prompt(get_conversation_history(), products_text)
                    gpt_msgs = create_gpt_messages_history()
                    gpt_msgs.append({"role": "user", "content": conv_prompt})
                    response = call_gpt_conversation(client, gpt_msgs)
                    if response:
                        if check_if_info_complete(response):
                            st.session_state.all_info_collected = True
                        st.markdown(response.replace("[INFO_COMPLETE]", "").strip())
                        st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


if __name__ == "__main__":
    main()
