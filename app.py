import streamlit as st
import requests

st.set_page_config(page_title="DPD Tracker Online", page_icon="📦")
st.title("📦 DPD Tracker — Online Version")

# Twój backend Railway
backend_url = "https://ggg-production.up.railway.app"

# Pole do wpisania numeru paczki
tracking_number = st.text_input("Numer paczki DPD:")

if st.button("🔍 Sprawdź status"):
    if not tracking_number:
        st.warning("Podaj numer paczki")
    else:
        try:
            # Wywołanie backendu
            response = requests.get(f"{backend_url}/track/{tracking_number}", timeout=30)
            data = response.json()

            if data.get("success"):
                st.success(f"Znaleziono {len(data['events'])} zdarzeń dla paczki {tracking_number}!")
                for e in data["events"]:
                    st.markdown(f"**📅 {e['date']}**  \n🏢 *{e['place']}*  \n➡️ {e['status']}")
                    st.markdown("---")
            else:
                st.error("Nie udało się pobrać danych: " + str(data))
        except Exception as ex:
            st.error("Błąd połączenia z backendem: " + str(ex))
