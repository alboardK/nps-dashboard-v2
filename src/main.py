import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from components.nps_overview import render_nps_overview

# Configuration de la page
st.set_page_config(
    page_title="NPS Dashboard V2",
    page_icon="🏊‍♀️",
    layout="wide"
)

# Test de la connexion aux données
def test_data():
    # Création d'un DataFrame de test plus complet
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    df = pd.DataFrame({
        'Horodateur': dates,
        'NPS_Score': np.random.randint(0, 11, size=100),
    })
    
    # Ajout des catégories
    df['NPS_Category'] = df['NPS_Score'].apply(lambda x: 
        'Promoteur' if x >= 9 else 
        'Passif' if x >= 7 else 
        'Détracteur'
    )
    
    return df

def main():
    st.title("🏊‍♀️ NPS Dashboard V2 - Test")
    
    # Chargement des données
    df = test_data()
    
    # Affichage du composant NPS Overview
    render_nps_overview(df)

if __name__ == "__main__":
    main()
    