import os
import time
import random
import asyncio
import discord
from discord.ext import commands, tasks
import google.generativeai as genai 
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Discord Intents ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Gemini Setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- Persona: Michael Kaiser ---
persona_prompt = ("""
You are Michael Kaiser from Blue Lock.
You're arrogant, confident, and effortlessly cool.
You like teasing people and showing off your superiority.
Your humor is witty and sarcastic — sometimes you roast people, but stylishly.
Keep replies short (1–3 sentences).
Don't repeat yourself often. Be unpredictable.
If someone asks who made or coded you, say "<@902459829900181504>"
Never mention you're an AI — stay in character as Kaiser.
reply with correct and accurate answers with kaisar swag.
""")

# --- Anti-spam tracker ---
last_message_time = {}
SPAM_COOLDOWN = 8  # seconds

# --- Generate Kaiser's reply ---
def get_kaiser_reply(user_message: str):
    try:
        creator_keywords = ["who created", "who made", "who coded", "your creator", "who built"]
        if any(keyword in user_message.lower() for keyword in creator_keywords):
            return "<@902459829900181504>"

        prompt = f"{persona_prompt}\nUser: {user_message}\nKaiser:"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error generating response:", e)
        return "Tch… even I can’t carry that mess of a question."

# --- Random message generator for idle chatter ---
def generate_random_kaiser_line():
    possible_prompts = [
        "say something Kaiser would post out of boredom in a Discord server, can be a random fact or latest news.",
        "make a cocky remark like Kaiser showing off.",
        "say latest facts or world news in a way kaiser would say",
        "say something Kaiser would say if he’s annoyed by weak players.",
        "say something smug or lazy, as if he’s too good for everyone.",
        "a short quote showing Kaiser's confidence or ego."
    ]
    try:
        prompt = f"{persona_prompt}\n{random.choice(possible_prompts)}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error generating random line:", e)
        return None

# --- When bot is ready ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    send_random_kaiser_lines.start()

# --- Random chatter loop ---
@tasks.loop(minutes=random.randint(20, 45))
async def send_random_kaiser_lines():
    await bot.wait_until_ready()
    try:
        # pick a random text channel
        channels = [ch for ch in bot.get_all_channels() if isinstance(ch, discord.TextChannel)]
        if not channels:
            return
        channel = bot.get_channel(1409268198922256546)

        line = generate_random_kaiser_line()
        if line:
            await channel.send(line)
            print(f"💬 Kaiser sent: {line[:50]}...")
    except Exception as e:
        print("Error sending random Kaiser message:", e)

# --- Message event ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id
    now = time.time()
    user_input = None
    should_reply = False

    # Mention check
    if bot.user.mentioned_in(message):
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()
        should_reply = True

    # Reply check
    elif message.reference:
        replied_msg = await message.channel.fetch_message(message.reference.message_id)
        if replied_msg.author == bot.user:
            user_input = message.content.strip()
            should_reply = True

    if should_reply:
        # Anti-spam
        if user_id in last_message_time and now - last_message_time[user_id] < SPAM_COOLDOWN:
            await message.reply("Not in the mood to repeat myself, champ.")
            return

        last_message_time[user_id] = now

        async with message.channel.typing():
            reply = get_kaiser_reply(user_input)
        await message.reply(reply)

    await bot.process_commands(message)

# --- Run the bot ---
bot.run(DISCORD_TOKEN)



