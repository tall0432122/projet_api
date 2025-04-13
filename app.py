# Importations
from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd
import numpy as np
import os

# Configuration de l'application
app = Flask(__name__, template_folder='templates', static_folder='static')
DOSSIER_UPLOAD = 'uploads'
os.makedirs(DOSSIER_UPLOAD, exist_ok=True)
app.config['DOSSIER_UPLOAD'] = DOSSIER_UPLOAD

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('index.html')

# Fonction pour nettoyer les données
def nettoyer_donnees(dataframe):
    """
    Nettoie le dataframe en plusieurs étapes :
    1. Supprime les doublons
    2. Remplit les valeurs manquantes
    3. Corrige les valeurs aberrantes
    """
    # Suppression des doublons
    nb_avant = len(dataframe)
    dataframe = dataframe.drop_duplicates(keep='first')
    nb_apres = len(dataframe)
    
    print(f"Doublons supprimés : {nb_avant - nb_apres} lignes")

    """""
    # 1. Nettoyage préalable de toutes les colonnes
    for col in dataframe.columns:
        # Convertit tout en string et supprime les espaces
        dataframe[col] = dataframe[col].astype(str).str.strip()
        
        # Conversion numérique si possible
        try:
            dataframe[col] = pd.to_numeric(dataframe[col])
        except:
            pass

    # 2. Suppression des doublons après normalisation
    avant = len(dataframe)
    dataframe = dataframe.drop_duplicates(keep='first')
    
    # Debug avancé
    doublons = dataframe[dataframe.duplicated(keep=False)]
    print(f"Doublons détectés:\n{doublons}")
    print(f"Lignes supprimées: {avant - len(dataframe)}")
    """""
    # Traitement des valeurs manquantes
    for colonne in dataframe.columns:
        if pd.api.types.is_numeric_dtype(dataframe[colonne]):
            # Pour les nombres : remplacer par la médiane
            mediane = dataframe[colonne].median()
            dataframe[colonne] = dataframe[colonne].fillna(mediane)
        else:
            # Pour le texte : remplacer par 'Non spécifié'
            dataframe[colonne] = dataframe[colonne].fillna('Non spécifié')
    
    # Correction des valeurs aberrantes (seulement pour les colonnes numériques)
    colonnes_numeriques = dataframe.select_dtypes(include=np.number).columns
    
    for colonne in colonnes_numeriques:
        # On ne traite pas les colonnes avec peu de valeurs uniques
        if dataframe[colonne].nunique() > 5:
            q1 = dataframe[colonne].quantile(0.25)
            q3 = dataframe[colonne].quantile(0.75)
            iqr = q3 - q1
            
            if iqr > 0:  # Évite les divisions par zéro
                limite_basse = q1 - 1.5 * iqr
                limite_haute = q3 + 1.5 * iqr
                dataframe[colonne] = np.clip(dataframe[colonne], limite_basse, limite_haute)
    
    return dataframe

# Route pour l'upload de fichier
@app.route('/upload', methods=['POST'])
def upload_fichier():
    """Gère l'upload et le nettoyage des fichiers CSV"""
    if 'fichier' not in request.files:
        return jsonify({'erreur': 'Aucun fichier envoyé'}), 400
        
    fichier = request.files['fichier']
    
    if fichier.filename == '':
        return jsonify({'erreur': 'Aucun fichier sélectionné'}), 400
        
    if not fichier.filename.lower().endswith('.csv'):
        return jsonify({'erreur': 'Seuls les fichiers CSV sont acceptés'}), 400
    
    try:
        # Lecture du fichier avec détection automatique des types
        donnees = pd.read_csv(fichier, na_values=['', 'NA', 'NaN', 'null'])
        
        # Nettoyage
        donnees_propres = nettoyer_donnees(donnees)
        
        # Sauvegarde du résultat
        nom_fichier_propre = f"nettoye_{fichier.filename}"
        chemin_complet = os.path.join(app.config['DOSSIER_UPLOAD'], nom_fichier_propre)
        donnees_propres.to_csv(chemin_complet, index=False)
        
        return jsonify({
            'succes': True,
            'message': 'Fichier nettoyé avec succès',
            'fichier': nom_fichier_propre,
            'apercu': donnees_propres.to_dict('records')
        })
    
    except Exception as e:
        return jsonify({'erreur': f"Problème lors du traitement : {str(e)}"}), 500

# Route pour télécharger les fichiers nettoyés
@app.route('/telecharger/<nom_fichier>')
def telecharger_fichier(nom_fichier):
    """Permet de télécharger les fichiers nettoyés"""
    return send_from_directory(
        app.config['DOSSIER_UPLOAD'],
        nom_fichier,
        as_attachment=True,
        mimetype='text/csv'
    )

# Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True, port=5000)