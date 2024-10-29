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
def display_nps_trend(df: pd.DataFrame, period: str):
    """

    Affiche le graphique d'évolution du NPS avec valeurs absolues et pourcentages
    """
    threshold = get_config('NPS_THRESHOLD', 35)
    
    # Regrouper par semaine
    df['Week'] = pd.to_datetime(df['Horodateur']).dt.strftime('%Y-%m-%W')
    weekly_data = []
    
    for week in sorted(df['Week'].unique()):
        week_df = df[df['Week'] == week]
        total = len(week_df)
        
        if total > 0:
            promoteurs_count = len(week_df[week_df['NPS_Category'] == 'Promoteur'])
            passifs_count = len(week_df[week_df['NPS_Category'] == 'Passif'])
            detracteurs_count = len(week_df[week_df['NPS_Category'] == 'Détracteur'])
            
            promoteurs_pct = (promoteurs_count / total) * 100
            passifs_pct = (passifs_count / total) * 100
            detracteurs_pct = (detracteurs_count / total) * 100
            
            nps_score = promoteurs_pct - detracteurs_pct
            
            # Convertir la semaine en date lisible
            week_date = pd.to_datetime(week + '-1', format='%Y-%m-%W-%w')
            readable_date = week_date.strftime('%d %b')
            
            weekly_data.extend([
                {
                    'Week': readable_date,
                    'Catégorie': 'Détracteur',
                    'Count': detracteurs_count,
                    'Pourcentage': detracteurs_pct,
                    'Réponses': total,
                    'Est_Représentatif': total >= threshold,
                    'NPS': nps_score,
                    'Order': 1  # Pour s'assurer que les détracteurs sont en bas
                },
                {
                    'Week': readable_date,
                    'Catégorie': 'Passif',
                    'Count': passifs_count,
                    'Pourcentage': passifs_pct,
                    'Réponses': total,
                    'Est_Représentatif': total >= threshold,
                    'NPS': nps_score,
                    'Order': 2  # Passifs au milieu
                },
                {
                    'Week': readable_date,
                    'Catégorie': 'Promoteur',
                    'Count': promoteurs_count,
                    'Pourcentage': promoteurs_pct,
                    'Réponses': total,
                    'Est_Représentatif': total >= threshold,
                    'NPS': nps_score,
                    'Order': 3  # Promoteurs en haut
                }
            ])
    
    chart_data = pd.DataFrame(weekly_data)
    
    # Barres empilées avec valeurs absolues
    bars = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Week:N', 
                title='Semaine',
                sort=None),
        y=alt.Y('Count:Q',  
                stack=True,
                title='Nombre de réponses'),
        color=alt.Color('Catégorie:N',
                       scale=alt.Scale(
                           domain=['Détracteur', 'Passif', 'Promoteur'],
                           range=['#ff4b4b', '#ffd166', '#2ab7ca']
                       ),
                       sort=['Détracteur', 'Passif', 'Promoteur']),
        order=alt.Order(
            'Order:Q',
            sort='ascending'
        ),
        opacity=alt.condition(
            'datum.Est_Représentatif',
            alt.value(1),
            alt.value(0.5)
        ),
        tooltip=[
            alt.Tooltip('Week:N', title='Semaine'),
            alt.Tooltip('Réponses:Q', title='Total réponses'),
            alt.Tooltip('Catégorie:N', title='Type'),
            alt.Tooltip('Pourcentage:Q', title='% ' + alt.datum.Catégorie, format='.1f'),
            alt.Tooltip('NPS:Q', title='Score NPS', format='.0f')
        ]
    )
    
    # Score NPS au-dessus des barres
    nps_text = alt.Chart(
        chart_data[chart_data['Catégorie'] == 'Promoteur']
    ).mark_text(
        dy=-25,  # Distance au-dessus des barres
        color='white',
        fontSize=16,  # Plus grand
        fontWeight='bold',  # En gras
        align='center',
        baseline='bottom'
    ).encode(
        x='Week:N',
        y=alt.Y(
            'sum(Count):Q',
            stack=True
        ),
        text=alt.Text('NPS:Q', format='.0f'),
        opacity=alt.condition(
            'datum.Est_Représentatif',
            alt.value(1),
            alt.value(0.5)
        )
    )

    # Légende pour le seuil de représentativité
    legend = alt.Chart({'values': [{'text': f'* Les barres grisées indiquent moins de {threshold} réponses'}]}).mark_text(
        dx=150,
        dy=10,
        color='gray',
        fontSize=11
    ).encode(
        text='text:N'
    )
    
    # Combiner tous les éléments
    final_chart = (bars + nps_text + legend).properties(
        height=400,
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
            