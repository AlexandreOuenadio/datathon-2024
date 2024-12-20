import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Fonction pour calculer la distance Haversine
def haversine(lat1, lon1, lat2, lon2):
    '''
    Fonction pour calculer la distance Haversine entre deux points

    :param lat1: Latitude du premier point
    :param lon1: Longitude du premier point
    :param lat2: Latitude du deuxième point
    :param lon2: Longitude du deuxième point

    :return: Distance en kilomètres
    '''

    R = 6371  # Rayon moyen de la Terre en kilomètres
    # Convertir les degrés en radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    # Différence des coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Formule de Haversine
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance

