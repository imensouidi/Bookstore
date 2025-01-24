import chainlit as cl
from backend import search_book

# État utilisateur pour suivre les conversations
user_state = {}

@cl.on_message
async def main(message):
    # Obtenez l'identifiant utilisateur
    user_id = getattr(message.author, "id", message.author)
    query = message.content.strip()

    # Initialiser l'état de l'utilisateur s'il n'existe pas encore
    if user_id not in user_state:
        user_state[user_id] = {"results": [], "action": None}

    # Vérifiez si une action précédente est en attente
    if user_state[user_id]["action"] == "details":
        book_title = query
        results = user_state[user_id]["results"]
        book_details = next(
            (result for result in results if result.get("Title", "").lower() == book_title.lower()), None
        )
        user_state[user_id]["action"] = None  # Réinitialiser l'action

        if book_details:
            response = (
                f"**Détails pour '{book_title}'** :\n"
                f"**Auteur :** {book_details.get('Author', 'N/A')}\n"
                f"**Description :** {book_details.get('Description', 'N/A')}\n"
                f"**Catégorie :** {book_details.get('Category', 'N/A')}\n"
                f"**ISBN :** {book_details.get('ISBN', 'N/A')}\n"
            )
        else:
            response = "Aucun livre trouvé avec ce titre. Essayez un autre titre."
        await cl.Message(content=response).send()
        return

    # Sinon, effectuer une recherche normale
    results = search_book(query)
    user_state[user_id]["results"] = results

    if results:
        response = "Voici les livres trouvés :\n\n"
        for result in results:
            response += (
                f"**Titre :** {result.get('Title', 'N/A')}\n"
                f"**Auteur :** {result.get('Author', 'N/A')}\n"
                f"**Catégorie :** {result.get('Category', 'N/A')}\n"
                f"**Description :** {result.get('Description', 'N/A')}\n\n"
            )
        response += "- Tapez **Plus d'informations** et indiquez le titre d'un livre pour plus de détails.\n"
    else:
        response = f"Aucun livre trouvé pour '{query}'. Voulez-vous reformuler votre requête ?"

    await cl.Message(content=response).send()

@cl.on_message
async def handle_followup(message):
    user_id = getattr(message.author, "id", message.author)
    query = message.content.strip().lower()

    if query == "plus d'informations":
        user_state[user_id]["action"] = "details"
        await cl.Message(content="Indiquez le titre du livre pour lequel vous souhaitez plus d'informations :").send()
    else:
        await main(message)  # Retour à la recherche principale