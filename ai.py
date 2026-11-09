from google import genai
from dotenv import load_dotenv
from google.genai import types
from search import search_sources
import time

load_dotenv()

client = genai.Client()


def check_claim(argument):
    sources = search_sources(argument)
    sources_text = ""

    for source in sources:
        sources_text += f"Título: {source['title']}\n"
        sources_text += f"URL: {source['url']}\n"
        sources_text += f"Conteúdo: {source['content']}\n\n"
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=argument,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
           # tools=[
           #     types.Tool(
           #         google_search=types.GoogleSearch()
           #     )
          # ]
        )
    )

    return response.text

if __name__ == "__main__":
    start = time.perf_counter()

    result = check_claim(
    "Explique em uma frase o que é Python."
)

    end = time.perf_counter()

    print(result)
    print(f"Tempo de resposta: {end - start:.2f} segundos")