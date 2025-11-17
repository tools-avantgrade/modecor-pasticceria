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
    page_icon="🧁",  # icona della tab del browser
    layout="wide"
)

st.title("Modecor – Lettura prodotti via API")
st.write(
    "Clicca il pulsante qui sotto per chiamare l'API "
    "`it-get-products.php` di Modecor con autenticazione Basic."
)

# -------------------------------------------------
# CREDENZIALI API MODECOR (come da tua richiesta)
# -------------------------------------------------
MODECOR_URL = "https://www.modecoritaliana.it/tools/api/it-get-products.php"
MODECOR_USERNAME = "modecorapis"
MODECOR_PASSWORD = "#M0d3CoR2025!"

# User-Agent “da browser” per evitare blocchi banali lato server/WAF
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def call_modecor_products():
    """
    Chiama l'endpoint prodotti Modecor con autenticazione Basic.
    Restituisce l'oggetto Response di requests.
    """
    response = requests.get(
        MODECOR_URL,
        auth=HTTPBasicAuth(MODECOR_USERNAME, MODECOR_PASSWORD),
        headers=HEADERS,
        timeout=30,
        verify=False,  # <<--- certificato SSL non verificato
    )
    return response


# -------------------------------------------------
# UI STREAMLIT: PULSANTE CHIAMATA API
# -------------------------------------------------

st.subheader("Chiamata API prodotti")

st.caption(
    "Endpoint chiamato:\n\n"
    f"`{MODECOR_URL}`\n\n"
    "Metodo: `GET` con autenticazione Basic (username/password)."
)

if st.button("🔄 Chiama API Modecor"):
    with st.spinner("Chiamata in corso..."):
        try:
            resp = call_modecor_products()

            st.markdown(f"**HTTP status code:** `{resp.status_code}`")

            if resp.status_code == 200:
                st.success("Risposta ricevuta dall'API Modecor (200 OK).")
                st.markdown("### Output grezzo (prime 10.000 battute):")
                st.code(resp.text[:10000], language="text")
            else:
                st.error(
                    f"Chiamata completata ma il server ha risposto con codice "
                    f"non OK: {resp.status_code}"
                )

                st.markdown("### Corpo della risposta (utile per capire il 403/errori):")
                st.code(resp.text[:8000], language="html")

                st.markdown("### Header di risposta (debug):")
                st.json(dict(resp.headers))

        except requests.exceptions.Timeout:
            st.error("Timeout nella chiamata all'API Modecor.")
        except requests.exceptions.RequestException as e:
            st.error(f"Errore di rete: {e}")
        except Exception as e:
            st.error(f"Errore imprevisto: {e}")
else:
    st.info("Premi il pulsante per effettuare la chiamata all'API Modecor.")
