# src/main.py
import streamlit as st
import pandas as pd
import numpy as np
from components.nps_overview import render_nps_overview
from utils.config import config, DEFAULT_CONFIG

def test_data():
    # Création du DataFrame de base
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=90)  # 3 mois de données
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Générer plusieurs réponses par jour (entre 3 et 8 réponses)
    all_dates = []
    for date in dates:
        # Générer un nombre aléatoire de réponses pour ce jour
        n_responses = np.random.randint(3, 9)
        all_dates.extend([date] * n_responses)
    
    n_samples = len(all_dates)
    np.random.seed(42)
    
    df = pd.DataFrame({
        'Horodateur': all_dates,
        'NPS_Score': np.random.choice(
            np.arange(0, 11),
            size=n_samples,
            p=[0.01, 0.02, 0.02, 0.03, 0.04, 0.05, 0.13, 0.15, 0.20, 0.18, 0.17]
        )
    })

    service_metrics = {
        # Général
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'ambiance générale": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la propreté générale": [3, 4, 5],

        # Expériences
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'expérience à la salle de sport": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'expérience piscine": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la disponibilité des équipements sportifs": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les vestiaires (douches / sauna/ serviettes..)": [2, 3, 4],

        # Personnel
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les coachs": [4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les maitres nageurs": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant le personnel d'accueil": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant Le commercial": [3, 4, 5],

        # Services (modification uniquement de ces deux dernières lignes)
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant La qualité des coaching en groupe": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la disponibilité des cours sur le planning": [2, 3, 4],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la restauration": [3, 4, 5],
        "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les événements et animations": [3, 4, 5]}

    for metric, possible_scores in service_metrics.items():
        df[metric] = np.random.choice(
            possible_scores,
            size=n_samples,
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
    st.set_page_config(
        page_title="NPS Dashboard V2",
        page_icon="🏊‍♀️",
        layout="wide"
    )

    # Tabs pour la navigation
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Analyses", "⚙️ Configuration"])
    
    df = test_data()

    with tab1:
        render_nps_overview(df)
    
    with tab2:
        st.header("Analyses détaillées")
        # ... (à implémenter)
    
    with tab3:
        st.markdown("### ⚙️ Configuration")
        with st.expander("Paramètres généraux", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                new_threshold = st.number_input(
                    "Seuil de représentativité",
                    min_value=10,
                    max_value=100,
                    value=config.get('NPS_THRESHOLD', 35),
                    help="Nombre minimum de réponses nécessaires pour considérer une période comme représentative"
                )
                
                if new_threshold != config.get('NPS_THRESHOLD'):
                    config['NPS_THRESHOLD'] = new_threshold
                    st.success(f"Seuil mis à jour : {new_threshold} réponses")

            with col2:
                st.markdown("""
                **À propos du seuil de représentativité**
                
                Ce seuil détermine le nombre minimum de réponses nécessaires pour qu'une période soit considérée comme statistiquement significative. 
                Les périodes n'atteignant pas ce seuil seront affichées en transparence dans les graphiques.
                """)

if __name__ == "__main__":
    main()