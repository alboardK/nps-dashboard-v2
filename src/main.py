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
    # Création du DataFrame de base
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=90)  # 3 mois de données
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_samples = len(dates)  # Nombre exact de jours
    
    np.random.seed(42)
    
    df = pd.DataFrame({
        'Horodateur': dates,
        'NPS_Score': np.random.choice(
            np.arange(0, 11),
            size=n_samples,
            p=[0.01, 0.02, 0.02, 0.03, 0.04, 0.05, 0.13, 0.15, 0.20, 0.18, 0.17]
        )
    })

    # Génération des scores pour chaque métrique
    service_metrics = {
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'expérience à la salle de sport": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'expérience piscine": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant La qualité des coaching en groupe": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la disponibilité des cours sur le planning": [2, 3, 4],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la disponibilité des équipements sportifs": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les coachs": [4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les maitres nageurs": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant le personnel d'accueil": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant Le commercial": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'ambiance générale": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la propreté générale": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les vestiaires (douches / sauna/ serviettes..)": [2, 3, 4],
        "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" concernant votre satisfaction sur les éléments de services suivants : [l'offre restauration]": [3, 4, 5],
        "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" concernant votre satisfaction sur les éléments de services suivants : [les fêtes]": [3, 4, 5]
    }

    for metric, possible_scores in service_metrics.items():
        df[metric] = np.random.choice(
            possible_scores,
            size=n_samples,  # Utiliser la même taille que dates
            p=np.ones(len(possible_scores)) / len(possible_scores)
        )

    # Ajout des catégories NPS
    df['NPS_Category'] = df['NPS_Score'].apply(lambda x: 
        'Promoteur' if x >= 8 else
        'Passif' if x >= 6 else
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
    