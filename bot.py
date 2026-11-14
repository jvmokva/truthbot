import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from teste import valid_input, MAX_ARGUMENT_LENGTH
from ai import check_claim
import asyncio
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
GUILD_ID = 392439823316811776
guild = discord.Object(id=GUILD_ID)

# o discord recusa mensagens com mais de 2000 caracteres, e quando isso
# acontecia o bot travava no "pensando..." sem responder nada. agora o texto
# é cortado (na mensagem de espera) ou dividido (na resposta) antes de ser enviado.
DISCORD_MAX_CHARS = 2000


def truncate(text, limit=DISCORD_MAX_CHARS):
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


# cortar a resposta da ia fazia o usuário perder o final dela, justamente onde
# ficam as fontes. então ela é dividida em partes de até 2000 caracteres,
# quebrando de preferência numa linha, depois num espaço, pra não partir
# uma url ou uma palavra no meio. se a última linha estiver muito no começo,
# usa o espaço, senão a primeira mensagem sairia quase vazia.
def split_message(text, limit=DISCORD_MAX_CHARS):
    parts = []

    while len(text) > limit:
        cut = text.rfind("\n", 0, limit + 1)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit + 1)
        if cut <= 0:
            cut = limit

        parts.append(text[:cut])
        text = text[cut:].lstrip("\n ")

    if text:
        parts.append(text)

    return parts


@tree.command(
    name="factcheck",
    description="Verifica a veracidade de uma afirmação.",
    guild=guild
)

async def factcheck(interaction: discord.Interaction, argumento: str):
    if valid_input(argumento):
        await interaction.response.defer(thinking=True)
        
        await interaction.edit_original_response(
            content=truncate(f"Aguarde, fazendo a checagem de fatos para: {argumento}")
        )

        try:
            result = await asyncio.to_thread(check_claim, argumento)

        except Exception as error:
            print(f"Erro durante a checagem: {error}")

            # esta mensagem precisa ficar dentro do except e não alinhada no try,
            # sempre que rodava, apagava a resposta da ia, e o usuário recebia
            # um "problema técnico" mesmo quando dava certo.
            result = (
                "Não foi possível concluir a checagem de fatos devido "
                "a um problema técnico. Por favor, tente novamente mais tarde."
            )

        # a primeira parte substitui o "aguarde...", e o resto vai em
        # mensagens novas logo abaixo.
        parts = split_message(result)
        await interaction.edit_original_response(content=parts[0])
        for part in parts[1:]:
            await interaction.followup.send(part)
        
    # antes, quem mandava um texto grande demais recebia "você não forneceu
    # argumentos suficientes", o que é justamente o contrário do problema.
    # agora cada caso tem a sua própria mensagem.
    elif len(argumento.strip()) > MAX_ARGUMENT_LENGTH:
        await interaction.response.send_message(
            f"Sua afirmação é muito longa. Use no máximo {MAX_ARGUMENT_LENGTH} "
            "caracteres e tente novamente."
        )

    else:
        await interaction.response.send_message(
            "Você não forneceu argumentos suficientes para uma checagem, por favor tente novamente."
        )
    
@client.event
async def on_ready():
    synced = await tree.sync(guild=guild)
    print(f"Comandos sincronizados: {len(synced)}")
    print(f"TruthBot conectado como {client.user}")
    
client.run(TOKEN)
