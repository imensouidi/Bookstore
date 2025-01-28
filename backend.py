import os
import requests
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import re

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

# Mode debug pour logs supplémentaires
DEBUG_MODE = True

def log_debug(message):
    """Afficher les messages de debug si DEBUG_MODE est activé."""
    if DEBUG_MODE:
        print(f"[Debug] {message}")

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
                    "Examples:\n"
                    "1. Original query: 'victor' \u2192 Refined query: 'victor hugo'\n"
                    "2. Original query: 'romantik' \u2192 Refined query: 'romantic romantique'\n"
                    "3. Original query: 'les mis' \u2192 Refined query: '\"les mis\u00e9rables\"'\n"
                    "4. Original query: 'book by hugo' \u2192 Refined query: 'victor hugo books'\n"
                    f"Original query: '{query}'\nRefined query:"
                ),
                "max_tokens": 50,
                "temperature": 0.7
            }
        )
        response.raise_for_status()

        # Récupérer la réponse brute
        enriched_query = response.json().get("choices", [{}])[0].get("text", "").strip()
        log_debug(f"Réponse brute de Phi 4 : {response.json()}")

        # Nettoyage de la réponse
        enriched_query = re.sub(r'[^a-zA-Z0-9\s\"\']', '', enriched_query).strip()

        # Vérification de la pertinence de la réponse
        if not enriched_query or enriched_query.lower() == query.lower() or len(enriched_query.split()) < 2:
            log_debug(f"Réponse enrichie non valide ou trop courte : {enriched_query}")
            return query

        log_debug(f"Requête enrichie finale : {enriched_query}")
        return enriched_query
    except Exception as e:
        log_debug(f"Erreur avec Phi 4 : {e}")
        return query  # Requête utilisateur utilisée comme fallback

def search_book(query):
    """
    Rechercher des livres dans Azure Search en utilisant une requête enrichie.
    """
    try:
        # Détecter une recherche par ISBN
        is_isbn = re.match(r'^\d{3}-\d{1,5}-\d{1,7}-\d{1,7}-\d{1}$', query)
        if is_isbn:
            log_debug("Recherche exacte pour ISBN détectée.")
            results = search_client.search(search_text=f"ISBN: \"{query}\"", filter=f"ISBN eq '{query}'")
        else:
            # Traitement de la requête avec Phi 4
            enriched_query = process_query_with_phi(query)
            log_debug(f"Requête enrichie : {enriched_query}")

            # Requête fuzzy avec Azure Search
            fuzzy_query = f"{enriched_query}~"
            log_debug(f"Requête envoyée à Azure Search : {fuzzy_query}")
            results = search_client.search(search_text=fuzzy_query)

        # Filtrer les résultats avec un score minimal
        results_list = [
            {
                "Title": res.get("Title", "Titre non disponible"),
                "Author": res.get("Author", "Auteur inconnu"),
                "Category": res.get("Category", "Catégorie non spécifiée"),
                "Description": res.get("Description", "Description non disponible"),
                "ISBN": res.get("ISBN", "N/A")
            }
            for res in results
            if res.get("@search.score", 0) >= 0.5
        ]
        log_debug(f"Résultats bruts d'Azure Search : {results_list}")

        return results_list
    except Exception as e:
        log_debug(f"Erreur lors de la recherche : {e}")
        return []

if __name__ == "__main__":
    print("\U0001F4DA Système de recherche de livres \U0001F4DA")  # Emoji pour le livre
    while True:
        query = input("\nEntrez votre recherche (ou 'exit' pour quitter) : ").strip()
        if query.lower() in ("exit", "quit"):
            print("Merci d'avoir utilisé notre système de recherche. Au revoir !")
            break

        results = search_book(query)
        if results:
            print("\n\U0001F50E Résultats :")  # Emoji pour la loupe
            for idx, result in enumerate(results, start=1):
                print(f"{idx}. {result['Title']} (Auteur : {result['Author']}, Catégorie : {result['Category']})")
        else:
            print("\nℹ️ Aucun résultat trouvé.")
