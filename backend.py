import openai
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Configuration Azure OpenAI
openai_endpoint = "https://webmatchingevalmodel.openai.azure.com"
openai_key = "606863432472474983eb27639e3e175c"
api_version = "2023-03-15-preview"
model = "gpt-4"

openai.api_type = "azure"
openai.api_base = openai_endpoint
openai.api_version = api_version
openai.api_key = openai_key

# Configuration Azure Search
search_endpoint = "https://imensearch.search.windows.net"
index_name = "library"
search_api_key = "wXcEg4PRUhGsKaASOcWCbeHDOQzZ9IhaKEva7Ezea0AzSeDNeBWV"

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

        # Étape 3 : Filtrer les résultats pour éviter les correspondances globales
        filtered_results = [
            result for result in results
        ]

        return filtered_results

    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return []
