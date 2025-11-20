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

# OpenAI API - Gestione robusta
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
# CSS PERSONALIZZATO STILE CHATGPT
# -------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
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
    
    .upload-section {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.2);
    }
    
    .upload-section h2 {
        margin: 0 0 1rem 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .upload-section p {
        margin: 0;
        opacity: 0.9;
    }
    
    /* Stile chat nativa Streamlit */
    .stChatMessage {
        padding: 1rem 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Avatar styling */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 32px !important;
        height: 32px !important;
    }
    
    /* Output finale */
    .final-output {
        background: white;
        border-radius: 12px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .final-output h1 {
        color: #DC2626;
        font-size: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .final-output h2 {
        color: #991B1B;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 2px solid #FCD34D;
        padding-bottom: 0.5rem;
    }
    
    .final-output h3 {
        color: #DC2626;
        font-size: 1.2rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .final-output p {
        color: #374151;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .final-output ul, .final-output ol {
        color: #374151;
        line-height: 1.8;
        margin-left: 1.5rem;
    }
    
    .final-output table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .final-output th {
        background: #DC2626;
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }
    
    .final-output td {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid #e5e7eb;
        color: #374151;
    }
    
    .final-output tr:hover td {
        background: #fef3c7;
    }
    
    .final-output a {
        color: #DC2626;
        text-decoration: none;
        font-weight: 500;
    }
    
    .final-output a:hover {
        text-decoration: underline;
    }
    
    .final-output hr {
        border: none;
        border-top: 2px solid #FCD34D;
        margin: 2rem 0;
    }
    
    /* Pulsanti */
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
    
    /* Input chat */
    .stChatInputContainer {
        border-top: 1px solid #e5e7eb;
        padding-top: 1rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f9fafb;
    }
    
    /* Phase indicator */
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
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# INIZIALIZZAZIONE STATO SESSIONE
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
if "awaiting_response" not in st.session_state:
    st.session_state.awaiting_response = False

# -------------------------------------------------
# FUNZIONI API MODECOR
# -------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_modecor_products() -> Optional[List[Dict]]:
    """Recupera tutti i prodotti Modecor via API"""
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
        else:
            print(f"Errore API Modecor: {response.status_code}")
            return None
    except Exception as e:
        print(f"Errore connessione API Modecor: {e}")
        return None

def prepare_products_for_ai(products: List[Dict], max_products: int = 1500) -> str:
    """Prepara il catalogo prodotti in formato compatto per GPT"""
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
    """Inizializza client OpenAI"""
    if not OPENAI_API_KEY:
        st.error("API Key OpenAI non configurata. Vai in Settings → Secrets su Streamlit Cloud.")
        st.stop()
    
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Errore inizializzazione OpenAI: {e}")
        return None

def encode_image_to_base64(uploaded_file) -> str:
    """Converte immagine in base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def create_initial_analysis_prompt(products_catalog: str) -> str:
    """Prompt per analisi iniziale immagine"""
    return f"""Sei l'assistente AI di Modecor per pasticcieri professionisti.

Analizza questa torta e descrivi brevemente:
- Tipo di torta
- Stile e colori dominanti
- Elementi decorativi principali
- Tecniche utilizzate
- Complessità stimata

Rispondi in modo conversazionale e conciso (massimo 150 parole).
Poi chiedi: "Questa è la torta che vuoi realizzare?"

{products_catalog}"""

def create_conversation_prompt(conversation_history: str, products_catalog: str) -> str:
    """Prompt per conversazione guidata"""
    return f"""Sei l'assistente AI di Modecor. Guida l'utente con domande dirette e specifiche.

DOMANDE DA FARE (una alla volta, in ordine):
1. Per quante persone è la torta?
2. Qual è l'occasione? (compleanno, matrimonio, ecc.)
3. Preferisci decorazioni in zucchero, cialda o cioccolato?
4. Ci sono colori specifici da usare?
5. Hai preferenze di gusto? (cioccolato, vaniglia, frutta, ecc.)
6. Ci sono allergie o ingredienti da evitare?

Fai UNA domanda alla volta. Sii conversazionale ma conciso.
Se hai tutte le info necessarie, dì: "Perfetto, ora genero la guida completa!"

CONVERSAZIONE FINORA:
{conversation_history}

CATALOGO:
{products_catalog}"""

def create_final_output_prompt(conversation_summary: str, products_catalog: str) -> str:
    """Prompt per output finale"""
    return f"""Genera una guida completa seguendo ESATTAMENTE questo formato:

# [Nome Torta]

[Breve descrizione estetica in 2-3 frasi]

---

## Prodotti Modecor da utilizzare

| Prodotto | Descrizione | Link |
|----------|-------------|------|
| [Nome] | [Come si usa] | [URL completo] |

(Includi 5-8 prodotti dal catalogo, SOLO prodotti reali con URL)

---

## Altri ingredienti da acquistare separatamente

- [Ingrediente 1 con quantità precisa]
- [Ingrediente 2 con quantità precisa]
- ...

---

## Step-by-step per realizzarla

### 1. Prepara la base
[Istruzioni dettagliate con dosi precise]

### 2. Copertura
[Istruzioni dettagliate]

### 3. Creazione decorazioni
[Istruzioni dettagliate]

### 4. Decorazione finale
[Istruzioni dettagliate]

### 5. Finitura
[Istruzioni dettagliate]

---

**REGOLE CRITICHE:**
- USA SOLO prodotti presenti nel catalogo con URL completi
- Dosi precise in grammi/ml
- Linguaggio tecnico ma chiaro
- NO emoji
- Formato Markdown pulito

CONVERSAZIONE:
{conversation_summary}

CATALOGO:
{products_catalog}"""

def call_gpt_vision(client: OpenAI, image_base64: str, prompt: str) -> Optional[str]:
    """Chiamata GPT-4 Vision"""
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
        st.error(f"Errore durante l'analisi dell'immagine: {e}")
        return None

def call_gpt_conversation(client: OpenAI, messages: List[Dict]) -> Optional[str]:
    """Chiamata GPT-4 conversazione"""
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
        st.error(f"Errore durante la generazione della risposta: {e}")
        return None

# -------------------------------------------------
# FUNZIONI UI
# -------------------------------------------------
def get_conversation_history() -> str:
    """Ottiene la storia conversazione"""
    history = ""
    for msg in st.session_state.messages:
        role = "Utente" if msg["role"] == "user" else "Modecor AI"
        history += f"{role}: {msg['content']}\n\n"
    return history

def create_gpt_messages_history() -> List[Dict]:
    """Crea lista messaggi per GPT"""
    return [{"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages]

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
def main():
    # Header
    st.markdown('<h1 class="main-title">🧁 Modecor AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Il tuo assistente per decorazioni professionali</p>', 
                unsafe_allow_html=True)
    
    # Inizializza client
    client = init_openai_client()
    if not client:
        st.stop()
    
    # Carica catalogo
    if st.session_state.products_catalog is None:
        with st.spinner("Caricamento catalogo prodotti..."):
            products = fetch_modecor_products()
            if products:
                st.session_state.products_catalog = products
            else:
                st.error("Impossibile caricare il catalogo. Riprova più tardi.")
                st.stop()
    
    # ===== FASE 1: UPLOAD =====
    if st.session_state.phase == "upload":
        st.markdown("""
        <div class="upload-section">
            <h2>Carica la Foto della Torta</h2>
            <p>Inizia caricando un'immagine della torta che vuoi realizzare</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Seleziona un'immagine",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, use_container_width=True)
            
            with col2:
                st.markdown("### Immagine pronta")
                st.markdown("Clicca per iniziare l'analisi AI della torta")
                
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
    
    # ===== FASE 2: CONVERSAZIONE =====
    elif st.session_state.phase == "conversation":
        # Sidebar
        with st.sidebar:
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, use_container_width=True)
            
            st.markdown("---")
            st.metric("Messaggi", len(st.session_state.messages))
            
            if st.button("Ricomincia", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Indicatore fase
        st.markdown('<div class="phase-badge">Conversazione in corso</div>', unsafe_allow_html=True)
        
        # Mostra chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🧁"):
                st.markdown(msg["content"])
        
        # Input utente
        if prompt := st.chat_input("Scrivi qui la tua risposta..."):
            # Mostra subito il messaggio utente
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            # Genera risposta
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
                        
                        # Check se passare a finale
                        if len(st.session_state.messages) > 12:
                            if "perfetto" in response.lower() or "guida completa" in response.lower():
                                st.session_state.phase = "final"
                                st.rerun()
            
            st.rerun()
        
        # Pulsante genera output
        if len(st.session_state.messages) >= 8:
            st.markdown("---")
            if st.button("Genera Guida Completa", use_container_width=True, type="primary"):
                st.session_state.phase = "final"
                st.rerun()
    
    # ===== FASE 3: OUTPUT FINALE =====
    elif st.session_state.phase == "final":
        with st.sidebar:
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, use_container_width=True)
            
            if st.button("Nuova Torta", use_container_width=True, type="primary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown('<div class="phase-badge">Generazione guida completa</div>', unsafe_allow_html=True)
        
        with st.spinner("Sto creando la tua guida personalizzata..."):
            conversation_summary = get_conversation_history()
            products_text = prepare_products_for_ai(st.session_state.products_catalog)
            final_prompt = create_final_output_prompt(conversation_summary, products_text)
            
            gpt_msgs = [{"role": "user", "content": final_prompt}]
            final_output = call_gpt_conversation(client, gpt_msgs)
            
            if final_output:
                st.markdown('<div class="final-output">', unsafe_allow_html=True)
                st.markdown(final_output)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Pulsanti azione
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="Scarica Ricetta",
                        data=final_output,
                        file_name="modecor_ricetta.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("Condividi", use_container_width=True):
                        st.info("Funzionalità in arrivo")
                
                with col3:
                    if st.button("Nuova Torta", use_container_width=True):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()

if __name__ == "__main__":
    main()
