import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. KONFIGURACJA ---
st.set_page_config(layout="wide", page_title="Gravity Analysis")
st.title("Analiza porównawcza scenariuszy")

# --- 2. FUNKCJA WCZYTYWANIA DANYCH (ULEPSZONA) ---
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        # Wczytujemy surowe dane, żeby nie psuć struktury indeksami
        df = pd.read_csv(file_path, sep=',', header=None, engine='python', on_bad_lines='skip')
        
        # Zamiast insert, dodajmy numer wiersza jako atrybut, nie zmieniając kolumn danych
        # Dzięki temu df[0] to zawsze pierwsza kolumna z pliku
        df['orig_row_index'] = range(1, len(df) + 1)
        
        return df
    except Exception as e:
        st.error(f"Błąd pliku {file_path}: {e}")
        return None

# --- 3. ŚCIEŻKI ---
scenariusze = {
    "Scenariusz 1 (1m)": "dane/wynik_1m.txt",
    "Scenariusz 2 (5m)": "dane/wynik_5m.txt",
    "Scenariusz 3 (10m)": "dane/wynik_10m.txt",
    "Scenariusz 4 (1m SB)": "dane/wynik_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/wynik_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/wynik_10m_sb.txt"
}

Krzywe_mid = {k: v.replace('wynik_', 'mid_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_up = {k: v.replace('wynik_', 'up_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_down = {k: v.replace('wynik_', 'down_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}

# --- 4. SIDEBAR ---
st.sidebar.header("Scenariusze")
wybrane_scenariusze = [n for n in scenariusze.keys() if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)"))]

# --- 5. WYKRES GŁÓWNY ---
if not wybrane_scenariusze:
    st.warning("Wybierz scenariusz.")
else:
    fig = go.Figure()

    for nazwa in wybrane_scenariusze:
        # PUNKTY
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            # Zakładamy standard: Col 1 = Y, Col 5 = X, Col 6 = Info
            # W Pandas po read_csv (bez nagłówka) to są indeksy: 0, 4, 5
            try:
                y_val = pd.to_numeric(df_p[0], errors='coerce') # Pierwotna kolumna 1
                x_val = pd.to_numeric(df_p[4], errors='coerce') # Pierwotna kolumna 5
                info_val = df_p[5] if 5 in df_p.columns else "" # Pierwotna kolumna 6
                
                mask = y_val > 0 # Dla skali logarytmicznej
                
                fig.add_trace(go.Scatter(
                    x=x_val[mask], y=y_val[mask],
                    mode='markers',
                    name=f"{nazwa} (Pkt)",
                    customdata=list(zip(df_p['orig_row_index'][mask], info_val[mask])),
                    hovertemplate="B: %{x}<br>Y: %{y}<extra></extra>"
                ))
            except Exception as e:
                st.error(f"Błąd formatu danych w {nazwa}: {e}")

        # KRZYWE
        def add_curve(file_dict, suffix, color, dash=None):
            df_c = load_data(file_dict[nazwa])
            if df_c is not None and len(df_c.columns) >= 2:
                # Krzywe: Col 1 = X (indeks 0), Col 2 = Y (indeks 1)
                x_c = pd.to_numeric(df_c[0], errors='coerce')
                y_c = pd.to_numeric(df_c[1], errors='coerce')
                
                c_mask = y_c > 0
                fig.add_trace(go.Scatter(
                    x=x_c[c_mask], y=y_c[c_mask],
                    mode='lines', name=f"{nazwa} {suffix}",
                    line=dict(color=color, width=1, dash=dash),
                    hoverinfo='skip'
                ))

        add_curve(Krzywe_mid, "MID", "black")
        add_curve(Krzywe_up, "UP", "gray", "dash")
        add_curve(Krzywe_down, "DOWN", "gray", "dash")

    fig.update_layout(
        yaxis_type="log", xaxis_title="B [m]", yaxis_title="Multiplier",
        height=600, template="plotly_white", clickmode='event+select'
    )

    selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # --- 6. DETALE ---
    if selected and "selection" in selected and len(selected["selection"]["points"]) > 0:
        for point in selected["selection"]["points"]:
            row_nr, row_desc = point['customdata']
            st.write(f"### Punkt z wiersza: {row_nr}")
            
            c1, c2 = st.columns(2)
            c1.metric("X (B)", point['x'])
            c2.metric("Y (Multiplier)", f"{point['y']:.4e}")

            # Wykres profilu
            df_k = load_data("dane_kord.txt")

if selected and "selection" in selected and len(selected["selection"]["points"]) > 0:
    for point in selected["selection"]["points"]:
        # Bezpieczne pobieranie customdata
        custom_data = point.get('customdata', [None, None])
        row_nr, row_desc = custom_data
        
        st.write(f"### Punkt z wiersza: {row_nr}")
        # ... reszta kodu ...

        if df_k is not None:
            try:
                # Bezpieczniejsza konwersja
                p_idx = int(float(str(row_desc).strip()))
                cx, cy = 2 * p_idx, 2 * p_idx + 1
                
                # Sprawdzenie czy kolumny istnieją w df_k
                if cx in df_k.columns and cy in df_k.columns:
                    sub = go.Figure()
                    sub.add_trace(go.Scatter(x=df_k[cx], y=df_k[cy], mode='lines+markers'))
                    # ...
                else:
                    st.warning(f"Brak kolumn dla profilu {p_idx}")
            except (ValueError, TypeError):
                st.info("Opis punktu nie jest poprawnym numerem profilu.")
