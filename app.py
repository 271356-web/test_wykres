import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Prosty Wykres Gravity")
st.title("Podgląd danych: wynik_1m.txt")

file_path = "dane/wynik_1m.txt"

if os.path.exists(file_path):
    try:
        # DODANO: on_bad_lines='skip' oraz engine='python'
        # To pominie wiersze, które mają "zepsutą" liczbę kolumn
        df = pd.read_csv(
            file_path, 
            sep=r'\s+', 
            header=None, 
            on_bad_lines='skip', 
            engine='python'
        )
        
        # Sprawdzamy czy udało się wczytać jakiekolwiek dane
        if df.empty:
            st.warning("Plik jest pusty lub nie zawiera czytelnych danych.")
        else:
            # Automatyczne nazwanie kolumn
            df.columns = [f"Col_{i}" for i in range(len(df.columns))]
            
            # Tworzenie wykresu
            # Upewnij się, że Twój plik ma co najmniej 5 kolumn (indeks 4)
            # Jeśli kolumn jest mniej, zmień Col_4 na np. Col_1
            x_col = "Col_4" if len(df.columns) > 4 else df.columns[-1]
            y_col = "Col_0"
            
            fig = px.scatter(
                df, 
                x=x_col, 
                y=y_col, 
                log_y=True,
                title=f"Wykres: {y_col} vs {x_col}",
                labels={x_col: "Oś X (B)", y_col: "Oś Y (Gravity)"},
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)
            
            if st.checkbox("Pokaż surowe dane"):
                st.write(df)
                
    except Exception as e:
        st.error(f"Błąd podczas czytania pliku: {e}")
else:
    st.error(f"Nie znaleziono pliku: {file_path}")
