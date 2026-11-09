import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from teste import valid_input
from ai import check_claim
import asyncio
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
GUILD_ID = 392439823316811776
guild = discord.Object(id=GUILD_ID)

@tree.command(
    name="factcheck",
    description="Verifica a veracidade de uma afirmação.",
    guild=guild
)

async def factcheck(interaction: discord.Interaction, argumento: str):
    if valid_input(argumento):
        await interaction.response.defer(thinking=True)
        
        await interaction.edit_original_response(
            content=f"Aguarde, fazendo a checagem de fatos para: {argumento}"
        )

        try:
            result = await asyncio.to_thread(check_claim, argumento)

        except Exception as error:
         print(f"Erro durante a checagem: {error}")

        result = (
            "Não foi possível concluir a checagem de fatos devido "
            "a um problema técnico. Por favor, tente novamente mais tarde."
        )

        await interaction.edit_original_response(content=result)
        
    else:
        await interaction.response.send_message(
            f"Você não forneceu argumentos suficientes para uma checagem, por favor tente novamente."
        )
    
@client.event
async def on_ready():
    synced = await tree.sync(guild=guild)
    print(f"Comandos sincronizados: {len(synced)}")
    print(f"TruthBot conectado como {client.user}")
    
client.run(TOKEN)
