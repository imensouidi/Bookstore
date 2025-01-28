import chainlit as cl
from backend import search_book

# Mémoire pour stocker les résultats lors d'une recherche
stored_results = {}


@cl.on_message
async def main(message: cl.Message):
    global stored_results

    # Requête initiale ou interaction
    query = message.content.strip()

    # Si aucune requête n'est fournie
    if not query:
        await cl.Message(content="❌ Veuillez entrer une requête valide.").send()
        return

    # Cas 1 : L'utilisateur demande "plus d'informations"
    if query.lower() == "plus d'informations":
        if not stored_results:
            await cl.Message(content="ℹ️ Vous devez effectuer une recherche avant de demander plus d'informations.").send()
            return

        await cl.Message(content="🔎 Entrez le titre exact du livre pour afficher plus d'informations :").send()
        return

    # Cas 2 : Recherche spécifique d'un titre pour plus d'informations
    if query in stored_results:
        detailed_info = stored_results[query]
        await cl.Message(content=f"📖 Informations détaillées pour '{query}' :\n\n{detailed_info}").send()
        return

    # Cas 3 : Nouvelle recherche ou requête utilisateur
    results = search_book(query)

    if "Aucun résultat" in results:
        await cl.Message(content="ℹ️ Aucun résultat trouvé. Essayez avec une autre requête.").send()
        return

    # Traitement et affichage des résultats (titre + auteur uniquement)
    await cl.Message(content="🔎 Résultats de la recherche (titre et auteur uniquement) :").send()
    books = []
    stored_results = {}  # Réinitialisation des résultats stockés

    # Traitement des résultats
    for line in results.split("\n\n"):  # Supposons que les résultats soient séparés par des sauts de ligne
        try:
            lines = line.split("\n")
            title = lines[0].replace("• ", "").strip()
            author = lines[1].replace("Auteur : ", "").strip()
            books.append(f"- **{title}** (par {author})")

            # Stocker les informations détaillées pour la recherche ultérieure
            stored_results[title] = line

        except IndexError:
            continue

    # Afficher les titres et auteurs
    if books:
        await cl.Message(content="\n".join(books)).send()

    # Proposer la suite
    await cl.Message(
        content="ℹ️ Si vous voulez plus d'informations sur un livre, tapez **plus d'informations**.\n"
                "Sinon, vous pouvez effectuer une nouvelle recherche."
    ).send()
