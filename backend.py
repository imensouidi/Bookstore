from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Configuration Azure Search
 
endpoint = "https://imensearch.search.windows.net"
index_name = "library"
api_key = "wXcEg4PRUhGsKaASOcWCbeHDOQzZ9IhaKEva7Ezea0AzSeDNeBWV"

# Initialisation du client Azure Search
search_client = SearchClient(endpoint=endpoint,
                              index_name=index_name,
                              credential=AzureKeyCredential(api_key))

def search_book(query):
   
    # Vérifier si la requête est un ISBN (commence par "978")
    if query.startswith("978"):
        filter_query = f"ISBN eq '{query}'"  # Filtre exact sur le champ ISBN
        results = search_client.search(search_text="", filter=filter_query)
    elif "Fiction" in query:  # Vérifier si la requête concerne une catégorie
        filter_query = f"Category eq '{query}'"  # Filtre exact sur le champ Category
        results = search_client.search(search_text="", filter=filter_query)
    else:
        # Recherche texte libre pour d'autres types de requêtes
        results = search_client.search(search_text=query)

    return [result for result in results]
