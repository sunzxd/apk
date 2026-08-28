import discord
from dotenv import load_dotenv
from os import getenv
from router import check_for, mkfrwl, turn_firewall, dscd
import requests
import subprocess
from req import event, monitor
import threading
import asyncio
import re
load_dotenv()
token = getenv("bott")
from discord.ext import commands, tasks
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
async def loop():
    me = await bot.fetch_user(793061880746082344)
    while True:
        data = dict(await event.get())
        if await asyncio.to_thread(check_for, data["MAC"].strip().upper()):
            data["FIREWALL"] = "Есть"
        else:
            data["FIREWALL"] = "Нету"
        if data["NAME"] == None:
            await me.send(f"# Подключено устройство.\n\n**IP:** *{data["IP"]}*\n**MAC:** *{data["MAC"]}*\n**FIREWALL:** *{data['FIREWALL']}*")
        else:
            await me.send(f"# Подключено устройство.\n\n**IP:** *{data["IP"]}*\n**MAC:** *{data["MAC"]}*\n**NAME:** *{data['NAME']}*\n**FIREWALL:** *{data['FIREWALL']}*")
laptop_active = False
@tasks.loop(minutes=1)
async def check_active():
    global laptop_active
    me = await bot.fetch_user(793061880746082344)
    if not laptop_active:
        try:
            request = await asyncio.to_thread(
                requests.get,
                "http://192.168.1.129:8000/is_active",
                timeout=5
            )
        except requests.exceptions.ConnectTimeout:
            laptop_active = False
            return
        if request.status_code == 200:
            laptop_active = True
            await me.send("Ноутбук запущен.")
    if laptop_active:
            try:
                request = await asyncio.to_thread(
                    requests.get,
                    "http://192.168.1.129:8000/is_active",
                    timeout=5
                )
            except requests.exceptions.ConnectTimeout:
                laptop_active = False
                await me.send("Ноутбук выключен.")
@bot.event
async def on_ready():
    me = await bot.fetch_user(793061880746082344)
    if me:
        await me.send("Я запущен.")
    check_active.start()
    asyncio.create_task(monitor())
    asyncio.create_task(loop())
@bot.event
async def on_message(message):
    print("MESSAGE:", message.content)
    await bot.process_commands(message)
@bot.command()
async def run(ctx: commands.Context, *, text=None):
   if ctx.author.name == "bonusniikloun":
        if text:
            try:
                process = await asyncio.to_thread(
                    subprocess.run,
                    text,
                    capture_output=True,
                    shell=True,
                    timeout=15
                )
                result = process.stderr if process.stderr else process.stdout
                await ctx.send(f"# $ {text}\n**Успешно.**\n\n**Вывод:**\n*{result.decode().strip()}*")
            except subprocess.TimeoutExpired:
                await ctx.send(f"# $ {text}\n**Ошибка:** *timeout expired*")
        else:
            await ctx.send(f"# $ ...\n**Вставь команду.**")
@bot.command()
async def runl(ctx: commands.Context, *, text=None):
    def make_request():
        return requests.get(url=f"http://192.168.1.129:8000/run?cmd={text}", timeout=5).json()
    if ctx.author.name == "bonusniikloun":
        if text:
            result = await asyncio.to_thread(make_request)
            output = result['content'][0]['stdout'] if result['content'][0]['stdout'] else result['content'][0]['stderr']
            await ctx.send(f"# $ {text}(l)\n**Успешно.**\n\n**Вывод:**\n*{output.strip()}*")
        else:
            await ctx.send(f"# $ ...(l)\n**Вставь команду.**")  
@bot.command()
async def firewall(ctx: commands.Context, *, text=None):
    if text:
        print("УВИДЕЛ ТЕКСТ")
        text = text.strip().upper()
        print("ОТПРАВИЛ ДВА ЗАПРОСА")  
    elif ctx.message.reference:
        replied_message = await ctx.fetch_message(
            ctx.message.reference.message_id
        )
        mac = re.search(r'[0-9a-f]{2}(:[0-9a-f]{2}){5}', replied_message.content.lower())
        if mac:
            text = mac.group(0).strip().upper()
        else:
            await ctx.send("# ❌ Не дан MAC.")
    else:
        await ctx.send("# ❌ Не дан MAC.")
    active_firewall, do = await asyncio.gather(
        asyncio.to_thread(check_for, mac=text),
        asyncio.to_thread(turn_firewall, mac=text),
    )
    
    print("ПРИШЛИ ДВА ОТВЕТА")
    if do:
        if active_firewall:
            await ctx.send(f"# FIREWALL OFF\n**For MAC:** *{text.upper().strip()}*")
        else:
            await ctx.send(f"# FIREWALL ON\n**For MAC:** *{text.upper().strip()}*")
@bot.command()
async def discnnt(ctx: commands.Context, *, text=None):
    if text:
        print("УВИДЕЛ ТЕКСТ")
        text = text.strip().upper()
        print("ОТПРАВИЛ ДВА ЗАПРОСА")  
    elif ctx.message.reference:
        replied_message = await ctx.fetch_message(
            ctx.message.reference.message_id
        )
        mac = re.search(r'[0-9a-f]{2}(:[0-9a-f]{2}){5}', replied_message.content.lower())
        if mac:
            text = mac.group(0).strip().upper()
        else:
            await ctx.send("# ❌ Не дан MAC.")
    else:
        await ctx.send("# ❌ Не дан MAC.")
    result = await asyncio.to_thread(dscd, mac=text)
    if result:
        await ctx.send(f"# ✅ SUCCESS.\n**Успешно отключено устройство.**\n**MAC:** *{text}*")
        return
    await ctx.send(f"# ❌ SMTH WENT WRONG.\n**MAC:** *{text}*")
@bot.command()
async def blkin(ctx: commands.Context):
    if ctx.author.name == "bonusniikloun":
            process = await asyncio.to_thread(
                subprocess.run,
                "modprobe -r usbhid",
                capture_output=True,
                shell=True,
                timeout=15
            )
            result = process.stderr if process.stderr else process.stdout
            await ctx.send(f"# $ modprobe -r usbhid\n**Успешно.**\n\n**Вывод:**\n*{result.decode().strip()}*")
@bot.command()
async def unblkin(ctx: commands.Context):
    if ctx.author.name == "bonusniikloun":
            process = await asyncio.to_thread(
                subprocess.run,
                "modprobe usbhid",
                capture_output=True,
                shell=True,
                timeout=15
            )
            result = process.stderr if process.stderr else process.stdout
            await ctx.send(f"# $ modprobe -r usbhid\n**Успешно.**\n\n**Вывод:**\n*{result.decode().strip()}*")
bot.run(token)