import re
import pandas as pd

# Importer les données
listings = pd.read_csv('Data/raw/airbnb-lyon-december-2023/listings_detailed.csv')    

def extract_bedrooms_from_name(name):
    match = re.search(r'(\d+) bedroom', str(name))
    if match:
        return int(match.group(1))
    return None

# Compléter les valeurs manquantes dans 'bedrooms' à partir du 'name'
listings['bedrooms'] = listings['bedrooms'].fillna(
    listings['name'].apply(extract_bedrooms_from_name)
)

# Vérifier à nouveau les valeurs manquantes
print(f"Valeurs manquantes après extraction du 'name' : {listings['bedrooms'].isnull().sum()}")

# Enregistrer le fichier enrichi 
listings.to_csv('Data/raw/airbnb-lyon-december-2023/listings_detailed.csv', index=False)