import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=TAVILY_API_KEY)

def search_sources(argument):
    results = client.search(
        query=argument,
        max_results=5
    )

    return results["results"]


if __name__ == "__main__":
    results = client.search(
        query="A Copa do Mundo FIFA 2014 foi comprada?",
        max_results=3
    )

    for source in results["results"]:
        print("Título:", source["title"])
        print("URL:", source["url"])
        print("Conteúdo:", source["content"])
        print("-" * 50)