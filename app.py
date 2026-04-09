import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="Gravity Analysis")
st.title("Analiza porównawcza scenariuszy")

# 1. Ścieżki do plików
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
Krzywe_up = {
    "Scenariusz 1 (1m)": "dane/up_curve_1m_mc.txt",
    "Scenariusz 2 (5m)": "dane/up_curve_5m_mc.txt",
    "Scenariusz 3 (10m)": "dane/up_curve_10m_mc.txt",
    "Scenariusz 4 (1m SB)": "dane/up_curve_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/up_curve_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/up_curve_10m_sb.txt"
}
Krzywe_down = {
    "Scenariusz 1 (1m)": "dane/down_curve_1m_mc.txt",
    "Scenariusz 2 (5m)": "dane/down_curve_5m_mc.txt",
    "Scenariusz 3 (10m)": "dane/down_curve_10m_mc.txt",
    "Scenariusz 4 (1m SB)": "dane/down_curve_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/down_curve_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/down_curve_10m_sb.txt"
}
# 2. Sidebar
st.sidebar.header("Wybierz scenariusze")
wybrane_scenariusze = [n for n in scenariusze.keys() if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)"))]

# 3. Inteligentna funkcja wczytywania
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        data = []
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Sprawdzamy separator: jeśli jest przecinek, to CSV (krzywe)
            if ',' in line:
                parts = line.split(',')
            else:
                # Pliki wynikowe: 4 kolumny liczb + reszta to nazwa
                # split(None, 5) dzieli na maksymalnie 6 części (indeksy 0-5)
                parts = line.split(None, 5)
            
            if len(parts) >= 2:
                data.append(parts)
        
        df = pd.DataFrame(data)
        
        # Konwersja kolumn na liczby (tylko te, które się da)
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if not converted.isna().all(): # Jeśli kolumna zawiera liczby
                df[col] = converted
        
        return df.dropna(subset=[df.columns[0]]) # Usuwamy wiersze bez pierwszej liczby
    except Exception as e:
        st.sidebar.error(f"Błąd w {file_path}: {e}")
        return None

# 4. Wykres
fig = go.Figure()

if not wybrane_scenariusze:
    st.warning("Zaznacz scenariusz w panelu bocznym.")
else:
    for nazwa in wybrane_scenariusze:
        # --- PUNKTY (Wyniki) ---
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            # Twoja struktura: x=kolumna 4 (B), y=kolumna 0 (G)
            # Jeśli nazwa ma spacje, będzie w kolumnie 5
            fig.add_trace(go.Scatter(
                x=df_p[4] if 4 in df_p.columns else df_p[0],
                y=df_p[0],
                mode='markers',
                name=f"{nazwa} (Pkt)",
                hovertext=df_p[5] if 5 in df_p.columns else ""
            ))
        
        # --- KRZYWA (Mid) ---
        df_m = load_data(Krzywe_mid[nazwa])
        if df_m is not None:
            df_m = df_m.sort_values(by=0)
            df_m_plot = df_m[df_m[1] > 0] # Filtr dla skali log
            fig.add_trace(go.Scatter(
                x=df_m_plot[0], y=df_m_plot[1],
                mode='lines',
                name=f"{nazwa} (MID)",
                line=dict(width=3, color='black')
            ))
        # --- KRZYWA (Down) ---
        df_m = load_data(Krzywe_down[nazwa])
        if df_m is not None:
            df_m = df_m.sort_values(by=0)
            df_m_plot = df_m[df_m[1] > 0] # Filtr dla skali log
            fig.add_trace(go.Scatter(
                x=df_m_plot[0], y=df_m_plot[1],
                mode='lines',
                name=f"{nazwa} (MID)",
                line=dict(width=3, color='black')
            ))
        # --- KRZYWA (Up) ---
        df_m = load_data(Krzywe_up[nazwa])
        if df_m is not None:
            df_m = df_m.sort_values(by=0)
            df_m_plot = df_m[df_m[1] > 0] # Filtr dla skali log
            fig.add_trace(go.Scatter(
                x=df_m_plot[0], y=df_m_plot[1],
                mode='lines',
                name=f"{nazwa} (MID)",
                line=dict(width=3, color='black')
            ))

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700
    )
    st.plotly_chart(fig, use_container_width=True)
