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
            # Resetujemy indeks, aby "index" stał się kolumną z numerem wiersza
            df_p = df_p.reset_index()
    
            # Przygotowujemy dane do przekazania: [numer_wiersza, opcjonalny_tekst]
            # Jeśli chcesz numerację od 1 (jak w notatniku), użyj: df_p['index'] + 1
            c_data = df_p[['index', 5]].values if 5 in df_p.columns else df_p[['index', 0]].values

            fig.add_trace(go.Scatter(
                x=df_p[4] if 4 in df_p.columns else df_p[0],
                y=df_p[0],
                mode='markers',
                name=f"{nazwa} (Pkt)",
                customdata=c_data, 
                # Wyłączamy pokazywanie wiersza w dymku (hover), by był widoczny TYLKO po kliknięciu
                hovertemplate="B: %{x}<br>Y: %{y}<extra></extra>"
            ))
        
        # --- KRZYWE (Mid, Down, Up) ---
        # (Tutaj dodaj swój kod rysowania linii - bez zmian)
        # Pamiętaj, aby dla linii ustawić hoverinfo='skip', żeby nie przeszkadzały w klikaniu punktów

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        clickmode='event+select' # Ważne dla obsługi kliknięć
    )

    # KLUCZOWY MOMENT: Wykorzystanie st.plotly_chart z obsługą zdarzeń
    # Używamy on_select="rerun", aby Streamlit odświeżył stronę po kliknięciu
    selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

   # --- 5. DANE POD WYKRESEM (Tylko po kliknięciu) ---
    if selected_data and "selection" in selected_data and len(selected_data["selection"]["points"]) > 0:
        st.success("✅ Dane dla wybranego punktu:")
        
        for point in selected_data["selection"]["points"]:
            row_num = point['customdata'][0]
            point_info = point['customdata'][1]
            
            # Tworzymy ładną tabelkę lub metryki
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📍 Numer wiersza w TXT", int(row_num))
            with col2:
                st.metric("Oś X (B)", f"{point['x']:.4f}")
            with col3:
                st.metric("Oś Y", f"{point['y']:.4e}")
            
            if point_info:
                st.write(f"**Dodatkowy opis:** {point_info}")
            st.divider()
    else:
        st.info("👆 Kliknij konkretny punkt na wykresie powyżej, aby zobaczyć, w którym wierszu pliku się znajduje.")
