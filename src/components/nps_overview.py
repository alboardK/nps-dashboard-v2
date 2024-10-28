import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from typing import Tuple, Dict

def calculate_nps_metrics(df: pd.DataFrame, period: str = '4W') -> Dict:
    """
    Calcule les métriques NPS pour la période spécifiée
    """
    # Filtrer sur la période
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(period)
    period_df = df[df['Horodateur'].between(start_date, end_date)]
    
    # Calculer les pourcentages
    total = len(period_df)
    if total == 0:
        return {
            'nps_score': 0,
            'promoters_pct': 0,
            'passive_pct': 0,
            'detractors_pct': 0,
            'total_responses': 0
        }
    
    promoters = len(period_df[period_df['NPS_Category'] == 'Promoteur'])
    passives = len(period_df[period_df['NPS_Category'] == 'Passif'])
    detractors = len(period_df[period_df['NPS_Category'] == 'Détracteur'])
    
    metrics = {
        'nps_score': round((promoters/total * 100) - (detractors/total * 100), 1),
        'promoters_pct': round(promoters/total * 100, 1),
        'passive_pct': round(passives/total * 100, 1),
        'detractors_pct': round(detractors/total * 100, 1),
        'total_responses': total
    }
    
    return metrics

def display_nps_header(metrics: Dict):
    """
    Affiche l'en-tête avec les métriques NPS principales
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Score NPS",
            f"{metrics['nps_score']}",
            help="Net Promoter Score = % Promoteurs - % Détracteurs"
        )
    
    with col2:
        st.metric(
            "Promoteurs",
            f"{metrics['promoters_pct']}%",
            help=f"{int(metrics['total_responses'] * metrics['promoters_pct']/100)} répondants"
        )
    
    with col3:
        st.metric(
            "Passifs",
            f"{metrics['passive_pct']}%",
            help=f"{int(metrics['total_responses'] * metrics['passive_pct']/100)} répondants"
        )
    
    with col4:
        st.metric(
            "Détracteurs",
            f"{metrics['detractors_pct']}%",
            help=f"{int(metrics['total_responses'] * metrics['detractors_pct']/100)} répondants"
        )

def render_nps_overview(df: pd.DataFrame):
    """
    Composant principal qui affiche la vue d'ensemble du NPS
    """
    # Sélecteur de période
    period = st.selectbox(
        "Période d'analyse",
        ['4 dernières semaines', '8 dernières semaines', '4 derniers mois', '12 derniers mois'],
        index=0
    )
    
    # Conversion de la sélection en format pandas
    period_mapping = {
        '4 dernières semaines': '4W',
        '8 dernières semaines': '8W',
        '4 derniers mois': '4M',
        '12 derniers mois': '12M'
    }
    
    # Calcul des métriques
    metrics = calculate_nps_metrics(df, period_mapping[period])
    
    # Affichage
    display_nps_header(metrics)