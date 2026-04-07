import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Prosty Wykres Gravity")

st.title("Podgląd danych: wynik_1m.txt")

# Ścieżka do pliku
file_path = "dane/wynik_1m.txt"

if os.path.exists(file_path):
    # Wczytanie danych
    # sep=r'\s+' obsługuje spacje i tabulatory jako separatory
    df = pd.read_csv(file_path, sep=r'\s+', header=None)
    
    # Nazwijmy kolumny dla ułatwienia (zgodnie z Twoim Matlabem: 0 to G, 4 to B)
    # Jeśli plik ma inne kolumny, dostosuj indeksy [0] i [4]
    df.columns = [f"Col_{i}" for i in range(len(df.columns))]
    
    # Tworzenie wykresu w Plotly
    # x = kolumna 5 (indeks 4), y = kolumna 1 (indeks 0)
    fig = px.scatter(
        df, 
        x="Col_4", 
        y="Col_0", 
        log_y=True, # Skala logarytmiczna tak jak w Matlabie
        title="Wykres Gravity Multiplier vs B",
        labels={"Col_4": "B [m]", "Col_0": "Gravity multiplier [-]"},
        template="plotly_white"
    )

    # Wyświetlenie wykresu w aplikacji
    st.plotly_chart(fig, use_container_width=True)
    
    # Opcjonalnie: pokaż tabelę z danymi pod spodem
    if st.checkbox("Pokaż surowe dane"):
        st.write(df)
else:
    st.error(f"Nie znaleziono pliku w ścieżce: {file_path}")
    st.info("Upewnij się, że plik znajduje się w folderze 'dane' w Twoim repozytorium.")
