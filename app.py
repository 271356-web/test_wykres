import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Prosty Wykres Gravity")
st.title("Podgląd danych: wynik_1m.txt")

file_path = "dane/wynik_1m.txt"

if os.path.exists(file_path):
    try:
        # Wczytujemy plik linia po linii, żeby uniknąć błędów parsera
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        data = []
        for line in lines:
            # Rozdzielamy linię na maksymalnie 6 części (5 kolumn danych + 1 nazwa)
            # To sprawi, że nawet jeśli w nazwie są spacje, zostaną w jednej kolumnie
            parts = line.strip().split(maxsplit=5)
            if len(parts) >= 5:
                data.append(parts)
        
        df = pd.DataFrame(data)
        
        # Konwertujemy kolumny liczbowe na liczby (bo po split są tekstami)
        for col in df.columns[:5]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        if df.empty:
            st.warning("Nie udało się sparsować danych.")
        else:
            df.columns = [f"Col_{i}" for i in range(len(df.columns))]
            
            # Wykres (B to Col_4, G to Col_0)
            fig = px.scatter(
                df, 
                x="Col_4", 
                y="Col_0", 
                log_y=True,
                hover_data=["Col_5"], # Tutaj będzie Twoja nazwa ze spacjami
                title="Wykres z obsługą spacji w nazwach",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if st.checkbox("Pokaż tabelę danych"):
                st.write(df)

    except Exception as e:
        st.error(f"Błąd: {e}")
else:
    st.error(f"Nie znaleziono pliku: {file_path}")
