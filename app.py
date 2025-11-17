import requests
from requests.auth import HTTPBasicAuth
import urllib3
import streamlit as st

# -------------------------------------------------
# DISABILITA WARNING SSL INSECURE (necessario con verify=False)
# -------------------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------------------------
# CONFIGURAZIONE STREAMLIT
# -------------------------------------------------
st.set_page_config(
    page_title="Modecor API Viewer",
    page_icon="🧁",
    layout="wide",
)

st.title("Modecor – Lettura prodotti via API")
st.write(
    "Clicca il pulsante qui sotto per chiamare l'API "
    "`it-get-products.php` di Modecor con autenticazione Basic."
)

# -------------------------------------------------
# CREDENZIALI API MODECOR
# -------------------------------------------------
MODECOR_URL = "https://www.modecoritaliana.it/tools/api/it-get-products.php"
MODECOR_USERNAME = "modecorapis"
MODECOR_PASSWORD = "#M0d3CoR2025!"

# User-Agent “da browser” per evitare blocchi del firewall
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def call_modecor_products():
    return requests.get(
        MODECOR_URL,
        auth=HTTPBasicAuth(MODECOR_USERNAME, MODECOR_PASSWORD),
        headers=HEADERS,
        timeout=30,
        verify=True,
    )


# -------------------------------------------------
# UI STREAMLIT: PULSANTE CHIAMATA API
# -------------------------------------------------

st.subheader("Chiamata API prodotti")

if st.button("🔄 Chiama API Modecor"):
    with st.spinner("Chiamata in corso..."):
        try:
            resp = call_modecor_products()

            st.markdown(f"**HTTP status code:** `{resp.status_code}`")

            if resp.status_code == 200:
                st.success("Prodotti ricevuti! Ecco TUTTA la risposta dell’API.")
                
                # MOSTRA TUTTO IL TESTO SENZA TRONCARE NIENTE
                st.markdown("### Output completo dell'API:")
                st.text_area(
                    "Risultato API (scrollabile)",
                    value=resp.text,
                    height=700,   # altezza regolabile
                )

            else:
                st.error(f"Errore: status code {resp.status_code}")
                st.code(resp.text, language="html")

        except Exception as e:
            st.error(f"Errore durante la chiamata: {e}")
else:
    st.info("Premi il pulsante per effettuare la chiamata all'API Modecor.")
