import os
import requests
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Azure Search
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_api_key = os.getenv("SEARCH_API_KEY")
search_index_name = os.getenv("SEARCH_INDEX_NAME")

# Initialiser le client Azure Search
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index_name,
    credential=AzureKeyCredential(search_api_key)
)

def process_query_with_phi(query):
    """
    Utiliser Phi 4 (LM Studio) pour enrichir et reformuler la requête utilisateur.
    """
    try:
        response = requests.post(
            "http://127.0.0.1:1234/v1/completions",
            json={
                "model": "phi-4",
                "prompt": (
                    "You are an assistant that improves search queries for a library. "
                    f"Original query: '{query}'. Please provide an improved version."
                ),
                "max_tokens": 50,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        enriched_query = response.json().get("choices", [{}])[0].get("text", "").strip()
        print("Réponse brute de Phi 4 :", response.json())
        return enriched_query or query  # Fallback si la réponse est vide
    except Exception as e:
        print(f"Erreur avec Phi 4 : {e}")
        return query  # Requête utilisateur utilisée comme fallback

def search_book(query):
    """
    Rechercher des livres dans Azure Search en utilisant une requête enrichie.
    """
    try:
        enriched_query = process_query_with_phi(query)
        print(f"Requête enrichie : {enriched_query}")

        # Effectuer une recherche fuzzy avec Azure Search
        fuzzy_query = f"{enriched_query}~"
        print(f"Requête envoyée à Azure Search : {fuzzy_query}")
        results = search_client.search(search_text=fuzzy_query)

        # Organiser les résultats
        results_list = list(results)
        print("Résultats bruts d'Azure Search :", results_list)

        # Reformater les résultats pour l'interface utilisateur
        formatted_results = []
        for result in results_list:
            formatted_results.append({
                "Title": result.get("Title", "N/A"),
                "Author": result.get("Author", "N/A"),
                "Category": result.get("Category", "N/A"),
                "Description": result.get("Description", "N/A"),
                "ISBN": result.get("ISBN", "N/A")
            })
        return formatted_results
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return []