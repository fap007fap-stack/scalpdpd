import streamlit as st
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://tracktrace.dpd.com.pl/findParcel?query={}&lang=pl_pl"

st.set_page_config(page_title="DPD Tracker", page_icon="📦")
st.title("📦 DPD Tracker – ulepszona wersja (pełny scraping)")

tracking_number = st.text_input("Podaj numer przesyłki DPD:")

DEBUG = st.checkbox("Pokaż surowy HTML (debug)")


def fetch_dpd(number: str):
    url = BASE_URL.format(number)
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if resp.status_code != 200:
        return None, "Błąd pobierania strony DPD."

    html = resp.text

    if DEBUG:
        st.text_area("HTML zwrócony przez DPD:", html, height=300)

    soup = BeautifulSoup(html, "html.parser")

    # 1️⃣ Najpierw szukamy klasycznej tabeli
    table = soup.find("table")
    events = []

    if table:
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                cols = tr.find_all("td")
                if len(cols) >= 3:
                    events.append({
                        "date": cols[0].text.strip(),
                        "place": cols[1].text.strip(),
                        "status": cols[2].text.strip(),
                    })

    # 2️⃣ Jeśli tabela nie istnieje — szukamy komunikatów DPD
    if not events:
        possible_boxes = soup.find_all(["p", "div", "span"])
        messages = []

        for tag in possible_boxes:
            text = tag.get_text(strip=True)
            if "brak" in text.lower() or "nie znaleziono" in text.lower() or "nie można" in text.lower():
                messages.append(text)

        if messages:
            return None, messages[0]

    # 3️⃣ Jeśli nadal nic — numer może być nieobsługiwany lub układ inny
    if not events:
        return None, "Brak dostępnych danych dla tego numeru. Możliwe, że DPD zmieniło układ lub numer jest zagraniczny."

    return events, None


if st.button("🔍 Sprawdź status"):
    if not tracking_number:
        st.warning("Podaj numer!")
    else:
        with st.spinner("Łączę z DPD..."):
            events, error = fetch_dpd(tracking_number)

        if error:
            st.error(error)
        else:
            st.success("Znaleziono dane!")

            for e in events:
                st.markdown(
                    f"""
                    **📅 {e['date']}**  
                    🏢 _{e['place']}_  
                    ➡️ {e['status']}
                    """
                )
                st.markdown("---")
