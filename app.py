import chainlit as cl
from backend import search_book

@cl.on_message
async def main(message):
    # Extraire la requête utilisateur
    query = message.content.strip()

    # Appeler la fonction de recherche dans backend.py
    results = search_book(query)

    # Construire la réponse
    if results:
        response = "Voici les informations des livres trouvés :\n\n"
        for result in results:
            response += (
                f"**ISBN**: {result.get('ISBN', 'N/A')}\n"
                f"**Title**: {result.get('Title', 'N/A')}\n"
                f"**Author**: {result.get('Author', 'N/A')}\n"
                f"**Description**: {result.get('Description', 'N/A')}\n"
                f"**Category**: {result.get('Category', 'N/A')}\n\n"
            )
    else:
        response = "Aucun livre trouvé pour votre recherche."

    # Envoyer la réponse à Chainlit
    await cl.Message(content=response).send()
