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
# --- 2. Krzywa Mid (linia) ---
        df_mid = load_data(Krzywe_mid[nazwa])
        
        # Sprawdzamy czy df istnieje i czy ma jakiekolwiek kolumny/wiersze
        if df_mid is not None and not df_mid.empty:
            try:
                fig.add_trace(go.Scatter(
                    x=df_mid[0], 
                    y=df_mid[1], 
                    mode='lines',
                    name=f"{nazwa} (krzywa mid)",
                    line=dict(dash='solid')
                ))
            except KeyError:
                st.sidebar.warning(f"Plik {Krzywe_mid[nazwa]} ma niewłaściwy format (brak kolumn 0 i 1).")

# 3. Poprawiona funkcja do wczytywania danych
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            data = []
            for line in lines:
                parts = line.strip().split() # Usuwamy maxsplit, by brać wszystko
                if len(parts) >= 2: # Zmieniamy na minimum 2 kolumny (dla X i Y)
                    data.append(parts)
            
            df = pd.DataFrame(data)
            # Konwersja dostępnych kolumn na liczby
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
        # --- 1. Dane główne (punkty) ---
        df_points = load_data(scenariusze[nazwa])
        if df_points is not None:
            fig.add_trace(go.Scatter(
                x=df_points[4], # Kolumna B
                y=df_points[0], # Kolumna G
                mode='markers',
                name=f"{nazwa} (punkty)",
                marker=dict(opacity=0.6),
                hovertext=df_points[5] if len(df_points.columns) > 5 else ""
            ))
        
        # --- 2. Krzywa Mid (linia) ---
        df_mid = load_data(Krzywe_mid[nazwa])
        if df_mid is not None:
            fig.add_trace(go.Scatter(
                x=df_mid[0], # X dla krzywej
                y=df_mid[1], # Y dla krzywej
                mode='lines', # Krzywe lepiej rysować linią
                name=f"{nazwa} (krzywa mid)",
                line=dict(dash='solid') # Możesz użyć 'dash', 'dot' itp.
            ))
            
    # Konfiguracja osi
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




