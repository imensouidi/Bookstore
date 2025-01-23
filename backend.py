import os
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration Azure OpenAI
openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_key = os.getenv("OPENAI_KEY")
api_version = os.getenv("OPENAI_API_VERSION")
model = os.getenv("OPENAI_MODEL")

# Initialize Azure OpenAI client
azure_openai_client = AzureOpenAI(
    api_key=openai_key,
    api_version=api_version,
    azure_endpoint=openai_endpoint
)

# Configuration Azure Search
search_endpoint = os.getenv("SEARCH_ENDPOINT")
index_name = os.getenv("SEARCH_INDEX_NAME")
search_api_key = os.getenv("SEARCH_API_KEY")

# Initialize Azure Search client
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_api_key)
)

def process_query_with_openai(query):
    """
    Use Azure OpenAI to enrich and rephrase the user query.
    """
    try:
        response = azure_openai_client.chat.completions.create(
            model=model,  # Use the deployment name of your model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intelligent assistant that helps search for books in a library. "
                        "Understand the user query and enrich it by adding similar terms and relevant keywords "
                        "to improve the search. Use only the information provided in the query."
                    )
                },
                {
                    "role": "user",
                    "content": f"Here is a user query: {query}. Improve it to make it more precise and effective."
                }
            ],
            max_tokens=300,  # Adjust as needed
            temperature=0.7  # Adjust for creativity
        )
        # Extract the enriched query
        enriched_query = response.choices[0].message.content.strip()
        return enriched_query
    except Exception as e:
        print(f"Error communicating with Azure OpenAI: {e}")
        return query  # Return the original query in case of an error

def reformat_results_with_openai(results):
    """
    Use Azure OpenAI to reformat the search results into a human-readable format.
    """
    try:
        # Extract relevant fields from the search results
        formatted_results = []
        for result in results:
            title = result.get("Title", "Unknown Title")
            author = result.get("Author", "Unknown Author")
            category = result.get("Category", "Unknown Category")
            description = result.get("Description", "No description available.")
            isbn = result.get("ISBN", "Unknown ISBN")

            # Format each result as a string
            formatted_result = (
                f"Title: {title}\n"
                f"Author: {author}\n"
                f"Category: {category}\n"
                f"Description: {description}\n"
                f"ISBN: {isbn}\n"
            )
            formatted_results.append(formatted_result)

        # Combine all formatted results into a single string
        results_str = "\n".join(formatted_results)

        # Send the formatted results to OpenAI for reformatting
        response = azure_openai_client.chat.completions.create(
            model=model,  # Use the deployment name of your model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intelligent assistant that helps format search results into a human-readable format. "
                        "Reformat the following search results into a clear and concise summary. "
                        "Include the title, author, category, and a brief description for each book. "
                        "Use only the information provided in the search results."
                    )
                },
                {
                    "role": "user",
                    "content": f"Here are the search results:\n{results_str}\n\nReformat them into a human-readable summary."
                }
            ],
            max_tokens=500,  # Adjust as needed
            temperature=0.5  # Adjust for creativity
        )
        # Extract the reformatted results
        reformatted_results = response.choices[0].message.content.strip()
        return reformatted_results
    except Exception as e:
        print(f"Error reformatting results with OpenAI: {e}")
        return results  # Return the original results in case of an error

def search_book(query):
    """
    Search for books in Azure Search with precise matches for categories.
    """
    try:
        # Step 1: Enrich the query with OpenAI
        enriched_query = process_query_with_openai(query)

        # Step 2: Apply fuzzy matching to the enriched query
        fuzzy_query = f"{enriched_query}~"

        # Step 3: Search Azure Search
        results = search_client.search(search_text=fuzzy_query)

        # Step 4: Reformat the results using OpenAI
        reformatted_results = reformat_results_with_openai(results)

        return reformatted_results

    except Exception as e:
        print(f"Error during search: {e}")
        return []

# Example usage with dynamic query input
if __name__ == "__main__":
    while True:
        query = input("Enter your search query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        results = search_book(query)
        
        if results:
            print("Reformatted Search Results:")
            print(results)
        else:
            print("No results found.")
