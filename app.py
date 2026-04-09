import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="Gravity Analysis")
st.title("Analiza porównawcza scenariuszy")

# 1. Ścieżki
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

# 2. Sidebar
st.sidebar.header("Wybierz scenariusze")
wybrane_scenariusze = [n for n in scenariusze.keys() if st.sidebar.checkbox(n, value=(n == "Scenariusz 1 (1m)"))]

# 3. Funkcja ładowania (uproszczona i bardziej stabilna)
def load_data(path):
    if not os.path.exists(path):
        return None
    try:
        # Próba wczytania z dowolnym separatorem białych znaków
        df = pd.read_csv(path, sep=r'\s+', header=None, engine='python')
        df = df.apply(pd.to_numeric, errors='coerce').dropna()
        return df
    except:
        return None

# 4. Wykres
fig = go.Figure()

if not wybrane_scenariusze:
    st.warning("Wybierz scenariusz w panelu bocznym.")
else:
    for nazwa in wybrane_scenariusze:
        # --- PUNKTY ---
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None and not df_p.empty:
            # Sprawdzamy czy mamy kolumnę 4 (B) i 0 (G), jeśli nie - bierzemy co jest
            col_x = 4 if 4 in df_p.columns else 0
            col_y = 0
            fig.add_trace(go.Scatter(
                x=df_p[col_x], y=df_p[col_y],
                mode='markers', name=f"{nazwa} (Pkt)",
                marker=dict(size=7, opacity=0.5)
            ))
        
        # --- KRZYWA MID ---
        df_m = load_data(Krzywe_mid[nazwa])
        if df_m is not None and len(df_m.columns) >= 2:
            # Sortujemy po X, żeby linia nie "skakała" po wykresie
            df_m = df_m.sort_values(by=df_m.columns[0])
            
            # Filtr dla skali logarytmicznej (usuwamy wartości <= 0)
            df_m_plot = df_m[df_m[df_m.columns[1]] > 0]
            
            fig.add_trace(go.Scatter(
                x=df_m_plot[df_m_plot.columns[0]], 
                y=df_m_plot[df_m_plot.columns[1]],
                mode='lines',
                name=f"{nazwa} (Krzywa MID)",
                line=dict(width=3) # Grubsza linia
            ))
        else:
            st.sidebar.warning(f"Brak lub zły format pliku: {Krzywe_mid[nazwa]}")

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# 5. Diagnostyka (pokaż tabelę pod spodem)
if st.checkbox("Debug: Pokaż dane tabelaryczne"):
    for nazwa in wybrane_scenariusze:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Plik Pkt: {scenariusze[nazwa]}")
            st.write(load_data(scenariusze[nazwa]))
        with col2:
            st.write(f"Plik Krzywa: {Krzywe_mid[nazwa]}")
            st.write(load_data(Krzywe_mid[nazwa]))import streamlit as st
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
        # 1. Punkty
        s_pkt = scenariusze[nazwa]
        d_pkt = load_data(s_pkt)
        if d_pkt is not None and not d_pkt.empty:
            fig.add_trace(go.Scatter(
                x=d_pkt[4] if 4 in d_pkt.columns else d_pkt[0], 
                y=d_pkt[0], 
                mode='markers',
                name=f"{nazwa} (punkty)"
            ))
        
        # 2. Krzywa
        s_mid = Krzywe_mid[nazwa]
        d_mid = load_data(s_mid)
        if d_mid is not None and len(d_mid.columns) >= 2:
            # Filtr dla skali logarytmicznej (tylko wartości > 0)
            d_mid_plot = d_mid[d_mid[1] > 0] 
            fig.add_trace(go.Scatter(
                x=d_mid_plot[0], 
                y=d_mid_plot[1], 
                mode='lines',
                name=f"{nazwa} (krzywa MID)",
                line=dict(width=3)
            ))

    fig.update_layout(
        xaxis_title="B [m]",
        yaxis_title="Gravity multiplier [-]",
        yaxis_type="log",
        template="plotly_white",
        height=700
    )
    st.plotly_chart(fig, use_container_width=True)

# 5. Podgląd tabelaryczny
if st.checkbox("Pokaż tabele danych"):
    for nazwa in wybrane_scenariusze:
        st.write(f"Dane dla: {nazwa}")
        d = load_data(scenariusze[nazwa])
        if d is not None:
            st.dataframe(d.head(10))
