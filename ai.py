
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
        contents=f"""
Você é um verificador de fatos (fact-checker).

Sua tarefa é analisar a afirmação apresentada utilizando as fontes
encontradas pela pesquisa.

AFIRMAÇÃO:
{argument}

FONTES ENCONTRADAS:
{sources_text}

INSTRUÇÕES:
1. Analise as evidências antes de apresentar uma conclusão.
2. Não invente informações, dados ou fontes.
3. Utilize somente informações sustentadas pelas evidências apresentadas.
4. Classifique a afirmação como:
   - Verdadeira
   - Falsa
   - Parcialmente verdadeira
   - Inconclusiva
5. Apresente até três fontes relevantes e confiáveis, com seus respectivos títulos e URLs.
6. Se não encontrar fontes suficientes, informe isso claramente.
7. Se houver divergências entre as fontes, explique-as.
8. Explique brevemente o motivo da conclusão.

FORMATO DA RESPOSTA:
Veredito:
Justificativa:
Fontes:
""",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            )
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
