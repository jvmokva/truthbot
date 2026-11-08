import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from teste import valid_input
from ai import check_claim

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
            content=f"Aguarde, fazendo a checagem de fatos... para: {argumento}"
        )

        result = check_claim(argumento)
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
