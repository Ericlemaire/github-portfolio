"""
1) moyenne de dépense journalière depuis le début du mois. 
2) idem par mois, par semaine, sur l'année en cours et passée. 
3) en fonction du niveau de dépanses moyen depuis une période donnée, calculé l'épargne totale possible à une échéance de temps particulière / pour les vacances, etc.
4) visualisation des alertes. 
"""



import pandas as pd
import random
from datetime import datetime, timedelta

# Définir les catégories de dépenses
categories_depenses = ['Nourriture', 'Logement', 'Transport', 'Santé', 'Éducation', 'Divertissement', 'Vêtements', 'Épargne et investissement']

# Définir la plage de dates
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

# Générer une liste de dates entre start_date et end_date
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Générer des données aléatoires pour les montants dépensés
montants_depenses = [random.randint(10, 1000) for _ in range(len(dates))]

# Créer une liste de tuples contenant les données
donnees = []
for date, montant in zip(dates, montants_depenses):
    categorie = random.choice(categories_depenses)
    donnees.append((date, categorie, montant))

# Créer le DataFrame
df = pd.DataFrame(donnees, columns=['Date', 'Categorie', 'Montant'])

# Afficher les premières lignes du DataFrame
print(df.head())





import pandas as pd
import random
from datetime import datetime, timedelta

# Définir la date de départ
date_depart = datetime(2023, 3, 15)

# Définir les catégories de dépenses
categories_depenses = ['Nourriture', 'Logement', 'Transport', 'Santé', 'Éducation', 'Divertissement', 'Vêtements', 'Épargne et investissement']

# Générer une liste de dates depuis la date de départ jusqu'à aujourd'hui
dates = pd.date_range(start=date_depart, end=datetime.today(), freq='D')

# Générer des données aléatoires pour les montants dépensés
montants_depenses = [random.randint(10, 1000) for _ in range(len(dates))]

# Créer une liste de tuples contenant les données
donnees = []
for date, montant in zip(dates, montants_depenses):
    categorie = random.choice(categories_depenses)
    donnees.append((date, categorie, montant))

# Créer le DataFrame
df = pd.DataFrame(donnees, columns=['Date', 'Categorie', 'Montant'])

# Filtrer les données pour obtenir seulement celles du mois en cours
df_mois_en_cours = df[df['Date'].dt.month == datetime.today().month]

# Calculer la dépense totale depuis le début du mois
depense_totale = df_mois_en_cours['Montant'].sum()

# Calculer le nombre de jours depuis le début du mois
nombre_jours = datetime.today().day

# Calculer la dépense moyenne journalière depuis le début du mois
depense_moyenne_journaliere = depense_totale / nombre_jours

# Afficher le résultat
print("La dépense moyenne journalière depuis le début du mois est de :", depense_moyenne_journaliere)
