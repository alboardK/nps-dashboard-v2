# nps_overview
import streamlit as st
import pandas as pd
import altair as alt
from typing import Dict, Tuple
from utils.config import get_config

def calculate_nps_metrics(df: pd.DataFrame, period: str = '28D') -> Dict:
    """
    Calcule les métriques NPS pour la période spécifiée
    """
    try:
        # Filtrer sur la période
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=int(period[:-1]))
        period_df = df[df['Horodateur'].between(start_date, end_date)]
        
        # Calculer les pourcentages
        total = len(period_df)
        
        # Retourner des valeurs par défaut si pas de données
        if total == 0:
            return {
                'nps_score': 0,
                'promoters_pct': 0,
                'passive_pct': 0,
                'detractors_pct': 0,
                'total_responses': 0
            }
        
        # Calculer les métriques
        promoters = len(period_df[period_df['NPS_Category'] == 'Promoteur'])
        passives = len(period_df[period_df['NPS_Category'] == 'Passif'])
        detractors = len(period_df[period_df['NPS_Category'] == 'Détracteur'])
        
        return {
            'nps_score': round((promoters/total * 100) - (detractors/total * 100), 1),
            'promoters_pct': round(promoters/total * 100, 1),
            'passive_pct': round(passives/total * 100, 1),
            'detractors_pct': round(detractors/total * 100, 1),
            'total_responses': total
        }
    
    except Exception as e:
        print(f"Error in calculate_nps_metrics: {str(e)}")
        # Retourner des valeurs par défaut en cas d'erreur
        return {
            'nps_score': 0,
            'promoters_pct': 0,
            'passive_pct': 0,
            'detractors_pct': 0,
            'total_responses': 0
        }

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
def prepare_data_for_period(df: pd.DataFrame, period: str):
    """
    Prépare et agrège les données selon la période sélectionnée
    """
    # Copie pour éviter les modifications sur le DataFrame original
    df = df.copy()
    
    # Conversion des dates
    df['Date'] = pd.to_datetime(df['Horodateur'])
    
    # Définition de la période d'agrégation
    if period in ['28D', '56D']:  # 4 ou 8 semaines
        # Grouper par semaine
        df['Period_Start'] = df['Date'].dt.to_period('W').dt.start_time
        format_str = '%d %b'
    else:  # 4 ou 12 mois
        # Grouper par mois
        df['Period_Start'] = df['Date'].dt.to_period('M').dt.start_time
        format_str = '%b %Y'
    
    # Créer l'agrégation
    grouped = df.groupby('Period_Start').agg(
        total=('NPS_Category', 'count'),
        promoteurs=('NPS_Category', lambda x: sum(x == 'Promoteur')),
        passifs=('NPS_Category', lambda x: sum(x == 'Passif')),
        detracteurs=('NPS_Category', lambda x: sum(x == 'Détracteur'))
    ).reset_index()
    
    # Calculer les métriques
    grouped['Display_Date'] = grouped['Period_Start'].dt.strftime(format_str)
    grouped['Sort_Key'] = grouped['Period_Start'].dt.strftime('%Y-%m-%d')
    grouped['NPS_Score'] = (grouped['promoteurs']/grouped['total'] * 100) - (grouped['detracteurs']/grouped['total'] * 100)
    grouped['Est_Representatif'] = grouped['total'] >= get_config('NPS_THRESHOLD', 35)
    
    # Trier chronologiquement
    return grouped.sort_values('Period_Start')

def display_nps_trend(df: pd.DataFrame, period: str):
    """
    Affiche le graphique d'évolution du NPS avec les données pré-agrégées
    """
    # Filtrer et agréger les données
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(period)
    period_df = df[df['Horodateur'].between(start_date, end_date)]
    
    if len(period_df) == 0:
        st.warning("Aucune donnée disponible pour la période sélectionnée.")
        return
        
    # Préparer les données agrégées
    agg_data = prepare_data_for_period(period_df, period)
    
    # Créer les données pour le graphique
    chart_data = []
    for _, row in agg_data.iterrows():
        # Ajouter les trois catégories pour chaque période
        for cat, count in [
            ('Détracteur', row['detracteurs']),
            ('Passif', row['passifs']),
            ('Promoteur', row['promoteurs'])
        ]:
            chart_data.append({
                'Period': row['Display_Date'],
                'Sort_Key': row['Sort_Key'],
                'Catégorie': cat,
                'Count': count,
                'Total': row['total'],
                'Est_Représentatif': row['Est_Representatif'],
                'NPS': round(row['NPS_Score'], 1)
            })
    
    # Convertir en DataFrame pour Altair
    chart_df = pd.DataFrame(chart_data)
    
    # Barres empilées
    bars = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X('Period:N',
                sort=alt.SortField('Sort_Key', order='ascending'),
                title=None),
        y=alt.Y('Count:Q',
                stack=True,
                title='Nombre de réponses'),
        color=alt.Color('Catégorie:N',
                       scale=alt.Scale(
                           domain=['Détracteur', 'Passif', 'Promoteur'],
                           range=['#ff4b4b', '#ffd166', '#2ab7ca']
                       )),
        opacity=alt.condition(
            'datum.Est_Représentatif',
            alt.value(1),
            alt.value(0.5)
        ),
        tooltip=[
            alt.Tooltip('Period:N', title='Période'),
            alt.Tooltip('Total:Q', title='Total réponses'),
            alt.Tooltip('Count:Q', title='Nombre de réponses'),
            alt.Tooltip('NPS:Q', title='Score NPS', format='.1f')
        ]
    ).properties(height=300)
    
    # Score NPS sous les barres
    text = alt.Chart(chart_df[chart_df['Catégorie'] == 'Promoteur']).mark_text(
        align='center',
        baseline='top',
        dy=5,
        fontSize=11,
        color='white'
    ).encode(
        x=alt.X('Period:N',
                sort=alt.SortField('Sort_Key', order='ascending')),
        text=alt.Text('NPS:Q', format='.1f'),
        opacity=alt.condition(
            'datum.Est_Représentatif',
            alt.value(1),
            alt.value(0.5)
        )
    )
    
    # Légende du seuil
    threshold = get_config('NPS_THRESHOLD', 35)
    legend = alt.Chart({'values': [{'text': f'* Les barres grisées indiquent moins de {threshold} réponses'}]}).mark_text(
        dx=150,
        dy=30,
        color='gray',
        fontSize=11
    ).encode(text='text:N')
    
    # Graphique final
    final_chart = (bars + text + legend).properties(
        title={
            'text': 'Évolution du NPS',
            'anchor': 'start',
            'fontSize': 16
        }
    ).configure_axis(
        grid=True,
        gridOpacity=0.1
    )
    
    st.altair_chart(final_chart, use_container_width=True)

def display_metrics_grid(df: pd.DataFrame, period: str):
    """
    Affiche la grille des métriques avec leurs évolutions
    """
    st.markdown("### Satisfaction par service")
    
    # Réorganisation des métriques par catégorie
    service_categories = {
        "Général": [
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'ambiance générale",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la propreté générale"
        ],
        "Expériences": [
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'expérience à la salle de sport",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant l'expérience piscine",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la disponibilité des équipements sportifs",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les vestiaires (douches / sauna/ serviettes..)"
        ],
        "Personnel": [
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les coachs",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les maitres nageurs",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant le personnel d'accueil",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant Le commercial"
        ],
        "Services": [
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant La qualité des coaching en groupe",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la disponibilité des cours sur le planning",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant la restauration",
            "sur une echelle de 1 à 5, 1 etant la pire note et 5 la meilleure, notez votre satisfaction concernant les événements"
        ]
    }

    # Calcul des périodes
    end_date = pd.Timestamp.now()
    period_days = int(period[:-1])
    start_date = end_date - pd.Timedelta(days=period_days)
    mid_date = start_date + pd.Timedelta(days=period_days/2)

    # Affichage par catégorie
    cols = st.columns(4)
    for idx, (category, metrics) in enumerate(service_categories.items()):
        with cols[idx]:
            st.markdown(f"#### {category}")
            
            for metric in metrics:
                try:
                    # Calcul période actuelle
                    current_data = df[
                        (df['Horodateur'] >= mid_date) & 
                        (df['Horodateur'] <= end_date) &
                        (df[metric].notna())
                    ][metric].astype(float)
                    
                    # Calcul période précédente
                    previous_data = df[
                        (df['Horodateur'] >= start_date) & 
                        (df['Horodateur'] < mid_date) &
                        (df[metric].notna())
                    ][metric].astype(float)
                    
                    if len(current_data) > 0 and len(previous_data) > 0:
                        current_avg = current_data.mean()
                        previous_avg = previous_data.mean()
                        evolution = current_avg - previous_avg
                        
                        # Nom court de la métrique
                        metric_short_name = metric.split("concernant ")[-1].split("]")[-1].strip()
                        if metric_short_name.startswith("l'"):
                            metric_short_name = metric_short_name[2:]
                        if metric_short_name.startswith("la "):
                            metric_short_name = metric_short_name[3:]
                        if metric_short_name.startswith("le "):
                            metric_short_name = metric_short_name[3:]
                        if metric_short_name.startswith("les "):
                            metric_short_name = metric_short_name[4:]
                        
                        # Détermination de la couleur et icône selon l'évolution
                        if abs(evolution) < 0.1:
                            icon = "―"
                            color = "gray"
                        elif evolution > 0:
                            icon = "▲"
                            color = "green"
                        else:
                            icon = "▼"
                            color = "red"
                        
                        # Affichage de la métrique
                        st.markdown(
                            f"""
                            <div style="
                                padding: 8px;
                                border-radius: 4px;
                                background-color: rgba(255,255,255,0.05);
                                margin-bottom: 8px;
                            ">
                                <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                ">
                                    <div>
                                        <div style="font-size: 0.9em;">{metric_short_name}</div>
                                        <div style="font-size: 1.2em; font-weight: bold;">
                                            {current_avg:.1f}
                                            <span style="
                                                color: {color};
                                                font-size: 0.8em;
                                                margin-left: 5px;
                                            ">
                                                {icon} {abs(evolution):.1f}
                                            </span>
                                        </div>
                                    </div>
                                    <div style="
                                        font-size: 0.7em;
                                        color: gray;
                                    ">
                                        {len(current_data)} rép.
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                except Exception as e:
                    st.error(f"Erreur pour la métrique {metric}: {str(e)}")

def render_nps_overview(df: pd.DataFrame):
    """
    Composant principal qui affiche la vue d'ensemble du NPS
    """
    try:
        # Sélecteur de période
        period = st.selectbox(
            "Période d'analyse",
            ['4 dernières semaines', '8 dernières semaines', '4 derniers mois', '12 derniers mois'],
            index=0
        )
        
        # Conversion de la sélection en format pandas
        period_mapping = {
            '4 dernières semaines': '28D',
            '8 dernières semaines': '56D',
            '4 derniers mois': '120D',
            '12 derniers mois': '365D'
        }
        
        # Calcul des métriques avec vérification
        metrics = calculate_nps_metrics(df, period_mapping[period])
        if metrics is None:
            metrics = {
                'nps_score': 0,
                'promoters_pct': 0,
                'passive_pct': 0,
                'detractors_pct': 0,
                'total_responses': 0
            }
        
        # Affichage
        display_nps_header(metrics)
        st.divider()
        display_nps_trend(df, period_mapping[period])
        st.divider()
        display_metrics_grid(df, period_mapping[period])
        
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")

def render_config():
    """
    Affiche et gère la configuration du dashboard
    """
    st.header("⚙️ Configuration")
    
    with st.expander("Paramètres généraux", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            new_threshold = st.number_input(
                "Seuil de représentativité",
                min_value=10,
                max_value=100,
                value=get_config('NPS_THRESHOLD', 35),
                help="Nombre minimum de réponses nécessaires pour considérer une période comme représentative"
            )
            
            if new_threshold != get_config('NPS_THRESHOLD', 35):
                update_config('NPS_THRESHOLD', new_threshold)
                st.success(f"Seuil mis à jour : {new_threshold} réponses")

        with col2:
            st.markdown("""
            **À propos du seuil de représentativité**
            
            Ce seuil détermine le nombre minimum de réponses nécessaires pour qu'une période soit considérée comme statistiquement significative. 
            Les périodes n'atteignant pas ce seuil seront affichées en transparence dans les graphiques.
            """)
