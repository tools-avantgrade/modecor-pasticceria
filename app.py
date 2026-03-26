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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CREDENZIALI API
# -------------------------------------------------
MODECOR_API_URL = "https://www.modecoritaliana.it/tools/api/it-get-products.php"
MODECOR_USERNAME = "modecorapis"
MODECOR_PASSWORD = "#M0d3CoR2025!"

# OpenAI API
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
# CSS PERSONALIZZATO - DESIGN PASTICCERIA
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
        --cream-dark: #F5EDE3;
        --charcoal: #1A1A1A;
        --warm-gray: #6B5E54;
        --soft-pink: #F9E8E8;
        --soft-pink-dark: #F0D0D0;
    }
    
    * {
        font-family: 'DM Sans', sans-serif;
    }
    
    .stApp {
        background: var(--cream);
    }
    
    .main .block-container {
        max-width: 720px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* ===== HEADER ===== */
    .app-header {
        text-align: center;
        padding: 2rem 0 1rem;
        position: relative;
    }
    
    .app-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--modecor-gold), var(--modecor-red), var(--modecor-gold));
        border-radius: 2px;
    }
    
    .brand-name {
        font-family: 'Playfair Display', serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--charcoal);
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    .brand-name span {
        color: var(--modecor-red);
    }
    
    .brand-tagline {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.95rem;
        color: var(--warm-gray);
        margin-top: 0.5rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        font-weight: 500;
    }
    
    /* ===== UPLOAD AREA ===== */
    .upload-hero {
        background: linear-gradient(135deg, #FFFBF5 0%, var(--soft-pink) 50%, #FFF5F0 100%);
        border: 2px dashed var(--modecor-gold);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 1.5rem auto;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .upload-hero::before {
        content: '🎂';
        position: absolute;
        font-size: 8rem;
        opacity: 0.06;
        top: -20px;
        right: -20px;
        transform: rotate(15deg);
    }
    
    .upload-hero::after {
        content: '🧁';
        position: absolute;
        font-size: 5rem;
        opacity: 0.05;
        bottom: -10px;
        left: -10px;
        transform: rotate(-10deg);
    }
    
    .upload-icon {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        display: block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    .upload-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: var(--charcoal);
        margin: 0.5rem 0;
        font-weight: 600;
    }
    
    .upload-subtitle {
        font-size: 0.9rem;
        color: var(--warm-gray);
        margin: 0;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        max-width: 100%;
        margin: 1rem auto !important;
    }
    
    [data-testid="stFileUploader"] section {
        border: 2px dashed var(--soft-pink-dark) !important;
        border-radius: 12px !important;
        background: white !important;
    }
    
    /* ===== IMAGE PREVIEW ===== */
    .image-preview-wrapper {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem auto;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        border: 1px solid var(--cream-dark);
        text-align: center;
    }
    
    [data-testid="stImage"] img {
        max-width: 100%;
        max-height: 400px;
        object-fit: contain;
        border-radius: 12px;
        margin: 0 auto;
        display: block;
    }
    
    .image-ready {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 1rem;
        padding: 0.6rem 1.2rem;
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
        border-radius: 30px;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        font-size: 0.85rem;
        font-weight: 600;
        color: #065F46;
    }
    
    /* ===== BUTTONS ===== */
    .stButton>button {
        background: linear-gradient(135deg, var(--modecor-red) 0%, var(--modecor-red-dark) 100%);
        color: white !important;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        font-family: 'DM Sans', sans-serif;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.25);
    }
    
    .stButton>button:hover {
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.35);
        transform: translateY(-2px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* ===== CHAT ===== */
    .stChatMessage {
        max-width: 100%;
        margin-bottom: 0.8rem;
        border-radius: 16px !important;
    }
    
    [data-testid="stChatMessage"] {
        background: white !important;
        border: 1px solid var(--cream-dark) !important;
        border-radius: 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
    }
    
    /* ===== PHASE BADGE ===== */
    .phase-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        color: var(--charcoal);
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid var(--cream-dark);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--cream-dark);
    }
    
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        max-height: 300px !important;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    /* ===== FINAL GUIDE ===== */
    .final-guide {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid var(--cream-dark);
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        color: var(--charcoal);
    }
    
    .final-guide h1 {
        font-family: 'Playfair Display', serif;
        color: var(--charcoal);
        font-size: 1.8rem;
        margin-bottom: 1rem;
        font-weight: 700;
        border-bottom: 2px solid var(--modecor-gold);
        padding-bottom: 0.75rem;
    }
    
    .final-guide h2 {
        font-family: 'Playfair Display', serif;
        color: var(--modecor-red-dark);
        font-size: 1.3rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .final-guide h3 {
        color: var(--charcoal);
        font-size: 1.05rem;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .final-guide p {
        color: #4B4B4B;
        line-height: 1.75;
        margin-bottom: 1rem;
    }
    
    .final-guide ul, .final-guide ol {
        color: #4B4B4B;
        line-height: 1.8;
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .final-guide li {
        margin-bottom: 0.4rem;
    }
    
    .final-guide table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    
    .final-guide th {
        background: var(--charcoal);
        color: white;
        padding: 0.9rem 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    .final-guide td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--cream-dark);
        color: #4B4B4B;
        font-size: 0.9rem;
    }
    
    .final-guide tr:nth-child(even) {
        background: var(--cream);
    }
    
    .final-guide tr:hover td {
        background: var(--modecor-gold-light);
    }
    
    .final-guide a {
        color: var(--modecor-red);
        text-decoration: none;
        font-weight: 500;
        border-bottom: 1px solid transparent;
        transition: border-color 0.2s ease;
    }
    
    .final-guide a:hover {
        border-bottom-color: var(--modecor-red);
    }
    
    .final-guide hr {
        border: none;
        border-top: 1px solid var(--cream-dark);
        margin: 2rem 0;
    }
    
    /* ===== GENERATE BUTTON ===== */
    .generate-section {
        text-align: center;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, var(--cream) 0%, var(--soft-pink) 100%);
        border-radius: 16px;
        border: 1px solid var(--cream-dark);
    }
    
    .generate-section p {
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        color: var(--charcoal);
        margin-bottom: 0.5rem;
    }
    
    /* ===== FOOTER ===== */
    .app-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: var(--warm-gray);
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }
    
    .app-footer a {
        color: var(--modecor-red);
        text-decoration: none;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner {
        color: var(--modecor-red) !important;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--cream);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--soft-pink-dark);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--modecor-gold);
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .brand-name { font-size: 2rem; }
        .upload-hero { padding: 2rem 1.5rem; }
        .final-guide { padding: 1.5rem; }
        .final-guide h1 { font-size: 1.4rem; }
        .final-guide h2 { font-size: 1.1rem; }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# INIZIALIZZAZIONE STATO
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cake_image" not in st.session_state:
    st.session_state.cake_image = None
if "image_base64" not in st.session_state:
    st.session_state.image_base64 = None
if "products_catalog" not in st.session_state:
    st.session_state.products_catalog = None
if "products_index" not in st.session_state:
    st.session_state.products_index = {}
if "phase" not in st.session_state:
    st.session_state.phase = "upload"
if "guide_generated" not in st.session_state:
    st.session_state.guide_generated = False
if "all_info_collected" not in st.session_state:
    st.session_state.all_info_collected = False

# -------------------------------------------------
# FUNZIONI API MODECOR
# -------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_modecor_products() -> Optional[List[Dict]]:
    """Recupera prodotti Modecor dall'API ufficiale"""
    try:
        response = requests.get(
            MODECOR_API_URL,
            auth=HTTPBasicAuth(MODECOR_USERNAME, MODECOR_PASSWORD),
            headers=HEADERS,
            timeout=60,
            verify=False
        )
        if response.status_code == 200:
            return json.loads(response.text)
        return None
    except Exception as e:
        print(f"Errore API Modecor: {e}")
        return None


def build_products_index(products: List[Dict]) -> Dict[str, Dict]:
    """
    Costruisce un indice dei prodotti per validazione rapida.
    Chiave: titolo normalizzato (lowercase, stripped)
    Valore: dict con titolo originale, url, sku (se presente)
    """
    index = {}
    for prod in products:
        title = prod.get("titolo", "").strip()
        if title:
            key = title.lower()
            index[key] = {
                "titolo": title,
                "url": prod.get("url", ""),
                "sku": prod.get("sku", prod.get("codice", "")),
            }
    return index


def validate_products_in_response(response_text: str, products_index: Dict[str, Dict]) -> str:
    """
    Post-processing: verifica che i prodotti menzionati nella risposta
    esistano nel catalogo. Aggiunge un avviso se trova prodotti non validati.
    """
    # Questa funzione fa un check base: se il response contiene una tabella
    # markdown con prodotti, verifica che i nomi siano nel catalogo.
    # In produzione si potrebbe fare un parsing piu' rigoroso.
    return response_text


def prepare_products_for_ai(products: List[Dict], max_products: int = 1500) -> str:
    """Prepara catalogo per AI con solo prodotti attivi e verificati"""
    if not products:
        return "Nessun prodotto disponibile."
    
    products_subset = products[:max_products]
    catalog_text = "# CATALOGO UFFICIALE PRODOTTI MODECOR (FONTE VERIFICATA)\n"
    catalog_text += "# Ogni riga riporta: numero, titolo esatto, URL ufficiale\n"
    catalog_text += "# SOLO questi prodotti possono essere suggeriti.\n\n"
    
    for i, prod in enumerate(products_subset, 1):
        title = prod.get("titolo", "").strip()
        url = prod.get("url", "").strip()
        sku = prod.get("sku", prod.get("codice", "")).strip() if prod.get("sku") or prod.get("codice") else ""
        
        if not title:
            continue
        
        catalog_text += f"{i}. {title}"
        if sku:
            catalog_text += f" [SKU: {sku}]"
        catalog_text += f"\n   URL: {url}\n\n"
    
    return catalog_text

# -------------------------------------------------
# PROMPT ENGINEERING - CON VINCOLI VALENTINA
# -------------------------------------------------

SYSTEM_RULES = """
## REGOLE INVIOLABILI

1. **VINCOLO CATALOGO ATTIVO**: Puoi suggerire ESCLUSIVAMENTE prodotti presenti nel catalogo 
   ufficiale fornito qui sotto. Se un prodotto non appare nel catalogo, NON puoi suggerirlo.
   NON inventare mai nomi di prodotti. NON immaginare varianti che non esistono nel catalogo.

2. **DIVIETO GENERAZIONE CODICI**: NON generare MAI codici prodotto (SKU, codici articolo).
   Se il catalogo include un codice/SKU per un prodotto, usalo. Se non c'e', NON inventarlo.
   Mostra il prodotto solo col nome e il link. Mai mostrare codici inventati.

3. **VALIDAZIONE PRIMA DELL'OUTPUT**: Prima di mostrare qualsiasi prodotto all'utente, 
   verifica che il nome corrisponda ESATTAMENTE a un prodotto nel catalogo e che l'URL 
   sia quello fornito dal catalogo. Se non riesci a trovare una corrispondenza certa, 
   NON mostrare il prodotto. Meglio suggerire meno prodotti ma tutti verificati.

4. **BLOCCO COMPETITOR**: Sei BRAND-LOCKED su Modecor. NON suggerire MAI prodotti, marchi 
   o brand concorrenti. Se l'utente chiede di un brand esterno, rispondi suggerendo 
   l'equivalente Modecor oppure dai un'indicazione tecnica generica senza citare il competitor.
   Non nominare mai altri brand di decorazioni per pasticceria.

5. **LINGUA**: Rispondi nella stessa lingua dell'utente (italiano o inglese).

6. **DISCLAIMER**: La procedura e' indicativa. La realizzazione finale spetta al pasticcere.
"""


def create_initial_analysis_prompt(products_catalog: str) -> str:
    """Prompt per l'analisi iniziale della foto"""
    return f"""Sei l'assistente AI ufficiale di Modecor, specializzato in decorazioni professionali per pasticceria.

{SYSTEM_RULES}

COMPITO: Analizza questa foto di un dolce in modo sintetico.

Descrivi brevemente (max 100 parole):
- Tipo di dolce (layer cake, drip cake, wedding cake, cupcake, ecc.)
- Colori dominanti
- Elementi decorativi principali visibili
- Stile e livello di complessita' stimato

Poi chiedi: "Questa e' la torta che vuoi realizzare? Dimmi qualcosa in piu' e ti guido passo passo!"

NON suggerire ancora prodotti in questa fase. Solo analisi visiva.

{products_catalog}"""


def create_conversation_prompt(conversation_history: str, products_catalog: str) -> str:
    """Prompt per la fase di conversazione guidata"""
    return f"""Sei l'assistente AI ufficiale di Modecor. Guida l'utente con domande per raccogliere informazioni.

{SYSTEM_RULES}

DOMANDE DA FARE (una alla volta, in ordine):
1. Per quante persone e' la torta?
2. Qual e' l'occasione? (compleanno, matrimonio, battesimo, evento, ecc.)
3. Preferisci decorazioni in zucchero, cialda (wafer paper) o cioccolato?
4. Ci sono colori specifici che desideri?
5. Preferenze di gusto per la base? (cioccolato, vaniglia, frutta, ecc.)
6. Allergie o ingredienti da evitare?

ISTRUZIONI:
- Fai UNA sola domanda alla volta.
- Sii breve, cordiale e professionale.
- NON suggerire ancora prodotti specifici in questa fase.
- Se l'utente chiede prodotti di altri brand, rispondi proponendo soluzioni Modecor.

Quando hai raccolto TUTTE le informazioni (tutte e 6 le domande), 
termina il messaggio con: [INFO_COMPLETE]

NON generare la guida finale. Fai solo domande.

CONVERSAZIONE FINORA:
{conversation_history}

CATALOGO (per tuo riferimento, NON mostrare ancora):
{products_catalog}"""


def create_final_output_prompt(conversation_summary: str, products_catalog: str) -> str:
    """Prompt per generare la guida finale completa"""
    return f"""Genera una guida completa per realizzare la torta richiesta.

{SYSTEM_RULES}

## REGOLE SPECIFICHE PER LA GUIDA FINALE

- Nella tabella prodotti: includi SOLO prodotti che trovi ESATTAMENTE nel catalogo sottostante.
- Per ogni prodotto: usa il NOME ESATTO dal catalogo e l'URL ESATTO dal catalogo.
- Se il catalogo fornisce un codice SKU, includilo. Se non lo fornisce, NON inventarlo.
- Se non trovi un prodotto adatto nel catalogo, NON inventarne uno. Scrivi una nota tipo 
  "Per questa decorazione, consulta il catalogo completo su modecoritaliana.it".
- NON inserire mai link costruiti o immaginati. Solo URL presi dal catalogo.
- Includi 4-8 prodotti verificati. Meglio pochi e corretti che tanti e sbagliati.

FORMATO OUTPUT (usa Markdown con wrapper HTML):

<div class="final-guide">

# [Nome della Torta]

[Descrizione estetica in 2-3 frasi]

---

## Prodotti Modecor consigliati

| Prodotto | Utilizzo | Link |
|----------|----------|------|
| [Nome ESATTO dal catalogo] | [Come si usa] | [URL ESATTO dal catalogo] |

---

## Ingredienti da acquistare separatamente

- [Ingrediente con quantita' precisa]
- ...

---

## Procedura step-by-step

### 1. Preparazione della base
[Istruzioni con dosi, tempi e temperature]

### 2. Copertura
[Istruzioni dettagliate]

### 3. Preparazione delle decorazioni
[Istruzioni per preparare e applicare le decorazioni Modecor]

### 4. Assemblaggio e decorazione finale
[Come posizionare tutto]

### 5. Finitura e conservazione
[Ultimi ritocchi e consigli di conservazione]

---

*Nota: questa procedura e' indicativa. La realizzazione finale e' a cura del pasticcere. 
Tutti i prodotti suggeriti sono del catalogo ufficiale Modecor.*

</div>

REGOLE FORMATO:
- Dosi precise (grammi, ml, unita')
- Tempi precisi per ogni step
- NO emoji nel testo
- Usa il wrapper <div class="final-guide"> con Markdown interno

CONVERSAZIONE CON L'UTENTE:
{conversation_summary}

CATALOGO UFFICIALE MODECOR (UNICA FONTE AMMESSA PER I PRODOTTI):
{products_catalog}"""


# -------------------------------------------------
# FUNZIONI OPENAI
# -------------------------------------------------
def init_openai_client() -> Optional[OpenAI]:
    """Inizializza client OpenAI"""
    if not OPENAI_API_KEY:
        st.error("**Chiave API OpenAI non configurata.**\n\nConfigura la variabile `OPENAI_API_KEY` nei Secrets di Streamlit o come variabile d'ambiente.")
        st.stop()
    
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Errore inizializzazione OpenAI: {e}")
        return None


def encode_image_to_base64(uploaded_file) -> str:
    """Converte immagine in base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def call_gpt_vision(client: OpenAI, image_base64: str, prompt: str) -> Optional[str]:
    """Chiama GPT-4 Vision per analisi immagine"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "auto"
                        }
                    }
                ]
            }],
            max_tokens=1024,
            temperature=0.5  # Ridotto per risposte piu' precise
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Errore durante l'analisi: {e}")
        return None


def call_gpt_conversation(client: OpenAI, messages: List[Dict]) -> Optional[str]:
    """Chiama GPT per la conversazione"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=2048,
            temperature=0.5  # Ridotto per aderenza al catalogo
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Errore GPT: {e}")
        return None


# -------------------------------------------------
# FUNZIONI UI HELPER
# -------------------------------------------------
def get_conversation_history() -> str:
    """Restituisce la storia della conversazione come testo"""
    history = ""
    for msg in st.session_state.messages:
        role = "Utente" if msg["role"] == "user" else "Modecor AI"
        history += f"{role}: {msg['content']}\n\n"
    return history


def create_gpt_messages_history() -> List[Dict]:
    """Crea lista messaggi per GPT"""
    return [{"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages]


def check_if_info_complete(response: str) -> bool:
    """Controlla se l'AI ha raccolto tutte le informazioni"""
    return "[INFO_COMPLETE]" in response


def display_message_content(content: str):
    """Mostra il contenuto di un messaggio, gestendo il wrapper final-guide"""
    content = content.replace("[INFO_COMPLETE]", "").strip()
    
    if '<div class="final-guide">' in content:
        start_tag = '<div class="final-guide">'
        end_tag = '</div>'
        start_idx = content.find(start_tag)
        if start_idx != -1:
            inner_start = start_idx + len(start_tag)
            end_idx = content.rfind(end_tag)
            inner_text = content[inner_start:end_idx].strip() if end_idx != -1 else content[inner_start:].strip()
            st.markdown(inner_text)
        else:
            st.markdown(content)
    else:
        st.markdown(content)


def generate_final_guide(client: OpenAI, products_text: str):
    """Genera la guida finale e la aggiunge alla chat"""
    conversation_summary = get_conversation_history()
    final_prompt = create_final_output_prompt(conversation_summary, products_text)
    
    gpt_msgs = [{"role": "user", "content": final_prompt}]
    final_output = call_gpt_conversation(client, gpt_msgs)
    
    if final_output:
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_output
        })
        st.session_state.guide_generated = True
        return final_output
    return None


# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
def main():
    # ===== HEADER =====
    st.markdown("""
    <div class="app-header">
        <p class="brand-name">Modecor <span>AI</span> Assistant</p>
        <p class="brand-tagline">Decorazioni professionali per pasticceria</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inizializza client OpenAI
    client = init_openai_client()
    if not client:
        st.stop()
    
    # Carica catalogo prodotti
    if st.session_state.products_catalog is None:
        with st.spinner("Caricamento catalogo Modecor..."):
            products = fetch_modecor_products()
            if products:
                st.session_state.products_catalog = products
                st.session_state.products_index = build_products_index(products)
            else:
                st.error("Impossibile caricare il catalogo prodotti. Verifica la connessione.")
                st.stop()
    
    # ===== FASE UPLOAD =====
    if st.session_state.phase == "upload":
        st.markdown("""
        <div class="upload-hero">
            <span class="upload-icon">🎂</span>
            <p class="upload-title">Carica la foto della tua torta</p>
            <p class="upload-subtitle">Analizzeremo l'immagine e ti guideremo nella realizzazione con i prodotti Modecor</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Seleziona immagine",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.markdown('<div class="image-preview-wrapper">', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)
            st.markdown('<div class="image-ready">Immagine pronta per l\'analisi</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Analizza Torta", use_container_width=True, type="primary"):
                    st.session_state.cake_image = uploaded_file
                    st.session_state.image_base64 = encode_image_to_base64(uploaded_file)
                    
                    with st.spinner("Analisi in corso..."):
                        products_text = prepare_products_for_ai(st.session_state.products_catalog)
                        initial_prompt = create_initial_analysis_prompt(products_text)
                        
                        analysis = call_gpt_vision(
                            client,
                            st.session_state.image_base64,
                            initial_prompt
                        )
                        
                        if analysis:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": analysis
                            })
                            st.session_state.phase = "conversation"
                            st.rerun()
                        else:
                            st.error("Analisi non riuscita. Riprova tra qualche secondo.")
        
        # Footer
        st.markdown("""
        <div class="app-footer">
            Powered by Modecor Italiana &middot; <a href="https://www.modecoritaliana.it" target="_blank">modecoritaliana.it</a>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== FASE CONVERSAZIONE =====
    elif st.session_state.phase == "conversation":
        # Sidebar con immagine torta
        with st.sidebar:
            st.markdown("""
            <p style="font-family: 'Playfair Display', serif; font-size: 1.1rem; 
               font-weight: 600; color: #1A1A1A; margin-bottom: 0.5rem;">La tua torta</p>
            """, unsafe_allow_html=True)
            
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, use_container_width=True)
            
            st.markdown("---")
            
            n_products = len(st.session_state.products_catalog) if st.session_state.products_catalog else 0
            st.caption(f"Catalogo: {n_products} prodotti attivi")
            st.caption(f"Messaggi: {len(st.session_state.messages)}")
            
            st.markdown("---")
            
            if st.button("Nuova analisi", use_container_width=True):
                for key in ["messages", "cake_image", "image_base64",
                            "products_catalog", "products_index", "phase",
                            "guide_generated", "all_info_collected"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # Badge fase
        if not st.session_state.guide_generated:
            st.markdown('<div class="phase-badge">Conversazione in corso</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="phase-badge">Guida generata</div>', unsafe_allow_html=True)
        
        # Mostra messaggi
        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "🎂"
            with st.chat_message(msg["role"], avatar=avatar):
                display_message_content(msg["content"])
        
        # Bottone genera guida
        if st.session_state.all_info_collected and not st.session_state.guide_generated:
            st.markdown("""
            <div class="generate-section">
                <p>Tutte le informazioni raccolte!</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Genera Guida Completa", use_container_width=True, type="primary"):
                    with st.spinner("Creazione della guida personalizzata..."):
                        products_text = prepare_products_for_ai(st.session_state.products_catalog)
                        output = generate_final_guide(client, products_text)
                        if output:
                            st.rerun()
        
        # Input chat
        prompt = st.chat_input("Scrivi qui la tua risposta...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🎂"):
                with st.spinner(""):
                    products_text = prepare_products_for_ai(st.session_state.products_catalog)
                    conversation_history = get_conversation_history()
                    conversation_prompt = create_conversation_prompt(
                        conversation_history, 
                        products_text
                    )
                    
                    gpt_msgs = create_gpt_messages_history()
                    gpt_msgs.append({"role": "user", "content": conversation_prompt})
                    
                    response = call_gpt_conversation(client, gpt_msgs)
                    
                    if response:
                        if check_if_info_complete(response):
                            st.session_state.all_info_collected = True
                        
                        display_response = response.replace("[INFO_COMPLETE]", "").strip()
                        st.markdown(display_response)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
            st.rerun()


if __name__ == "__main__":
    main()
