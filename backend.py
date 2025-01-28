import os
import re
import shlex
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Initialisation des clients Azure
azure_openai_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("OPENAI_ENDPOINT")
)

search_client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name=os.getenv("SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("SEARCH_API_KEY"))
)

def process_query_with_openai(query):
    """Correction et enrichissement intelligent de la requête"""
    try:
        response = azure_openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Expert en recherche documentaire. Corrigez UNIQUEMENT les erreurs évidentes. "
                        "Conservez tous les termes originaux. Ajoutez des variantes linguistiques si pertinent. "
                        "Pour les phrases composées, utilisez des guillemets. N'utilisez PAS d'opérateurs booléens (OR/AND/NOT).\n"
                        "Exemples :\n"
                        "- 'book by victor' → 'victor hugo'\n"
                        "- 'romantik' → 'romantique romantic'\n"
                        "- 'les mis' → '\"les misérables\"'\n"
                        "- '978...' → NE RIEN MODIFIER"
                    )
                },
                {
                    "role": "user",
                    "content": f"Corrigez cette requête en conservant tous les termes : {query}"
                }
            ],
            temperature=0.3,
            max_tokens=150
        )
        optimized = response.choices[0].message.content.strip()
        return re.sub(r'\b(OR|AND|NOT)\b', ' ', optimized, flags=re.IGNORECASE)
    except Exception as e:
        print(f"Erreur OpenAI : {str(e)}")
        return query

def execute_search(query):
    """Exécution de la recherche avec stratégie avancée"""
    try:
        query = query.strip()
        
        # Vérifiez si la requête est un ISBN
        if re.match(r'^(\d+[- ]?){9,}[\dX]$', query):
            clean_isbn = re.sub(r'[^0-9X]', '', query.upper())  # Supprimer les tirets et espaces
            results = search_client.search(
                search_text="",
                query_type="simple",
                search_mode="all",
                filter=f"ISBN eq '{query}' or ISBN eq '{clean_isbn}'",
                top=1
            )
            return results
        
        # Si ce n'est pas un ISBN, procédez à la recherche classique
        tokens = shlex.split(query)
        terms = [
            f'"{token}"' if token.startswith('"') and token.endswith('"') else f"{token}~"
            for token in tokens if len(token) > 2
        ]
        search_text = " ".join(terms)
        
        return search_client.search(
            search_text=search_text,
            query_type="full",
            search_mode="all",
            search_fields=["Title", "Author", "Category", "Description", "ISBN"],
            top=10,
            include_total_count=True
        )
    except Exception as e:
        print(f"Erreur de recherche : {str(e)}")
        return []

def format_results(results):
    """Formatage des résultats avec validation robuste"""
    if not results:
        return "Aucun résultat trouvé."

    output = []
    for result in results:
        try:
            entry = [
                f"• {result['Title']}",
                f"  Auteur : {result.get('Author', 'Inconnu')}",
                f"  Catégorie : {result.get('Category', 'Général')}",
                f"  ISBN : {result.get('ISBN', 'N/A')}",
                f"  Description : {result.get('Description', '')[:120]}..."
            ]
            output.append("\n".join(entry))
        except KeyError as e:
            print(f"Champ manquant : {str(e)}")
    
    return "\n\n".join(output) if output else "Aucun résultat correspondant aux critères."

def search_book(query):
    """Workflow complet de recherche avec prise en charge ISBN"""
    if not query.strip():
        return "Veuillez entrer une requête valide."
    
    # Vérifiez si la requête est un ISBN
    if re.match(r'^(\d+[- ]?){9,}[\dX]$', query):
        # Nettoyage et formatage de l'ISBN
        raw_isbn = query.strip()
        clean_isbn = re.sub(r'[^0-9X]', '', raw_isbn.upper())  # Supprimer les tirets et espaces
        print(f"[Debug] Recherche directe par ISBN : {raw_isbn} et {clean_isbn}")
        
        try:
            # Essayer les deux formats : avec et sans tirets
            results = search_client.search(
                search_text="",
                query_type="simple",
                search_mode="all",
                filter=f"ISBN eq '{raw_isbn}' or ISBN eq '{clean_isbn}'",
                top=1
            )
            return format_results(results)
        except Exception as e:
            print(f"Erreur lors de la recherche par ISBN : {str(e)}")
            return "Erreur lors de la recherche par ISBN. Veuillez réessayer."
    
    # Si ce n'est pas un ISBN, passez par le traitement standard
    try:
        optimized_query = process_query_with_openai(query)
        print(f"[Debug] Requête initiale : '{query}' → Optimisée : '{optimized_query}'")
        
        search_results = execute_search(optimized_query)
        return format_results(search_results)

    except Exception as e:
        print(f"Erreur système : {str(e)}")
        return "Erreur temporaire du système. Veuillez réessayer."

# Interface utilisateur
if __name__ == "__main__":
    print("📖 Système de recherche de livres - Mode interactif 📖\n")
    
    while True:
        try:
            query = input("\nEntrez votre recherche (ou 'exit' pour quitter) : ").strip()
            if query.lower() in ('exit', 'quit'):
                print("\nMerci d'avoir utilisé notre système de recherche. Au revoir !")
                break
                
            results = search_book(query)
            
            if "Aucun résultat" not in results:
                print("\n🔎 Résultats de la recherche :")
                print(results)
            else:
                print("\nℹ️ " + results)
                
        except KeyboardInterrupt:
            print("\nRecherche annulée par l'utilisateur.")
            break
        except Exception as e:
            print(f"\n⚠️ Erreur inattendue : {str(e)}")
