# src/utils/config.py

# Paramètres par défaut
DEFAULT_CONFIG = {
    'NPS_THRESHOLD': 35,  # Seuil de réponses minimum
    'PERIODS': {
        '4 dernières semaines': '28D',
        '8 dernières semaines': '56D',
        '4 derniers mois': '120D',
        '12 derniers mois': '365D'
    }
}

# Variables globales pour stocker la configuration
config = DEFAULT_CONFIG.copy()

def get_config(key: str, default=None):
    """Récupère une valeur de configuration"""
    return config.get(key, default)

def update_config(key: str, value: any):
    """Met à jour une valeur de configuration"""
    config[key] = value
    return config