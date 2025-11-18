import streamlit as st
import requests
from bs4 import BeautifulSoup

DPD_URL = "https://tracktrace.dpd.com.pl/findParcel?query={}&lang=pl_pl"

st.set_page_config(page_title="DPD Tracker", page_icon="📦")

st.title("📦 DPD Tracker – Śledzenie przesyłek bez limitów")

tracking_number = st.text_input("Podaj numer przesyłki DPD:")

def fetch_dpd_status(number: str):
    url = DPD_URL.format(number)
    response = requests.get(url)

    if response.status_code != 200:
        return None, "Błąd połączenia z serwerem DPD."

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="table")

    if not table:
        return None, "Brak danych — numer nie istnieje lub DPD zmieniło stronę."

    events = []
    for row in table.find("tbody").find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 3:
            events.append({
                "date": cols[0].text.strip(),
                "place": cols[1].text.strip(),
                "status": cols[2].text.strip()
            })

    return events, None


if st.button("🔍 Sprawdź status"):
    if not tracking_number:
        st.warning("Podaj numer przesyłki!")
    else:
        with st.spinner("Pobieram dane z DPD..."):
            events, error = fetch_dpd_status(tracking_number)

        if error:
            st.error(error)
        else:
            st.success(f"Znaleziono {len(events)} zdarzeń!")

            for event in events:
                st.markdown(
                    "**📅 {}**  \n🏢 *{}*  \n➡️ {}".format(
                        event["date"], event["place"], event["status"]
                    )
                )
                st.markdown("---")
