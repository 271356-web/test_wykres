import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. KONFIGURACJA ---
st.set_page_config(layout="wide", page_title="Gravity Analysis")
st.title("Analiza porównawcza scenariuszy")

# --- 2. FUNKCJE WCZYTYWANIA DANYCH ---

@st.cache_data
def load_data(file_path):
    """Wczytuje główne pliki wynikowe."""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path, sep=',', header=None, engine='python', on_bad_lines='skip')
        # Dodajemy oryginalny indeks wiersza (użyteczny przy debugowaniu)
        df['orig_row_index'] = range(1, len(df) + 1)
        return df
    except Exception as e:
        st.error(f"Błąd pliku {file_path}: {e}")
        return None

def get_profile_data(file_path, row_desc):
    if not os.path.exists(file_path):
        return None, None
    try:
        df_k = pd.read_csv(file_path, sep=',', header=None, engine='python')
        
        p_idx = int(float(str(row_desc).strip()))
        cx, cy = 2 * p_idx, 2 * p_idx + 1
        st.write(f"Kolumna X (indeks {cx})")
        st.write(f"Kolumna Y (indeks {cy})")
        x = df_k[cx]
            y = df_k[cy]
            return x, y
        else:
            st.error(f"Nie znaleziono kolumn {cx} i {cy} w pliku kordów.")
            return None, None
    except Exception as e:
        st.error(f"Błąd wewnątrz funkcji: {e}")
        return None, None

# --- 3. DEFINICJA SCENARIUSZY I ŚCIEŻEK ---
scenariusze = {
    "Scenariusz 1 (1m)": "dane/wynik_1m.txt",
    "Scenariusz 2 (5m)": "dane/wynik_5m.txt",
    "Scenariusz 3 (10m)": "dane/wynik_10m.txt",
    "Scenariusz 4 (1m SB)": "dane/wynik_1m_sb.txt",
    "Scenariusz 5 (5m SB)": "dane/wynik_5m_sb.txt",
    "Scenariusz 6 (10m SB)": "dane/wynik_10m_sb.txt"
}

# Automatyczne generowanie ścieżek dla krzywych teoretycznych
Krzywe_mid = {k: v.replace('wynik_', 'mid_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_up = {k: v.replace('wynik_', 'up_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}
Krzywe_down = {k: v.replace('wynik_', 'down_curve_').replace('.txt', '_mc.txt') for k, v in scenariusze.items()}

# --- 4. PASEK BOCZNY (SIDEBAR) ---
st.sidebar.header("Wybór scenariuszy")
wybrane_scenariusze = [n for n in scenariusze.keys() if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)"))]

# --- 5. WYKRES GŁÓWNY ---
if not wybrane_scenariusze:
    st.warning("Wybierz przynajmniej jeden scenariusz w panelu bocznym.")
else:
    fig = go.Figure()

    for nazwa in wybrane_scenariusze:
        # A. RYSOWANIE PUNKTÓW (DANE POMIAROWE)
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            try:
                # Kolumna 1 (indeks 0): Multiplier (Y)
                # Kolumna 5 (indeks 4): B [m] (X)
                # Kolumna 6 (indeks 5): Nr Profilu (Info)
                y_val = pd.to_numeric(df_p[0], errors='coerce')
                x_val = pd.to_numeric(df_p[4], errors='coerce')
                info_val = df_p[5] if 5 in df_p.columns else "0"
                
                mask = y_val > 0 # Ważne dla skali logarytmicznej
                
                fig.add_trace(go.Scatter(
                    x=x_val[mask], 
                    y=y_val[mask],
                    mode='markers',
                    name=f"{nazwa} (Pkt)",
                    customdata=list(zip(df_p['orig_row_index'][mask], info_val[mask])),
                    hovertemplate="B: %{x}<br>Y: %{y}<br>Row: %{customdata[0]}<extra></extra>"
                ))
            except Exception as e:
                st.error(f"Błąd formatu danych punktowych w {nazwa}: {e}")

        # B. RYSOWANIE KRZYWYCH (FUNKCJA POMOCNICZA)
        def add_curve(file_dict, suffix, color, dash=None):
            df_c = load_data(file_dict[nazwa])
            if df_c is not None and len(df_c.columns) >= 2:
                x_c = pd.to_numeric(df_c[0], errors='coerce')
                y_c = pd.to_numeric(df_c[1], errors='coerce')
                c_mask = y_c > 0
                fig.add_trace(go.Scatter(
                    x=x_c[c_mask], y=y_c[c_mask],
                    mode='lines', 
                    name=f"{nazwa} {suffix}",
                    line=dict(color=color, width=1, dash=dash),
                    hoverinfo='skip'
                ))

        add_curve(Krzywe_mid, "MID", "black")
        add_curve(Krzywe_up, "UP", "gray", "dash")
        add_curve(Krzywe_down, "DOWN", "gray", "dash")

    fig.update_layout(
        yaxis_type="log",
        xaxis_title="B [m]",
        yaxis_title="Multiplier",
        height=600,
        template="plotly_white",
        clickmode='event+select',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Wyświetlenie wykresu i przechwycenie interakcji
    selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # --- 6. DETALE (PO KLIKNIĘCIU W PUNKT) ---
    if selected and "selection" in selected and len(selected["selection"]["points"]) > 0:
        st.divider()
        st.subheader("Szczegółowa analiza wybranych punktów")
        
        for point in selected["selection"]["points"]:
            # Pobranie danych z customdata zapisanego w ścieżce Scatter
            # customdata[0] = row_index, customdata[1] = row_desc (nr profilu)
            row_nr, row_desc = point.get('customdata', [0, "0"])
            
            with st.expander(f"Punkt z wiersza {row_nr} (Profil {row_desc})", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("B [m] (Oś X)", f"{point['x']:.2f}")
                c2.metric("Multiplier (Oś Y)", f"{point['y']:.4e}")

                # Wykres profilu geometrycznego
                x_prof, y_prof = get_profile_data("dane_kord.txt", row_desc)
                
                if x_prof is not None and y_prof is not None:
                    sub = go.Figure()
                    sub.add_trace(go.Scatter(
                        x=x_prof, 
                        y=y_prof, 
                        mode='lines+markers', 
                        line=dict(color='firebrick')
                    ))
                    sub.update_layout(
                        height=300, 
                        margin=dict(l=20, r=20, t=40, b=20),
                        title=f"Geometria profilu nr {row_desc}",
                        xaxis_title="Odległość",
                        yaxis_title="Wartość"
                    )
                    st.plotly_chart(sub, use_container_width=True)
                else:
                    st.info(f"Dla tego punktu (Profil {row_desc}) nie znaleziono danych w dane_kord.txt")
