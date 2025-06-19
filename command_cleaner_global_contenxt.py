import discord
from discord import app_commands
from dotenv import load_dotenv
load_dotenv()
from os import getenv

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    for guild in client.guilds:
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)

client.run(DISCORD_TOKEN)
