import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="Gravity Analysis - Scenariusze")
st.title("Analiza porównawcza scenariuszy")

# 1. Definicja scenariuszy i ścieżek do plików
# Możesz to dostosować do swoich rzeczywistych nazw folderów i plików
scenariusze = {
    "Scenariusz 1 (1m)": "dane/wynik_1m.txt",
    "Scenariusz 2 (5m)": "dane/wynik_5m.txt",
    "Scenariusz 3 (10m)": "dane/wynik_10m.txt",
    "Scenariusz 4 (1m SB)": "dane/wynik_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/wynik_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/wynik_10m_sb.txt"
}

# 2. Tworzenie checkboxów w panelu bocznym
st.sidebar.header("Wybierz scenariusze")
wybrane_scenariusze = []
for nazwa in scenariusze.keys():
    if st.sidebar.checkbox(nazwa, value=(nazwa == "Scenariusz 1 (1m)")):
        wybrane_scenariusze.append(nazwa)

# 3. Funkcja do bezpiecznego wczytywania danych (twoja sprawdzona metoda)
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            data = []
            for line in lines:
                parts = line.strip().split(maxsplit=5)
                if len(parts) >= 5:
                    data.append(parts)
            df = pd.DataFrame(data)
            # Konwersja na liczby dla pierwszych 5 kolumn
            for col in df.columns[:5]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            st.sidebar.error(f"Błąd wczytywania {file_path}: {e}")
    return None

# 4. Budowanie wykresu
fig = go.Figure()

if not wybrane_scenariusze:
    st.warning("Zaznacz co najmniej jeden scenariusz w panelu bocznym.")
else:
    for nazwa in wybrane_scenariusze:
        sciezka = scenariusze[nazwa]
        df = load_data(sciezka)
        
        if df is not None:
            # Dodajemy serię danych do wykresu
            fig.add_trace(go.Scatter(
                x=df[4], # Kolumna B
                y=df[0], # Kolumna G
                mode='markers',
                name=nazwa,
                marker=dict(opacity=0.6),
                hovertext=df[5] if len(df.columns) > 5 else "" # Nazwa ze spacjami
            ))

    # Konfiguracja osi i wyglądu
    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

# 5. Opcjonalnie: podgląd tabelaryczny dla zaznaczonych danych
if st.checkbox("Pokaż tabele danych dla zaznaczonych scenariuszy"):
    for nazwa in wybrane_scenariusze:
        st.write(f"Dane dla: {nazwa}")
        st.dataframe(load_data(scenariusze[nazwa]).head(10)) # pokazujemy pierwsze 10 wierszyimport streamlit as st




