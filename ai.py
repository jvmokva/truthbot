
from google import genai
from dotenv import load_dotenv
from google.genai import types
from search import search_sources
from unittest.mock import patch
from urllib.parse import urlparse
import time

load_dotenv()

client = genai.Client()


def check_claim(argument):
    sources = search_sources(argument)
    unique_urls = set()
    unique_sources = []
    
    for source in sources:
        if (
            not source.get("url", "").strip()
            or not source.get("content", "").strip()
    ):
            continue

        parsed_url = urlparse(source["url"])

        if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
            continue

        if source["url"] not in unique_urls:
            unique_urls.add(source["url"])
            unique_sources.append(source)

                
    if len(unique_urls) < 3:
        return (
            "Não existem fontes confiáveis que neguem ou comprovem tal "
            "afirmação/pergunta/questionamento. "
            "Você pode tentar uma nova checagem de fatos."
        )
    sources_text = ""

    for source in unique_sources:
        sources_text += f"Título: {source.get('title') or 'Título indisponível'}\n"
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
6. Se não houver pelo menos três fontes relevantes e confiáveis
   que permitam verificar a afirmação, não apresente um veredito.

   Nesse caso, responda exclusivamente com a seguinte mensagem:

   Não existem fontes confiáveis que neguem ou comprovem tal afirmação/pergunta/questionamento. Você pode tentar uma nova checagem de fatos.

   Não acrescente explicações, títulos ou URLs à mensagem.
7. Se as fontes confiáveis apresentarem evidências
   contraditórias que impeçam uma conclusão segura:

   - Não apresente um veredito definitivo.
   - Explique objetivamente quais informações estão
     em conflito.
   - Resuma as evidências de cada uma das três fontes.
   - Apresente os títulos e URLs das três fontes.
   - Informe que não foi possível estabelecer
     uma conclusão segura.

   Não considere uma simples diferença de opinião
   como uma contradição factual.
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

    # quando o gemini bloqueia a resposta (por filtro de segurança, por exemplo),
    # o response.text vem vazio, e o bot mandava uma mensagem em branco ou dava
    # erro. agora o usuário recebe um aviso no lugar.
    if not response.text:
        return (
            "Não foi possível gerar uma resposta para essa checagem. "
            "Tente reformular a afirmação."
        )

    return response.text


if __name__ == "__main__":
    fake_sources = [
        {
            "url": "https://site-a.com",
            "title": "Notícia A",
            "content": "Informações da notícia A."
        },
        {
            "url": "isso-nao-e-um-link",
            "title": "Notícia B",
            "content": "Informações da notícia B."
        },
        {
            "url": "https://site-c.com",
            "title": "Notícia C",
            "content": "Informações da notícia C."
        }
    ]

    with patch("__main__.search_sources", return_value=fake_sources):
        result = check_claim("A Terra é plana?")
        print(result)