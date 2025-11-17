import requests
from requests.auth import HTTPBasicAuth
import urllib3

# disabilita i warning "InsecureRequestWarning"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MODECOR_URL = "https://www.modecoritaliana.it/tools/api/it-get-products.php"
MODECOR_USERNAME = "modecorapis"
MODECOR_PASSWORD = "#M0d3CoR2025!"


def call_modecor_products():
    """
    Chiama l'endpoint prodotti Modecor con autenticazione Basic.
    Restituisce il testo grezzo della risposta o solleva eccezione.
    """
    response = requests.get(
        MODECOR_URL,
        auth=HTTPBasicAuth(MODECOR_USERNAME, MODECOR_PASSWORD),
        timeout=30,
        verify=False,  # <--- AGGIUNTO: non verifica il certificato SSL
    )
    response.raise_for_status()
    return response.text

# -------------------------------------------------
# UI: PULSANTE PER CHIAMARE L'API
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
            raw_output = call_modecor_products()

            st.success("Risposta ricevuta dall'API Modecor.")
            st.markdown("### Output grezzo (prime 10.000 battute):")
            st.code(raw_output[:10000], language="text")

        except requests.exceptions.HTTPError as e:
            st.error(f"Errore HTTP nella chiamata all'API Modecor: {e}")
        except requests.exceptions.Timeout:
            st.error("Timeout nella chiamata all'API Modecor.")
        except requests.exceptions.RequestException as e:
            st.error(f"Errore di rete: {e}")
        except Exception as e:
            st.error(f"Errore imprevisto: {e}")
else:
    st.info("Premi il pulsante per effettuare la chiamata all'API Modecor.")
