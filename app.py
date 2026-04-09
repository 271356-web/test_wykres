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

# 3. Funkcja do inteligentnego wczytywania danych
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        # Podejrzyj pierwszą linię, żeby sprawdzić separator
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
        
        # Jeśli w pliku jest przecinek, to CSV. Jeśli nie, to spacje/taby.
        sep = ',' if ',' in first_line else r'\s+'
        
        # Wczytanie pliku
        df = pd.read_csv(file_path, sep=sep, header=None, engine='python')
        
        # Konwersja na liczby i usunięcie pustych wierszy/nieliczbowych danych
        df = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        return df if not df.empty else None
    except Exception as e:
        st.sidebar.error(f"Błąd w pliku {file_path}: {e}")
        return None

# 4. Budowanie wykresu
fig = go.Figure()

if not wybrane_scenariusze:
    st.warning("Zaznacz co najmniej jeden scenariusz w panelu bocznym.")
else:
    for nazwa in wybrane_scenariusze:
        # --- CZĘŚĆ A: PUNKTY (Separator: Spacje) ---
        df_pkt = load_data(scenariusze[nazwa])
        if df_pkt is not None:
            # Używamy kolumny 4 (B) jako X i kolumny 0 (G) jako Y
            fig.add_trace(go.Scatter(
                x=df_pkt[4] if 4 in df_pkt.columns else df_pkt[0],
                y=df_pkt[0],
                mode='markers',
                name=f"{nazwa} (punkty)",
                marker=dict(opacity=0.6, size=8),
                hovertext=df_pkt[5] if len(df_pkt.columns) > 5 else ""
            ))
        
        # --- CZĘŚĆ B: KRZYWA MID (Separator: Przecinki) ---
        df_mid = load_data(Krzywe_mid[nazwa])
        if df_mid is not None and len(df_mid.columns) >= 2:
            # Sortujemy po osi X (kolumna 0), żeby linia nie skakała
            df_mid = df_mid.sort_values(by=0)
            
            # Filtr dla skali logarytmicznej (usuwamy wartości Y <= 0)
            df_mid_plot = df_mid[df_mid[1] > 0]
            
            fig.add_trace(go.Scatter(
                x=df_mid_plot[0],
                y=df_mid_plot[1],
                mode='lines',
                name=f"{nazwa} (krzywa MID)",
                line=dict(width=3)
            ))
        elif df_mid is None:
            st.sidebar.warning(f"Nie znaleziono pliku krzywej dla: {nazwa}")

    # Konfiguracja osi i wyglądu
    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# 5. Podgląd danych (opcjonalnie)
if st.checkbox("Pokaż tabele danych (Debug)"):
    for nazwa in wybrane_scenariusze:
        st.write(f"### {nazwa}")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Punkty (Spacje):")
            st.dataframe(load_data(scenariusze[nazwa]).head(5) if load_data(scenariusze[nazwa]) is not None else "Brak")
        with c2:
            st.write("Krzywa (Przecinki):")
            st.dataframe(load_data(Krzywe_mid[nazwa]).head(5) if load_data(Krzywe_mid[nazwa]) is not None else "Brak")
