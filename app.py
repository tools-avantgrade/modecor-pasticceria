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
    page_icon="🧁",
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
except:
    pass

if not OPENAI_API_KEY:
    try:
        if "default" in st.secrets:
            OPENAI_API_KEY = st.secrets["default"]["OPENAI_API_KEY"]
    except:
        pass

if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# -------------------------------------------------
# CSS PERSONALIZZATO
# -------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* ===== CONTENITORE CENTRALE - Tutto centrato ===== */
    .main .block-container {
        max-width: 900px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }
    
    /* Su mobile, usa tutta la larghezza */
    @media (max-width: 768px) {
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* ===== HEADER ===== */
    .main-title {
        color: #DC2626;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* ===== SEZIONE UPLOAD - Centrata ===== */
    .upload-section {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin: 1.5rem auto;
        max-width: 700px;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.2);
    }
    
    .upload-section h2 {
        margin: 0 0 0.8rem 0;
        font-size: 1.6rem;
        font-weight: 600;
    }
    
.upload-section p {
    margin: 0;
    opacity: 0.9;
    font-size: 0.95rem;
}

/* ===== CONTENITORE UPLOAD - Centrato e stretto ===== */
.upload-container {
    max-width: 600px;
    margin: 2rem auto;
}

.upload-container [data-testid="column"] {
    padding: 0 1rem;
}

/* Immagine nella sezione upload */
.upload-container [data-testid="stImage"] img {
    max-height: 350px !important;
    width: 100%;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 1rem;
}

/* Testo nella sezione upload */
.upload-info {
    background: #f9fafb;
    padding: 1.5rem;
    border-radius: 12px;
    border: 2px solid #e5e7eb;
    text-align: center;
}

.upload-info h3 {
    color: #DC2626;
    margin-bottom: 1rem;
    font-size: 1.3rem;
}

.upload-info p {
    color: #6b7280;
    margin-bottom: 1.5rem;
}
    
    /* ===== FILE UPLOADER - Centrato ===== */
    [data-testid="stFileUploader"] {
        max-width: 600px;
        margin: 1rem auto !important;
    }
    
    /* ===== IMMAGINE ANTEPRIMA - Dimensione fissa piccola ===== */
    [data-testid="stImage"] {
        max-width: 400px !important;
        margin: 0 auto !important;
    }
    
    [data-testid="stImage"] img {
        max-width: 100%;
        max-height: 400px;
        object-fit: contain;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Colonne upload - centrate */
    .stColumns {
        gap: 2rem !important;
    }
    
    /* ===== SIDEBAR - Immagine piccola ===== */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        max-width: 100% !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        max-height: 300px !important;
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] {
        background: #f9fafb;
    }
    
    /* ===== CHAT MESSAGES ===== */
    .stChatMessage {
        max-width: 100%;
    }
    
    /* ===== OUTPUT FINALE ===== */
    .final-guide {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid #DC2626;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.1);
    }
    
    .final-guide h1 {
        color: #DC2626;
        font-size: 1.8rem;
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 3px solid #FCD34D;
        padding-bottom: 0.5rem;
    }
    
    .final-guide h2 {
        color: #991B1B;
        font-size: 1.4rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .final-guide h3 {
        color: #DC2626;
        font-size: 1.1rem;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .final-guide p {
        color: #374151;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .final-guide ul, .final-guide ol {
        color: #374151;
        line-height: 1.8;
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .final-guide li {
        margin-bottom: 0.5rem;
    }
    
    .final-guide table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .final-guide th {
        background: #DC2626;
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        border: 1px solid #991B1B;
    }
    
    .final-guide td {
        padding: 0.8rem;
        border: 1px solid #e5e7eb;
        color: #374151;
    }
    
    .final-guide tr:nth-child(even) {
        background: #f9fafb;
    }
    
    .final-guide tr:hover td {
        background: #fef3c7;
    }
    
    .final-guide a {
        color: #DC2626;
        text-decoration: none;
        font-weight: 500;
    }
    
    .final-guide a:hover {
        text-decoration: underline;
    }
    
    .final-guide hr {
        border: none;
        border-top: 2px solid #FCD34D;
        margin: 2rem 0;
    }
    
    /* ===== PULSANTI ===== */
    .stButton>button {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
        transform: translateY(-1px);
    }
    
    /* Pulsante genera guida */
    .generate-btn {
        margin: 2rem 0 1rem 0;
        text-align: center;
    }
    
    /* ===== BADGE FASE ===== */
    .phase-badge {
        display: inline-block;
        background: linear-gradient(90deg, #DC2626 0%, #991B1B 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.2);
    }
    
    /* ===== RESPONSIVE - Mobile ===== */
    @media (max-width: 768px) {
        .upload-section {
            max-width: 100%;
            padding: 2rem 1.5rem;
        }
        
        [data-testid="stImage"] {
            max-width: 100% !important;
        }
        
        [data-testid="stImage"] img {
            max-height: 300px;
        }
        
        .final-guide {
            padding: 1.5rem;
        }
        
        .final-guide h1 {
            font-size: 1.5rem;
        }
        
        .final-guide h2 {
            font-size: 1.2rem;
        }
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
if "phase" not in st.session_state:
    st.session_state.phase = "upload"
if "guide_generated" not in st.session_state:
    st.session_state.guide_generated = False

# -------------------------------------------------
# FUNZIONI API MODECOR
# -------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_modecor_products() -> Optional[List[Dict]]:
    """Recupera prodotti Modecor"""
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

def prepare_products_for_ai(products: List[Dict], max_products: int = 1500) -> str:
    """Prepara catalogo per AI"""
    if not products:
        return "Nessun prodotto disponibile."
    
    products_subset = products[:max_products]
    catalog_text = "# CATALOGO PRODOTTI MODECOR\n\n"
    
    for i, prod in enumerate(products_subset, 1):
        catalog_text += f"{i}. {prod.get('titolo', 'N/A')}\n"
        catalog_text += f"   URL: {prod.get('url', 'N/A')}\n\n"
    
    return catalog_text

# -------------------------------------------------
# FUNZIONI OPENAI
# -------------------------------------------------
def init_openai_client() -> Optional[OpenAI]:
    """Inizializza OpenAI"""
    if not OPENAI_API_KEY:
        st.error("API Key OpenAI non configurata.")
        st.stop()
    
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Errore OpenAI: {e}")
        return None

def encode_image_to_base64(uploaded_file) -> str:
    """Converte immagine in base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def create_initial_analysis_prompt(products_catalog: str) -> str:
    """Prompt analisi iniziale"""
    return f"""Sei l'assistente AI di Modecor per pasticcieri.

Analizza questa torta brevemente:
- Tipo e stile
- Colori dominanti
- Elementi decorativi principali
- Complessità

Rispondi in modo conversazionale (max 120 parole).
Poi chiedi: "Questa è la torta che vuoi realizzare?"

{products_catalog}"""

def create_conversation_prompt(conversation_history: str, products_catalog: str) -> str:
    """Prompt conversazione"""
    return f"""Sei l'assistente AI di Modecor. Guida l'utente con domande dirette.

DOMANDE DA FARE (una alla volta):
1. Per quante persone?
2. Qual è l'occasione?
3. Preferisci decorazioni in zucchero, cialda o cioccolato?
4. Ci sono colori specifici?
5. Preferenze di gusto?
6. Allergie o ingredienti da evitare?

Fai UNA domanda alla volta. Sii breve e conversazionale.

NON generare la guida finale. Fai solo domande finché non hai tutte le info.

CONVERSAZIONE:
{conversation_history}

CATALOGO:
{products_catalog}"""

def create_final_output_prompt(conversation_summary: str, products_catalog: str) -> str:
    """Prompt output finale"""
    return f"""Genera una guida completa seguendo ESATTAMENTE questo formato HTML:

<div class="final-guide">

# [Nome Torta]

[Breve descrizione estetica in 2-3 frasi]

---

## Prodotti Modecor da utilizzare

| Prodotto | Descrizione | Link |
|----------|-------------|------|
| [Nome prodotto] | [Come si usa nella torta] | [URL completo] |
| [Nome prodotto 2] | [Come si usa] | [URL completo] |

(Includi 5-8 prodotti dal catalogo con URL reali)

---

## Altri ingredienti da acquistare separatamente

- [Ingrediente 1] con quantità precisa (es. 300g farina)
- [Ingrediente 2] con quantità precisa
- [Ingrediente 3] con quantità precisa
- ...

---

## Step-by-step per realizzarla

### 1. Prepara la base
[Istruzioni dettagliate con dosi, tempi e temperature precise]

### 2. Copertura
[Istruzioni dettagliate per la copertura]

### 3. Creazione decorazioni
[Istruzioni per creare le decorazioni]

### 4. Decorazione finale
[Come assemblare e posizionare le decorazioni]

### 5. Finitura
[Ultimi ritocchi e conservazione]

</div>

**REGOLE:**
- USA SOLO prodotti con URL dal catalogo
- Dosi precise in grammi/ml
- NO emoji
- Formato Markdown dentro HTML

CONVERSAZIONE:
{conversation_summary}

CATALOGO:
{products_catalog}"""

def call_gpt_vision(client: OpenAI, image_base64: str, prompt: str) -> Optional[str]:
    """GPT-4 Vision"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }],
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Errore GPT Vision: {e}")
        return None

def call_gpt_conversation(client: OpenAI, messages: List[Dict]) -> Optional[str]:
    """GPT-4 conversazione"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Errore GPT: {e}")
        return None

# -------------------------------------------------
# FUNZIONI UI
# -------------------------------------------------
def get_conversation_history() -> str:
    """Storia conversazione"""
    history = ""
    for msg in st.session_state.messages:
        role = "Utente" if msg["role"] == "user" else "Modecor AI"
        history += f"{role}: {msg['content']}\n\n"
    return history

def create_gpt_messages_history() -> List[Dict]:
    """Lista messaggi GPT"""
    return [{"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages]

def generate_final_guide(client: OpenAI, products_text: str):
    """Genera e mostra guida finale nella chat"""
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
    # Header
    st.markdown('<h1 class="main-title">🧁 Modecor AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Il tuo assistente per decorazioni professionali</p>', 
                unsafe_allow_html=True)
    
    # Inizializza
    client = init_openai_client()
    if not client:
        st.stop()
    
    # Carica catalogo
    if st.session_state.products_catalog is None:
        with st.spinner("Caricamento catalogo..."):
            products = fetch_modecor_products()
            if products:
                st.session_state.products_catalog = products
            else:
                st.error("Impossibile caricare il catalogo.")
                st.stop()
    
    # ===== FASE UPLOAD =====
    if st.session_state.phase == "upload":
        st.markdown("""
        <div class="upload-section">
            <h2>Carica la Foto della Torta</h2>
            <p>Inizia caricando un'immagine della torta che vuoi realizzare</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Seleziona immagine",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        
if uploaded_file:
    # Contenitore centrato stretto
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    
    # Immagine centrata
    st.image(uploaded_file, use_container_width=True)
    
    # Spaziatura
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Info centrata
    st.markdown("### ✅ Immagine Pronta")
    st.markdown("Clicca il pulsante per iniziare l'analisi AI")
    
    # Pulsante centrato in colonna
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analizza Torta", use_container_width=True, type="primary"):
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== FASE CONVERSAZIONE (SEMPRE ATTIVA) =====
    elif st.session_state.phase == "conversation":
        # Sidebar
        with st.sidebar:
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, use_container_width=True)
            
            st.markdown("---")
            st.metric("Messaggi", len(st.session_state.messages))
            
            if st.button("Nuova Torta", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Badge fase
        st.markdown('<div class="phase-badge">Chat Modecor AI</div>', unsafe_allow_html=True)
        
        # Mostra tutti i messaggi
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🧁"):
                st.markdown(msg["content"], unsafe_allow_html=True)
        
        # Pulsante genera guida (dopo 6+ messaggi)
        if len(st.session_state.messages) >= 6 and not st.session_state.guide_generated:
            st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
            if st.button("✨ Genera Guida Completa", use_container_width=True, type="primary"):
                with st.spinner("Creazione guida personalizzata..."):
                    products_text = prepare_products_for_ai(st.session_state.products_catalog)
                    output = generate_final_guide(client, products_text)
                    if output:
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Input SEMPRE attivo
        if prompt := st.chat_input("Scrivi qui la tua risposta..."):
            # Mostra subito messaggio utente
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            # Genera risposta AI
            with st.chat_message("assistant", avatar="🧁"):
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
                        st.markdown(response)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
            
            st.rerun()

if __name__ == "__main__":
    main()
