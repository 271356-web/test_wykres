import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="Gravity Analysis")
st.title("Analiza porównawcza scenariuszy")

# ... (Sekcje 1, 2 i 3 pozostają bez zmian - wczytywanie danych) ...

# 4. Wykres
fig = go.Figure()

if not wybrane_scenariusze:
    st.warning("Zaznacz scenariusz w panelu bocznym.")
else:
    for nazwa in wybrane_scenariusze:
        # --- PUNKTY (Wyniki) ---
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            # Dodajemy metadane do customdata, aby móc je wyciągnąć po kliknięciu
            custom_data = df_p[5] if 5 in df_p.columns else df_p[0]
            
            fig.add_trace(go.Scatter(
                x=df_p[4] if 4 in df_p.columns else df_p[0],
                y=df_p[0],
                mode='markers',
                name=f"{nazwa} (Pkt)",
                marker=dict(size=6), # Zwiększyłem nieco punkt dla łatwiejszego klikania
                hovertext=custom_data,
                customdata=custom_data # To przekażemy do Streamlita
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

    # 5. Wyświetlanie danych pod wykresem
    if selected_points and "selection" in selected_points and len(selected_points["selection"]["points"]) > 0:
        st.subheader("Szczegóły wybranego punktu:")
        
        for point in selected_points["selection"]["points"]:
            # Wyciągamy dane z punktu
            x_val = point['x']
            y_val = point['y']
            
            # Tworzymy ładny widok
            col1, col2, col3 = st.columns(3)
            col1.metric("B [m] (X)", f"{x_val:.4f}")
            col2.metric("Multiplier (Y)", f"{y_val:.4f}")
            
            # Jeśli w customdata była nazwa/opis
            if 'customdata' in point:
                st.info(f"**Dodatkowe informacje:** {point['customdata']}")
            
            st.divider()
    else:
        st.info("Kliknij w punkt na wykresie, aby zobaczyć szczegółowe dane.")
