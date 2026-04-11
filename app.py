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
Krzywe_mid = {k: v.replace('wynik_', 'mid_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_up = {k: v.replace('wynik_', 'up_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_down = {k: v.replace('wynik_', 'down_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}

# Uwaga: Jeśli Twoje pliki krzywych mają inne nazwy, użyj swoich oryginalnych słowników Krzywe_mid, up, down.

# 2. Sidebar - Wybór scenariuszy
st.sidebar.header("Wybierz scenariusze")
wybrane_scenariusze = []
for n in scenariusze.keys():
    if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)")):
        wybrane_scenariusze.append(n)

# 3. Funkcja wczytywania danych
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
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if not converted.isna().all():
                df[col] = converted
        return df
    except Exception as e:
        return None

# --- 4. GŁÓWNA LOGIKA WYKRESU ---
if not wybrane_scenariusze:
    st.warning("Zaznacz scenariusz w panelu bocznym.")
else:
    fig = go.Figure()

    for nazwa in wybrane_scenariusze:
        # --- 4a. PUNKTY (Wyniki) ---
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            # Po modyfikacji load_data: [0]=Nr wiersza, [1]=Y, [5]=X, [6]=Info
            x_idx = 5 if 5 in df_p.columns else 1
            y_idx = 1
            txt_info = df_p[6] if 6 in df_p.columns else ""
            
            fig.add_trace(go.Scatter(
                x=df_p[x_idx], y=df_p[y_idx],
                mode='markers',
                name=f"{nazwa} (Pkt)",
                marker=dict(size=6),
                customdata=pd.concat([df_p[0], txt_info], axis=1),
                hovertemplate="B: %{x}<br>Y: %{y}<extra></extra>"
            ))

        # --- 4b. FUNKCJA POMOCNICZA DLA KRZYWYCH ---
        def add_curve(file_dict, label_suffix, color):
            df_c = load_data(file_dict[nazwa])
            if df_c is not None:
                # Krzywe CSV zazwyczaj mają: [0]=Nr wiersza, [1]=X, [2]=Y
                df_c = df_c.sort_values(by=1)
                df_c_plot = df_c[df_c[2] > 0] # Filtr dla logarytmu
                fig.add_trace(go.Scatter(
                    x=df_c_plot[1], y=df_c_plot[2],
                    mode='lines',
                    name=f"{nazwa} ({label_suffix})",
                    line=dict(width=1.5, color=color),
                    hoverinfo='skip' # Krzywe nie przeszkadzają w klikaniu punktów
                ))

        add_curve(Krzywe_mid, "MID", "black")
        add_curve(Krzywe_up, "UP", "gray")
        add_curve(Krzywe_down, "DOWN", "gray")

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        clickmode='event+select'
    )

    # Rysowanie wykresu
    selected_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # --- 5. WYŚWIETLANIE DANYCH PO KLIKNIĘCIU ---
    if selected_data and "selection" in selected_data and len(selected_data["selection"]["points"]) > 0:
        st.markdown("---")
        st.subheader("🔍 Szczegóły wybranego punktu")
        
        for point in selected_data["selection"]["points"]:
            if 'customdata' in point:
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
