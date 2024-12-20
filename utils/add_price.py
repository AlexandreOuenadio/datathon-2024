from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, mean, when

def add_price(listings_path, calendar_path):
    # Initialiser une session Spark
    spark = SparkSession.builder.appName("Ajout de prix moyen").getOrCreate()
    
    # Charger les fichiers en DataFrames Spark
    listings = spark.read.csv(listings_path, header=True, inferSchema=True)
    calendar = spark.read.csv(calendar_path, header=True, inferSchema=True)
    
    # 1. Nettoyer et convertir la colonne `price` dans calendar
    calendar = calendar.withColumn('price', regexp_replace(col('price'), r'[\$,]', '').cast('float'))
    
    # Vérifier les valeurs manquantes dans `price` après conversion
    missing_price = calendar.filter(col('price').isNull()).count()
    print(f"Valeurs manquantes dans calendar['price'] : {missing_price}")
    
    # 2. Calculer le prix moyen par `listing_id`
    average_price_by_id = calendar.groupBy('listing_id').agg(mean('price').alias('average_price'))
    
    # 3. Joindre les moyennes au dataset principal
    listings = listings.join(average_price_by_id, listings['id'] == average_price_by_id['listing_id'], 'left')
    
    # 4. Compléter les valeurs manquantes dans la colonne `price` avec `average_price`
    listings = listings.withColumn(
        'price',
        when(col('price').isNull(), col('average_price')).otherwise(col('price'))
    )
    
    # Supprimer les colonnes temporaires
    listings = listings.drop('average_price', 'listing_id')
    
    # Vérifier les valeurs manquantes restantes dans `price`
    missing_listings_price = listings.filter(col('price').isNull()).count()
    print(f"Valeurs manquantes dans listings['price'] après imputation : {missing_listings_price}")
    
    return listings