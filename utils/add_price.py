import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def add_price(listings_path, calendar_path, output_path):
    # Charger les fichiers
    listings = pd.read_csv(listings_path)
    calendar = pd.read_csv(calendar_path)

    # 1. Nettoyer et convertir la colonne `price` dans calendar
    # Supprimer les caractères spéciaux ($, ,) et convertir en numérique
    calendar['price'] = calendar['price'].str.replace('[\$,]', '', regex=True).astype(float)

    # Vérifier les valeurs manquantes dans `price` après conversion
    print(f"Valeurs manquantes dans calendar['price'] : {calendar['price'].isnull().sum()}")

    # 2. Calculer le prix moyen par `listing_id`
    average_price_by_id = calendar.groupby('listing_id')['price'].mean().reset_index()
    average_price_by_id.rename(columns={'price': 'average_price'}, inplace=True)

    # 3. Joindre les moyennes au dataset principal
    listings = listings.merge(average_price_by_id, left_on='id', right_on='listing_id', how='left')

    # 4. Compléter les valeurs manquantes dans la colonne `price` avec `average_price`
    listings['price'] = listings['price'].fillna(listings['average_price'])

    # Supprimer la colonne temporaire `average_price` si elle n'est plus nécessaire
    listings.drop(columns=['average_price', 'listing_id'], inplace=True)

    # Vérifier les valeurs manquantes restantes dans `price`
    print(f"Valeurs manquantes dans listings['price'] après imputation : {listings['price'].isnull().sum()}")

    # Exporter les données enrichies
    listings.to_csv(output_path, index=False)

    # Aperçu des données enrichies
    print(listings[['id', 'price']].head())

    # Heatmap des valeurs manquantes
    plt.figure(figsize=(8, 6))
    sns.heatmap(listings.isnull(), cbar=False, cmap='viridis')
    plt.title('Valeurs manquantes dans le dataset')
    plt.show()