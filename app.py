import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="Gravity Analysis - Scenariusze")
st.title("Analiza porównawcza scenariuszy")

# 1. Definicja scenariuszy i ścieżek do plików
scenariusze = {
    "Scenariusz 1 (1m)": "dane/wynik_1m.txt",
    "Scenariusz 2 (5m)": "dane/wynik_5m.txt",
    "Scenariusz 3 (10m)": "dane/wynik_10m.txt",
    "Scenariusz 4 (1m SB)": "dane/wynik_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/wynik_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/wynik_10m_sb.txt"
}
Krzywe_mid = {
    "Scenariusz 1 (1m)": "dane/mid_curve_1m_mc.txt",
    "Scenariusz 2 (5m)": "dane/mid_curve_5m_mc.txt",
    "Scenariusz 3 (10m)": "dane/mid_curve_10m_mc.txt",
    "Scenariusz 4 (1m SB)": "dane/mid_curve_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/mid_curve_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/mid_curve_10m_sb.txt"
}

# 2. Tworzenie checkboxów w panelu bocznym
st.sidebar.header("Wybierz scenariusze")
wybrane_scenariusze = []
for nazwa in scenariusze.keys():
    if st.sidebar.checkbox(nazwa, value=(nazwa == "Scenariusz 1 (1m)")):
        wybrane_scenariusze.append(nazwa)

# 3. Funkcja do bezpiecznego wczytywania danych
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            data = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    data.append(parts)
            
            df = pd.DataFrame(data)
            for col in df.columns:
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
        # --- CZĘŚĆ A: PUNKTY (Główny scenariusz) ---
        df_pkt = load_data(scenariusze[nazwa])
        if df_pkt is not None and not df_pkt.empty:
            fig.add_trace(go.Scatter(
                x=df_pkt[4] if 4 in df_pkt.columns else df_pkt[0], 
                y=df_pkt[0], 
                mode='markers',
                name=f"{nazwa} (punkty)",
                marker=dict(opacity=0.6),
                hovertext=df_pkt[5] if len(df_pkt.columns) > 5 else ""
            ))
        
        # --- CZĘŚĆ B: KRZYWA (Mid Curve) ---
        df_mid = load_data(Krzywe_mid[nazwa])
        if df_mid is not None and len(df_mid.columns) >= 2:
            fig.add_trace(go.Scatter(
                x=df_mid[0], 
                y=df_mid[1], 
                mode='lines',
                name=f"{nazwa} (krzywa MID)",
                line=dict(width=2)
            ))

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

# 5. Podgląd tabelaryczny
if st.checkbox("Pokaż tabele danych"):
    for nazwa in wybrane_scenariusze:
        st.write(f"Dane dla: {nazwa}")
        d = load_data(scenariusze[nazwa])
        if d is not None:
            st.dataframe(d.head(10))
