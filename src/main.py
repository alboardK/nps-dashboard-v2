import streamlit as st
import pandas as pd
import altair as alt

# Configuration de la page
st.set_page_config(
    page_title="NPS Dashboard V2",
    page_icon="🏊‍♀️",
    layout="wide"
)

# Test de la connexion aux données
def test_data():
    return pd.DataFrame({
        'mois': ['Jan', 'Fév', 'Mar'],
        'nps': [45, 48, 47],
        'réponses': [42, 38, 45]
    })

# Interface de test
def main():
    st.title("🏊‍♀️ NPS Dashboard V2 - Test")
    
    df = test_data()
    
    # Test d'Altair
    chart = alt.Chart(df).mark_bar().encode(
        x='mois',
        y='nps',
        tooltip=['mois', 'nps', 'réponses']
    ).properties(title="Test de visualisation")
    
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
