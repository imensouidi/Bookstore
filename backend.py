import os
import openai
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Configuration Azure OpenAI
openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_key = os.getenv("OPENAI_KEY")
api_version = os.getenv("OPENAI_API_VERSION")
model = os.getenv("OPENAI_MODEL")

openai.api_type = "azure"
openai.api_base = openai_endpoint
openai.api_version = api_version
openai.api_key = openai_key

# Configuration Azure Search
search_endpoint = os.getenv("SEARCH_ENDPOINT")
index_name = os.getenv("SEARCH_INDEX_NAME")
search_api_key = os.getenv("SEARCH_API_KEY")

# Initialisation du client Azure Search
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_api_key)
)

def process_query_with_openai(query):
    """
    Utilise Azure OpenAI pour enrichir et reformuler la requête utilisateur.
    """
    try:
        response = openai.ChatCompletion.create(
            engine=model,
            messages=[
                {"role": "system", "content": (
                    "Tu es un assistant intelligent qui aide à chercher des livres dans une bibliothèque. "
                    "Comprends la requête utilisateur et enrichis-la en ajoutant des termes similaires et des mots-clés pertinents "
                    "pour améliorer la recherche."
                )},
                {"role": "user", "content": f"Voici une requête utilisateur : {query}. Améliore-la pour qu'elle soit plus précise et efficace."}
            ]
        )
        # Extraire la requête enrichie
        enriched_query = response['choices'][0]['message']['content'].strip()
        return enriched_query
    except Exception as e:
        print(f"Erreur lors de la communication avec Azure OpenAI : {e}")
        return query  # Retourne la requête initiale en cas d'erreur

def search_book(query):
    """
    Recherche des livres dans Azure Search avec correspondances précises pour les catégories.
    """
    try:
        # Étape 1 : Enrichir la requête avec OpenAI
        enriched_query = process_query_with_openai(query)

        # Étape 2 : Appliquer fuzzy matching à la requête enrichie
        fuzzy_query = f"{enriched_query}~"

        # Étape 3 : Détecter si la requête concerne une catégorie spécifique
        if fuzzy_query.startswith("978"):  # ISBN détecté
            filter_query = f"ISBN eq '{fuzzy_query}'"
            results = search_client.search(search_text="", filter=filter_query)
        elif "fiction" in fuzzy_query.lower():  # Recherche par catégorie contenant "fiction"
            # Nettoyer la requête pour extraire la catégorie
            filter_query = f"Category eq '{fuzzy_query}'"
            results = search_client.search(search_text="", filter=filter_query)
        else:  # Recherche textuelle générale
            results = search_client.search(search_text=fuzzy_query)

        # Filtrer les résultats pour éviter les correspondances globales
        filtered_results = [
            result for result in results
        ]

        return filtered_results

    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return []
