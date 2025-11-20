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
# API Modecor
MODECOR_API_URL = "https://www.modecoritaliana.it/tools/api/it-get-products.php"
MODECOR_USERNAME = "modecorapis"
MODECOR_PASSWORD = "#M0d3CoR2025!"

# OpenAI API - Gestione robusta con fallback multipli
OPENAI_API_KEY = None

# Metodo 1: Prova secrets con chiave diretta
try:
    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    pass

# Metodo 2: Prova secrets con sezione [default]
if not OPENAI_API_KEY:
    try:
        if "default" in st.secrets:
            OPENAI_API_KEY = st.secrets["default"]["OPENAI_API_KEY"]
    except:
        pass

# Metodo 3: Prova environment variables
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# -------------------------------------------------
# CSS PERSONALIZZATO MODECOR
# -------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        color: #DC2626;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(220, 38, 38, 0.3);
    }
    
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease-in;
        color: #1f2937 !important;
    }
    
    .chat-message strong {
        color: #DC2626 !important;
    }
    
    .chat-message * {
        color: #1f2937 !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-left: 5px solid #DC2626;
        color: #1f2937 !important;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 5px solid #FCD34D;
        color: #1f2937 !important;
    }
    
    .product-card {
        background: white;
        border: 2px solid #FCD34D;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        color: #1f2937 !important;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.3);
        border-color: #DC2626;
    }
    
    .phase-indicator {
        background: linear-gradient(90deg, #DC2626 0%, #991B1B 100%);
        color: white !important;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
    
    .final-output {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        color: #1f2937 !important;
    }
    
    .final-output * {
        color: #1f2937 !important;
    }
    
    .final-output h1, .final-output h2, .final-output h3 {
        color: #DC2626 !important;
    }
    
    .final-output strong {
        color: #991B1B !important;
    }
    
    .final-output a {
        color: #DC2626 !important;
        text-decoration: underline;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        color: white !important;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
    }
    
    /* Fix per markdown nelle chat */
    .chat-message p, .chat-message li, .chat-message span {
        color: #1f2937 !important;
    }
    
    .chat-message h1, .chat-message h2, .chat-message h3, .chat-message h4 {
        color: #DC2626 !important;
    }
    
    /* Fix per tabelle */
    table {
        color: #1f2937 !important;
    }
    
    th {
        background: #DC2626 !important;
        color: white !important;
    }
    
    td {
        color: #1f2937 !important;
    }
    
    /* Fix per expander debug */
    .streamlit-expanderHeader {
        color: #1f2937 !important;
    }
    
    .streamlit-expanderContent {
        color: #1f2937 !important;
    }
    
    /* Fix generale per tutto il testo dell'app */
    .stMarkdown {
        color: #1f2937 !important;
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
if "conversation_data" not in st.session_state:
    st.session_state.conversation_data = {}
if "phase" not in st.session_state:
    st.session_state.phase = "upload"
if "initial_analysis" not in st.session_state:
    st.session_state.initial_analysis = None

# -------------------------------------------------
# FUNZIONI API MODECOR
# -------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_modecor_products() -> Optional[List[Dict]]:
    """Recupera tutti i prodotti Modecor via API con caching"""
    try:
        response = requests.get(
            MODECOR_API_URL,
            auth=HTTPBasicAuth(MODECOR_USERNAME, MODECOR_PASSWORD),
            headers=HEADERS,
            timeout=60,
            verify=False
        )
        
        if response.status_code == 200:
            products = json.loads(response.text)
            return products
        else:
            st.error(f"❌ Errore API Modecor: Status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Errore connessione API Modecor: {e}")
        return None

def prepare_products_for_ai(products: List[Dict], max_products: int = 1500) -> str:
    """Prepara il catalogo prodotti in formato ottimizzato per GPT"""
    if not products:
        return "Nessun prodotto disponibile."
    
    # Prendi max_products per evitare overflow token
    products_subset = products[:max_products]
    
    # Crea rappresentazione compatta
    catalog_text = "# CATALOGO PRODOTTI MODECOR\n\n"
    catalog_text += f"Totale prodotti disponibili: {len(products_subset)}\n\n"
    
    for i, prod in enumerate(products_subset, 1):
        catalog_text += f"{i}. **{prod.get('titolo', 'N/A')}**\n"
        catalog_text += f"   - Descrizione: {prod.get('descrizione', 'N/A')}\n"
        catalog_text += f"   - URL: {prod.get('url', 'N/A')}\n\n"
    
    return catalog_text

# -------------------------------------------------
# FUNZIONI OPENAI GPT-4 VISION
# -------------------------------------------------
def init_openai_client() -> Optional[OpenAI]:
    """Inizializza client OpenAI con debug info"""
    
    # Debug Panel (rimuovibile dopo verifica)
    with st.expander("🔍 Debug Info - Configurazione API", expanded=False):
        st.write("**Secrets disponibili:**", list(st.secrets.keys()) if hasattr(st, 'secrets') and st.secrets else "Nessuno")
        st.write("**API Key caricata:**", "✅ Sì" if OPENAI_API_KEY else "❌ No")
        if OPENAI_API_KEY:
            st.write("**Lunghezza API Key:**", len(OPENAI_API_KEY))
            st.write("**Prefisso API Key:**", OPENAI_API_KEY[:10] + "..." if len(OPENAI_API_KEY) > 10 else "Errore")
    
    if not OPENAI_API_KEY:
        st.error("⚠️ **API Key OpenAI mancante!**")
        st.info("""
        **📝 Come configurarla su Streamlit Cloud:**
        
        1. Clicca su **'Settings'** (⚙️ in alto a destra)
        2. Vai in **'Secrets'** nel menu a sinistra
        3. Incolla questo testo:
```
        [default]
        OPENAI_API_KEY = "sk-proj-LA_TUA_NUOVA_API_KEY"
```
        
        4. Clicca **'Save'**
        5. Torna all'app e clicca **'Reboot app'** dal menu (⋮)
        6. Aspetta 1-2 minuti che l'app si riavvii
        """)
        st.stop()
    
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"❌ Errore inizializzazione OpenAI: {e}")
        return None

def encode_image_to_base64(uploaded_file) -> str:
    """Converte immagine caricata in base64 per OpenAI"""
    image_bytes = uploaded_file.getvalue()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return base64_image

def create_initial_analysis_prompt(products_catalog: str) -> str:
    """Crea il prompt per l'analisi iniziale dell'immagine"""
    return f"""Sei l'assistente AI ufficiale di Modecor, azienda leader italiana per decorazioni da pasticceria.

# TUO COMPITO
Analizza l'immagine della torta caricata e fornisci un'analisi dettagliata iniziale.

# ANALISI RICHIESTA
Identifica e descrivi:

1. **Tipo di torta**: (es. drip cake, naked cake, wedding cake, number cake, cream tart, ecc.)
2. **Stile generale**: (moderno, classico, rustico, elegante, minimal, ecc.)
3. **Palette colori dominanti**: elenca i colori principali usati
4. **Elementi decorativi visibili**: 
   - Topper (soggetti, scritte, candeline)
   - Fiori (tipo, colori, dimensioni)
   - Perline, glitter, sprinkles
   - Drip (colore e tipo)
   - Texture o pattern
   - Altri elementi decorativi
5. **Tecniche riconosciute**:
   - Tipo di copertura (fondente, crema, ganache, mirror glaze, ecc.)
   - Aerografo o colorazione
   - Stencil o decorazioni a mano
   - Modellazione 3D
6. **Dimensioni stimate**: numero di piani, diametro approssimativo
7. **Complessità**: livello di difficoltà (base/intermedio/esperto)

# CATALOGO PRODOTTI MODECOR
{products_catalog}

# FORMATO OUTPUT
Rispondi in italiano con un'analisi chiara e professionale. Usa questo formato:

🎂 **Tipo di Torta**: [tipo]

🎨 **Stile**: [descrizione stile]

🌈 **Colori Dominanti**: [lista colori]

✨ **Elementi Decorativi**:
- [elemento 1]
- [elemento 2]
- ...

🛠️ **Tecniche Utilizzate**:
- [tecnica 1]
- [tecnica 2]
- ...

📏 **Dimensioni Stimate**: [descrizione]

⭐ **Livello Complessità**: [base/intermedio/esperto]

Poi chiedi conferma: "Confermi che questa è la tipologia di torta che vuoi realizzare?"

**IMPORTANTE**: Sii preciso e dettagliato. Questa analisi servirà per le domande successive."""

def create_conversation_prompt(conversation_history: str, products_catalog: str) -> str:
    """Crea il prompt per la conversazione guidata"""
    return f"""Sei l'assistente AI ufficiale di Modecor per pasticcieri professionisti.

# CATALOGO PRODOTTI MODECOR DISPONIBILI
{products_catalog}

# FLUSSO CONVERSAZIONALE DA SEGUIRE

## FASE 1 – Inquadramento Iniziale
Fai queste domande per capire esigenze e contesto:

### Estetica e Decorazioni
1. **Colori specifici?** → Se sì, proponi coloranti Modecor (Colorgel per glasse/pasta di zucchero, ColorVel/ColorSoft per -18°C)
2. **È per una ricorrenza?** (Compleanno, matrimonio, Natale, Halloween, San Valentino, ecc.)
3. **Se compleanno → Servono candeline?** → Se sì, fornisci link: https://www.modecoritaliana.it/it/tutti-i-prodotti/ricorrenze/auguri-generici.html?cat=25&product_list_dir=desc
4. **Materiale decorazione preferito?** (Zucchero / Cialda / Cioccolato)

### Gusto e Ingredienti
5. **Torta +4°C (fresca) o -18°C (semifreddo)?**
   - +4°C: quote cake, lambeth, naked, chiffon, pasta di zucchero
   - -18°C: semifreddi glassati, torte gelato
6. **Che tipo di torta?** (moderna, tradizionale, decorata, monoporzione)
7. **Preferenze di gusto?** (cioccolato, frutta, vaniglia, nocciola, ecc.)
8. **Allergie o ingredienti da evitare?**
9. **Per quante persone?**

## FASE 2 – Scelta Decorazioni Dettagliata

Dopo la Fase 1, in base alla risposta "Materiale decorazione":

### Se "Zucchero":
- Vuoi un **fiore** o un **soggettino**?
  - **Fiore**: tipo (rosa/generico/ghiaccia) → colore → dimensione (0-2cm / 2-3.5cm / 3.5-5cm / >5cm)
  - **Soggettino**: piatto o 3D?
    - Se 3D: generico o a tema/brand? (Natale, Halloween, Thun, Sonic, Peppa Pig, ecc.)

### Se "Cialda":
- **Per bambino o adulto?**
  - Bambino → cialde brandizzate (Sonic, Peppa Pig, ecc.)
  - Adulto → fiori (come flusso zucchero)

### Se "Cioccolato":
- **Tipo cioccolato**: fondente / bianco / colorato
- **Tipo decorazione**: piatta / 3D

### Extra Finale:
"Vuoi integrare con decorazioni easy?" → Suggerisci: macarons, sprinkles, golden touch, meringhe

## FINALE:
"Ora che la tua torta è bellissima, non dimenticare di metterci sopra il tuo logo con un personalizzato 👉 [Mettici la firma](https://www.modecoritaliana.it/mettici-la-firma)"

# STORIA CONVERSAZIONE
{conversation_history}

# REGOLE IMPORTANTI
- Fai UNA domanda alla volta, massimo DUE se strettamente correlate
- Sii amichevole e professionale
- Usa emoji per rendere la chat più piacevole
- Se l'utente ha già risposto a qualcosa, NON chiederlo di nuovo
- Suggerisci prodotti Modecor SOLO dal catalogo fornito sopra
- Usa sempre i link completi presenti nel catalogo
- Rispondi in italiano

# TUO COMPITO ADESSO
Continua la conversazione seguendo il flusso. Fai la prossima domanda appropriata o, se hai tutte le informazioni, passa alla generazione dell'output finale."""

def create_final_output_prompt(conversation_summary: str, products_catalog: str) -> str:
    """Crea il prompt per l'output finale completo"""
    return f"""Sei l'assistente AI ufficiale di Modecor. Hai raccolto tutte le informazioni necessarie.

# INFORMAZIONI RACCOLTE
{conversation_summary}

# CATALOGO PRODOTTI MODECOR
{products_catalog}

# TUO COMPITO
Genera l'OUTPUT FINALE COMPLETO seguendo questa struttura ESATTA:

---

# [TITOLO DESCRITTIVO DELLA TORTA]

[Descrizione estetica e stilistica della torta in 2-3 frasi]

---

## 🛍️ PRODOTTI MODECOR DA UTILIZZARE

[Per ogni prodotto, crea una card con questo formato:]

### [NOME PRODOTTO]
**Descrizione d'uso**: [come si usa nella torta]  
**Link prodotto**: [URL completo dal catalogo]  
**Badge**: [ESATTO ✅ o ALTERNATIVA 🔶]

[Includi da 5 a 10 prodotti pertinenti. SOLO prodotti presenti nel catalogo fornito!]

---

## 🥄 INGREDIENTI AGGIUNTIVI (non Modecor)

- [Ingrediente 1 con quantità precisa in grammi]
- [Ingrediente 2 con quantità precisa]
- ...

---

## 👨‍🍳 PROCEDURA COMPLETA STEP-BY-STEP

### **1️⃣ Preparazione della Base**
- Tipo impasto: [Pan di Spagna/Chiffon/Biscuit/ecc.] 
- Dosi precise in grammi
- Diametro e numero strati
- Temperatura e tempi di cottura

### **2️⃣ Farcitura e Assemblaggio**
- Tipo crema/mousse con quantità
- Metodo di stratificazione
- Bagne o inserti
- Tempi di raffreddamento

### **3️⃣ Copertura**
- Tecnica usata (fondente/panna/ganache/mirror glaze/ecc.)
- Coloranti Modecor specifici e applicazione
- Strumenti necessari
- Temperature ideali

### **4️⃣ Decorazione e Finitura**
- Elenco prodotti Modecor usati con posizionamento
- Sequenza di applicazione dettagliata
- Tempi di asciugatura tra passaggi

### **5️⃣ Presentazione Finale**
- Disposizione su vassoio
- Nastri o bordure
- Condizioni di conservazione
- Temperatura di servizio

---

## 📊 TABELLA RIEPILOGO

### Ingredienti Base
| Ingrediente | Quantità |
|-------------|----------|
| [Nome] | [Quantità] |
| ... | ... |

### Utensili Necessari
- [Utensile 1]
- [Utensile 2]
- ...

### Informazioni Aggiuntive
- ⏱️ **Tempo totale**: [tempo]
- ⭐ **Difficoltà**: [Base/Intermedio/Esperto]
- 🚫 **Allergeni**: [lista o "Nessuno noto"]
- 🍰 **Porzioni**: [numero]

---

## 💡 CONSIGLI PROFESSIONALI

- [Consiglio 1]
- [Consiglio 2]
- [Varianti possibili]

---

## ✨ TOCCO FINALE MODECOR

Non dimenticare di personalizzare la tua creazione con il tuo logo!  
👉 **[Mettici la firma](https://www.modecoritaliana.it/mettici-la-firma)**

---

# REGOLE CRITICHE
- USA SOLO prodotti presenti nel CATALOGO fornito sopra
- Includi SEMPRE gli URL completi esatti dal catalogo
- NON inventare prodotti o link
- Dosi PRECISE in grammi/ml/cm
- Linguaggio tecnico ma chiaro
- Formato Markdown professionale"""

def call_gpt_vision(client: OpenAI, image_base64: str, prompt: str) -> Optional[str]:
    """Chiama GPT-4 Vision per analizzare l'immagine"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ Errore chiamata GPT-4 Vision: {e}")
        return None

def call_gpt_conversation(client: OpenAI, messages: List[Dict]) -> Optional[str]:
    """Chiama GPT-4 per conversazione testuale"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ Errore chiamata GPT-4: {e}")
        return None

# -------------------------------------------------
# FUNZIONI UI
# -------------------------------------------------
def display_chat_messages():
    """Mostra tutti i messaggi della chat"""
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            st.markdown(f'<div class="chat-message user-message">👤 <strong>Tu:</strong><br>{content}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🎂 <strong>Modecor AI:</strong><br>{content}</div>', 
                       unsafe_allow_html=True)

def add_message(role: str, content: str):
    """Aggiunge un messaggio alla chat"""
    st.session_state.messages.append({"role": role, "content": content})

def get_conversation_history() -> str:
    """Ottiene la storia della conversazione come stringa"""
    history = ""
    for msg in st.session_state.messages:
        role = "Utente" if msg["role"] == "user" else "Modecor AI"
        history += f"\n{role}: {msg['content']}\n"
    return history

def create_gpt_messages_history() -> List[Dict]:
    """Crea la lista di messaggi per GPT API"""
    messages = []
    for msg in st.session_state.messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    return messages

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
def main():
    # Header
    st.markdown('<h1 class="main-title">🎂 Modecor AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Il tuo assistente intelligente per decorazioni professionali</p>', 
                unsafe_allow_html=True)
    
    # Inizializza OpenAI Client
    client = init_openai_client()
    if not client:
        st.stop()
    
    # Carica catalogo prodotti
    if st.session_state.products_catalog is None:
        with st.spinner("🔄 Caricamento catalogo Modecor..."):
            products = fetch_modecor_products()
            if products:
                st.session_state.products_catalog = products
                st.success(f"✅ Catalogo caricato: {len(products)} prodotti disponibili")
            else:
                st.error("❌ Impossibile caricare il catalogo prodotti. Riprova più tardi.")
                st.stop()
    
    # ===== FASE 1: UPLOAD IMMAGINE =====
    if st.session_state.phase == "upload":
        st.markdown("""
        <div class="upload-section">
            <h2>📸 Carica la Foto della Torta</h2>
            <p>Inizia caricando un'immagine della torta che vuoi realizzare</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Seleziona un'immagine (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Carica una foto chiara della torta che vuoi ricreare"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, caption="Immagine caricata", use_container_width=True)
            
            with col2:
                st.markdown("### ✅ Immagine pronta!")
                st.markdown("Clicca il pulsante per iniziare l'analisi AI")
                
                if st.button("🚀 Analizza Torta", use_container_width=True):
                    # Salva immagine
                    st.session_state.cake_image = uploaded_file
                    base64_img = encode_image_to_base64(uploaded_file)
                    st.session_state.image_base64 = base64_img
                    
                    # Prepara catalogo per AI
                    products_text = prepare_products_for_ai(st.session_state.products_catalog)
                    
                    # Analisi iniziale con GPT-4 Vision
                    with st.spinner("🔍 Analisi in corso con GPT-4 Vision..."):
                        initial_prompt = create_initial_analysis_prompt(products_text)
                        analysis = call_gpt_vision(
                            client,
                            st.session_state.image_base64,
                            initial_prompt
                        )
                        
                        if analysis:
                            st.session_state.initial_analysis = analysis
                            add_message("assistant", analysis)
                            st.session_state.phase = "conversation"
                            st.rerun()
    
    # ===== FASE 2: CONVERSAZIONE =====
    elif st.session_state.phase == "conversation":
        # Mostra immagine in sidebar
        with st.sidebar:
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, caption="Torta da realizzare", use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📊 Stato")
            st.markdown(f"✅ {len(st.session_state.messages)} messaggi scambiati")
            
            if st.button("🔄 Ricomincia", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Mostra fase attuale
        st.markdown('<div class="phase-indicator">💬 Conversazione in Corso - Flusso Guidato Modecor</div>', 
                   unsafe_allow_html=True)
        
        # Mostra messaggi
        display_chat_messages()
        
        # Input utente
        user_input = st.chat_input("Scrivi la tua risposta...")
        
        if user_input:
            # Aggiungi messaggio utente
            add_message("user", user_input)
            
            # Prepara prompt conversazione
            products_text = prepare_products_for_ai(st.session_state.products_catalog)
            conversation_history = get_conversation_history()
            conversation_prompt = create_conversation_prompt(conversation_history, products_text)
            
            # Prepara messaggi GPT
            gpt_msgs = create_gpt_messages_history()
            gpt_msgs.append({
                "role": "user",
                "content": conversation_prompt
            })
            
            # Chiamata GPT-4
            with st.spinner("🤔 Modecor AI sta pensando..."):
                response = call_gpt_conversation(client, gpt_msgs)
                
                if response:
                    add_message("assistant", response)
                    
                    # Verifica se è ora di generare output finale
                    if len(st.session_state.messages) > 12:
                        if any(word in user_input.lower() for word in ["sì", "si", "ok", "perfetto", "va bene", "procedi", "genera"]):
                            st.session_state.phase = "final"
            
            st.rerun()
        
        # Pulsante genera output (se conversazione avanzata)
        if len(st.session_state.messages) > 10:
            st.markdown("---")
            if st.button("✨ Genera Output Finale Completo", use_container_width=True):
                st.session_state.phase = "final"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== FASE 3: OUTPUT FINALE =====
    elif st.session_state.phase == "final":
        with st.sidebar:
            if st.session_state.cake_image:
                st.image(st.session_state.cake_image, caption="Torta da realizzare", use_container_width=True)
            
            if st.button("🔄 Nuova Torta", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown('<div class="phase-indicator">✨ Generazione Output Finale...</div>', 
                   unsafe_allow_html=True)
        
        with st.spinner("🎂 Sto creando la tua guida completa personalizzata..."):
            # Prepara summary conversazione
            conversation_summary = get_conversation_history()
            products_text = prepare_products_for_ai(st.session_state.products_catalog)
            
            # Genera output finale
            final_prompt = create_final_output_prompt(conversation_summary, products_text)
            
            gpt_msgs = [{
                "role": "user",
                "content": final_prompt
            }]
            
            final_output = call_gpt_conversation(client, gpt_msgs)
            
            if final_output:
                st.markdown('<div class="final-output">', unsafe_allow_html=True)
                st.markdown(final_output, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Pulsanti azione
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📥 Scarica Ricetta",
                        data=final_output,
                        file_name="modecor_ricetta.md",
                        mime="text/markdown"
                    )
                
                with col2:
                    if st.button("📧 Invia via Email", use_container_width=True):
                        st.info("Funzionalità in arrivo!")
                
                with col3:
                    if st.button("🔄 Nuova Torta", use_container_width=True):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()

if __name__ == "__main__":
    main()
