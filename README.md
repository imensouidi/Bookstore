Voici un exemple de **README** pour ton projet :

---

# 📚 Système de Recherche de Livres

Ce projet est un assistant de recherche pour une bibliothèque, permettant aux utilisateurs de rechercher des livres, d'obtenir leurs détails et de recevoir des suggestions améliorées basées sur des requêtes enrichies. Le système utilise **Azure Search**, **Phi 4** (LM Studio) et **Chainlit** pour une expérience utilisateur optimisée.

## 🛠️ Fonctionnalités

- **Recherche de livres** : Permet de rechercher des livres en saisissant des mots-clés ou un ISBN.
- **Détails des livres** : Fournit des informations détaillées sur un livre spécifique.
- **Requêtes enrichies** : Reformulation automatique des recherches grâce à Phi 4 (LM Studio).
- **Interface interactive** : Interaction intuitive avec l'utilisateur via Chainlit.

## 🚀 Installation et Configuration

### Prérequis

- Python 3.8 ou plus récent
- Azure Cognitive Search
- Phi 4 (LM Studio) fonctionnel localement
- Fichier `.env` pour les variables d'environnement

### Étapes d'installation

1. Clonez ce dépôt :
   ```bash
   git clone <URL_du_dépôt>
   cd <nom_du_dossier>
   ```

2. Installez les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez vos variables d'environnement dans un fichier `.env` :
   ```
   SEARCH_ENDPOINT=<votre_search_endpoint>
   SEARCH_API_KEY=<votre_search_api_key>
   SEARCH_INDEX_NAME=<votre_search_index_name>
   ```

4. Démarrez Phi 4 (LM Studio) sur le port `1234`.

5. Lancez le serveur Chainlit :
   ```bash
   chainlit run app.py
   ```

6. Accédez à l'interface utilisateur sur `http://localhost:8000`.

## 📂 Structure du Projet

```
.
├── app.py                # Point d'entrée principal pour l'application Chainlit
├── backend.py            # Module pour la recherche et le traitement des requêtes
├── requirements.txt      # Liste des dépendances Python
├── .env                  # Variables d'environnement (non inclus dans le dépôt Git)
└── README.md             # Documentation du projet
```

## 🌟 Utilisation

1. Lancez l'application avec Chainlit.
2. Saisissez votre requête (par exemple, "Victor Hugo" ou un ISBN).
3. Obtenez une liste de résultats avec les titres et auteurs.
4. Tapez **"Plus d'informations"** et le titre du livre pour des détails supplémentaires.

## 🔧 Technologies Utilisées

- **Python** : Langage principal pour le développement.
- **Chainlit** : Framework pour la création d'interfaces conversationnelles.
- **Azure Cognitive Search** : Moteur de recherche puissant.
- **Phi 4 (LM Studio)** : Pour l'enrichissement des requêtes utilisateur.

## 🐞 Débogage

- Activez le mode débogage en réglant `DEBUG_MODE` à `True` dans `backend.py`.
- Consultez les logs pour diagnostiquer les problèmes.


---

