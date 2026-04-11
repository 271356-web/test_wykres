import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- KONFIGURACJA ---
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
# 2. Sidebar - Wybór scenariuszy
st.sidebar.header("Wybierz scenariusze")
wybrane_scenariusze = []
for n in scenariusze.keys():
    if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)")):
        wybrane_scenariusze.append(n)

# 3. Funkcja wczytywania danych z zachowaniem numeru wiersza
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        data = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            # i+1 to fizyczny numer wiersza w pliku txt
            if ',' in line:
                parts = [i + 1] + line.split(',')
            else:
                parts = [i + 1] + line.split(None, 5)
            
            if len(parts) >= 3:
                data.append(parts)
        
        df = pd.DataFrame(data)
        
        # Konwersja na liczby tam gdzie się da
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if not converted.isna().all():
                df[col] = converted
        return df
    except Exception as e:
        st.sidebar.error(f"Błąd w {file_path}: {e}")
        return None

# --- 4. GŁÓWNA LOGIKA WYKRESU ---
if not wybrane_scenariusze:
    st.warning("Zaznacz scenariusz w panelu bocznym.")
else:
    fig = go.Figure()

    for nazwa in wybrane_scenariusze:
        # --- PUNKTY ---
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            # Kolumny po dodaniu numeru wiersza na początku:
            # [0] - Nr wiersza, [1] - G (Y), [5] - B (X), [6] - Nazwa/Info
            
            y_val = df_p[1]
            x_val = df_p[5] if 5 in df_p.columns else df_p[1]
            txt_info = df_p[6] if 6 in df_p.columns else ""
            
            fig.add_trace(go.Scatter(
                x=x_val,
                y=y_val,
                mode='markers',
                name=f"{nazwa}",
                marker=dict(size=6),
                # Przekazujemy numer wiersza i info do customdata
                customdata=pd.concat([df_p[0], txt_info], axis=1),
                hovertemplate="B: %{x}<br>Y: %{y}<extra></extra>"
            ))

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        clickmode='event+select'
    )

    # Rysowanie wykresu i przechwycenie kliknięcia
    selected_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # --- 5. WYŚWIETLANIE DANYCH PO KLIKNIĘCIU ---
    # Ta sekcja musi być wewnątrz 'else', żeby widzieć 'selected_data'
    if selected_data and "selection" in selected_data and len(selected_data["selection"]["points"]) > 0:
        st.markdown("---")
        st.subheader("🔍 Szczegóły wybranego punktu")
        
        for point in selected_data["selection"]["points"]:
            # Pobieramy dane z customdata (zdefiniowane w fig.add_trace)
            row_nr = point['customdata'][0]
            row_desc = point['customdata'][1]
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Numer wiersza (TXT)", int(row_nr))
            with c2:
                st.metric("Współrzędna B (X)", f"{point['x']:.4f}")
            with c3:
                st.metric("Multiplier (Y)", f"{point['y']:.4e}")
            
            if row_desc:
                st.info(f"**Informacja z pliku:** {row_desc}")
            st.divider()
    else:
        st.info("💡 Kliknij punkt na wykresie, aby zobaczyć jego lokalizację w pliku źródłowym.")
