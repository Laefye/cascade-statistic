from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from os import getenv
import discord
from discord import app_commands
from stat_generator import generate_stats, generate_top_by_messages, generate_top_by_voice
from tempfile import NamedTemporaryFile
from models import create_tables, add_message, add_voice_session, get_message_count, get_voice_session_duration, get_top_by_messages, get_top_by_voice
from datetime import datetime
from enum import Enum

class TopType(Enum):
    messages = "по колличеству сообщений"
    voice = "во времени в войсах"


create_tables()


DISCORD_TOKEN = getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True



voices = {

}


client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    for guild in client.guilds:
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
    
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.guild is None:
        return
    add_message(message.guild.id, message.author.id)

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member.bot:
        return

    guild_id = member.guild.id
    user_id = member.id

    if before.channel is None and after.channel is not None:
        if guild_id not in voices:
            voices[guild_id] = {}
        voices[guild_id][user_id] = int(datetime.now().timestamp())
    elif before.channel is not None and after.channel is None:
        if guild_id in voices and user_id in voices[guild_id]:
            timestamp_in = voices[guild_id][user_id]
            timestamp_out = int(datetime.now().timestamp())
            add_voice_session(guild_id, user_id, timestamp_in, timestamp_out)
            del voices[guild_id][user_id]

    print(voices)

@tree.command(name="stats", description="Получает вашу статистику")
@app_commands.describe(
    user="Пользователь, для которого нужно получить статистику (по умолчанию вы)"
)
async def stats_command(interaction: discord.Interaction, user: Optional[discord.Member]):
    if user is None:
        user = interaction.user

    caller = interaction.user.name
    username = user.name
    display_name = user.display_name
    count_messages = get_message_count(user.id, interaction.guild.id)
    time_in_voice = get_voice_session_duration(user.id, interaction.guild.id)

    image = generate_stats(caller, username, display_name, count_messages, time_in_voice)
    with NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        image.save(temp_file.name)
        await interaction.response.send_message(file=discord.File(temp_file.name))

@tree.command(name="top", description="Получает топ пользователей")
@app_commands.describe(
    by="Тип топа (сообщения или голос)"
)
async def top(interaction: discord.Interaction, by: TopType):
    if by == TopType.messages:
        top_users = get_top_by_messages(interaction.guild.id, top_n=10)
        user_stats = []
        for user_id, message_count in top_users:
            user = interaction.guild.get_member(user_id)
            if user:
                user_stats.append((user.display_name, message_count))
        user_stats = sorted(user_stats, key=lambda x: x[1], reverse=True)[:10]
        image = generate_top_by_messages(interaction.user.name, user_stats, top_n=10)
    elif by == TopType.voice:
        top_users = get_top_by_voice(interaction.guild.id, top_n=10)
        user_stats = []
        for user_id, voice_duration in top_users:
            user = interaction.guild.get_member(user_id)
            if user:
                user_stats.append((user.display_name, voice_duration))
        user_stats = sorted(user_stats, key=lambda x: x[1], reverse=True)[:10]
        image = generate_top_by_voice(interaction.user.name, user_stats, top_n=10)

    with NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        image.save(temp_file.name)
        await interaction.response.send_message(file=discord.File(temp_file.name))

client.run(DISCORD_TOKEN)
