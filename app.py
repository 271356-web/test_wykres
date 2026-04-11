import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. KONFIGURACJA I STYLE ---
st.set_page_config(layout="wide", page_title="Gravity Analysis")

# Stylowanie metryk, aby były mniejsze i czytelniejsze
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("Analiza porównawcza scenariuszy")

# --- 2. FUNKCJE WCZYTYWANIA DANYCH (Z CACHE) ---
@st.cache_data
def load_data(file_path):
    """Wczytuje dane z pliku tekstowego i konwertuje na DataFrame."""
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
        # Konwersja na liczby tam, gdzie to możliwe
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if not converted.isna().all():
                df[col] = converted
        return df
    except Exception:
        return None

# --- 3. KONFIGURACJA ŚCIEŻEK ---
scenariusze = {
    "Scenariusz 1 (1m)": "dane/wynik_1m.txt",
    "Scenariusz 2 (5m)": "dane/wynik_5m.txt",
    "Scenariusz 3 (10m)": "dane/wynik_10m.txt",
    "Scenariusz 4 (1m SB)": "dane/wynik_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/wynik_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/wynik_10m_sb.txt"
}

# Dynamiczne generowanie ścieżek dla krzywych (z zabezpieczeniem nazw)
Krzywe_mid = {k: v.replace('wynik_', 'mid_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_up = {k: v.replace('wynik_', 'up_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_down = {k: v.replace('wynik_', 'down_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}

# --- 4. SIDEBAR - WYBÓR ---
st.sidebar.header("Ustawienia widoku")
wybrane_scenariusze = []
for n in scenariusze.keys():
    if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)")):
        wybrane_scenariusze.append(n)

# --- 5. GŁÓWNA LOGIKA WYKRESU ---
if not wybrane_scenariusze:
    st.warning("👈 Zaznacz scenariusz w panelu bocznym, aby wyświetlić dane.")
else:
    fig = go.Figure()

    for nazwa in wybrane_scenariusze:
        # --- 5a. PUNKTY (Wyniki) ---
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            # Bezpieczne przypisanie kolumn
            # [0]=Nr wiersza, [1]=Y (Multiplier), [5]=X (B)
            x_col = 5 if 5 in df_p.columns else 1
            y_col = 1
            info_col = 6 if 6 in df_p.columns else None
            
            # Filtr dla skali logarytmicznej (Y > 0)
            df_p_plot = df_p[df_p[y_col] > 0].copy()
            
            custom_info = df_p_plot[info_col] if info_col is not None else [""] * len(df_p_plot)

            fig.add_trace(go.Scatter(
                x=df_p_plot[x_col], 
                y=df_p_plot[y_col],
                mode='markers',
                name=f"{nazwa} (Pkt)",
                marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
                customdata=list(zip(df_p_plot[0], custom_info)),
                hovertemplate="<b>B:</b> %{x}<br><b>Val:</b> %{y}<br><b>Wiersz:</b> %{customdata[0]}<extra></extra>"
            ))

        # --- 5b. KRZYWE (MID, UP, DOWN) ---
        def add_curve(file_dict, label_suffix, color, dash=None):
            df_c = load_data(file_dict[nazwa])
            if df_c is not None and 1 in df_c.columns and 2 in df_c.columns:
                df_c = df_c.sort_values(by=1)
                df_c_plot = df_c[df_c[2] > 0]
                fig.add_trace(go.Scatter(
                    x=df_c_plot[1], 
                    y=df_c_plot[2],
                    mode='lines',
                    name=f"{nazwa} ({label_suffix})",
                    line=dict(width=1.5, color=color, dash=dash),
                    hoverinfo='skip'
                ))

        add_curve(Krzywe_mid, "MID", "black")
        add_curve(Krzywe_up, "UP", "gray", dash='dash')
        add_curve(Krzywe_down, "DOWN", "gray", dash='dash')

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        clickmode='event+select'
    )

    # Renderowanie wykresu
    selected_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # --- 6. SZCZEGÓŁY PO KLIKNIĘCIU ---
    if selected_data and "selection" in selected_data and len(selected_data["selection"]["points"]) > 0:
        st.divider()
        st.subheader("🔍 Szczegóły wybranego punktu")
        
        for point in selected_data["selection"]["points"]:
            if 'customdata' in point:
                row_nr, row_desc = point['customdata']
                
                # Wyświetlanie metryk
                c1, c2, c3 = st.columns(3)
                c1.metric("Wiersz w pliku", int(row_nr))
                c2.metric("Współrzędna B (X)", f"{point['x']:.3f}")
                c3.metric("Multiplier (Y)", f"{point['y']:.4e}")
                
                if row_desc:
                    st.info(f"**Dodatkowe info:** {row_desc}")

                # Próba wczytania danych kordynatów
                df_coords = load_data("dane_kord.txt")
                if df_coords is not None:
                    try:
                        # Próba rzutowania row_desc na int, jeśli tam jest indeks kolumny
                        idx = int(float(row_desc)) 
                        col_x = 2 * idx
                        col_y = 2 * idx + 1
                        
                        if col_x in df_coords.columns and col_y in df_coords.columns:
                            st.write(f"**Profil dla punktu (kolumny {col_x} i {col_y}):**")
                            # Wykres lokalny
                            local_fig = go.Figure()
                            local_fig.add_trace(go.Scatter(
                                x=df_coords[col_x], 
                                y=df_coords[col_y], 
                                mode='lines+markers',
                                line=dict(color='firebrick')
                            ))
                            local_fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
                            st.plotly_chart(local_fig, use_container_width=True)
                    except (ValueError, TypeError):
                        st.warning("Nie można dopasować profilu kordynatów (niepoprawny format opisu punktu).")
                
                st.divider()
    else:
        st.info("💡 **Wskazówka:** Kliknij dowolny punkt na wykresie powyżej, aby zobaczyć szczegółowe dane profilu.")
