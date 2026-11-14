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
# é cortado antes de ser enviado.
DISCORD_MAX_CHARS = 2000


def truncate(text, limit=DISCORD_MAX_CHARS):
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


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

        await interaction.edit_original_response(content=truncate(result))
        
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
