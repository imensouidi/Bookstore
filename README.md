# 📚 Système de Recherche de Livres avec Azure OpenAI

Bienvenue dans cette application de recherche de livres basée sur Azure et OpenAI ! Ce projet propose un système intelligent qui corrige, enrichit et traite les requêtes des utilisateurs pour fournir des résultats précis et pertinents.

---

## 🛠 Fonctionnalités

- **Recherche Avancée** : Correction et enrichissement des requêtes grâce à OpenAI.
- **Intégration avec Azure** : Exploite Azure OpenAI et Azure Cognitive Search pour des performances optimales.
- **Interface Interactive** : Une expérience utilisateur fluide et en temps réel pour afficher les résultats et les détails des livres.

---

## 📂 Structure du Projet

- **`backend.py`** : Contient la logique métier pour le traitement et l'exécution des requêtes.
- **`app.py`** : Fournit une interface utilisateur interactive basée sur Chainlit.

---

## 📖 Documentation

Une **documentation détaillée** et un **diagramme d'architecture** sont inclus pour mieux comprendre les aspects techniques du projet.

---

## 🚀 Configuration et Lancement

### Prérequis

- Python 3.8 ou une version ultérieure
- Azure OpenAI et Azure Cognitive Search configurés
- Un fichier `.env` contenant vos clés et paramètres d’API Azure

### Étapes

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/votre-repo.git
   cd votre-repo
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer le fichier `.env`** :
   Créez un fichier `.env` à la racine du projet et ajoutez-y les informations suivantes :
   ```plaintext
   OPENAI_KEY=<votre_clé_OpenAI>
   OPENAI_API_VERSION=v1
   OPENAI_ENDPOINT=<votre_endpoint_OpenAI>
   OPENAI_MODEL=<nom_du_modèle_OpenAI>
   SEARCH_ENDPOINT=<endpoint_Azure_Cognitive_Search>
   SEARCH_INDEX_NAME=<nom_de_l’index>
   SEARCH_API_KEY=<votre_clé_API_recherche>
   ```

4. **Lancer l'application** :
   ```bash
   python app.py
   ```

---

## 🖼 Aperçu de l'Architecture

Voici un aperçu simplifié du processus :

1. **Requête utilisateur** : L'utilisateur soumet une recherche via l'interface.
2. **Traitement initial** : La requête est corrigée et enrichie par OpenAI.
3. **Recherche optimisée** : Azure Cognitive Search effectue une recherche sur les données.
4. **Résultats affichés** : Les résultats pertinents sont présentés à l'utilisateur via l'interface interactive.

