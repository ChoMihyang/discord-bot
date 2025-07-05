import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from dotenv import load_dotenv
import os
import re

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # 유저 메시지 읽기 허용
bot = commands.Bot(command_prefix="!", intents=intents)

scheduled_tasks = {}  # 유저별 알림 저장

def parse_date(text):
    # ① 정규식 패턴: 7/1, 7월1일, 7.10, 7月1日
    pattern = r'(\d{1,2})\s*(?:/|\.|월|月)\s*(\d{1,2})\s*(?:일|日)?'
    match = re.search(pattern, text)
    
    if match:
        try:
            month, day = int(match.group(1)), int(match.group(2))
            return datetime.datetime(datetime.datetime.now().year, month, day)
        except ValueError:
            return None
    return None

@bot.event
async def on_ready():
    print(f"🤖 봇 로그인 완료: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    input_date = parse_date(message.content)
    if input_date:
        now = datetime.datetime.now()
        target = input_date.replace(year=now.year)
        if target < now:
            target = target.replace(year=now.year + 1)

        user = message.author
        channel = message.channel
        await channel.send(f"{user.mention} 님의 학습 챌린지를 예약했어요! {target.strftime('%m/%d')}까지 매일 오후 9시에 알림을 보낼게요.")

        # 기존 예약이 있다면 취소
        if user.id in scheduled_tasks:
            scheduled_tasks[user.id].cancel()

        task = bot.loop.create_task(schedule_challenge(user, channel, target))
        scheduled_tasks[user.id] = task

async def schedule_challenge(user, channel, end_date):
    while True:
        now = datetime.datetime.now()
        next_9pm = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now > next_9pm:
            next_9pm += datetime.timedelta(days=1)

        await asyncio.sleep((next_9pm - now).total_seconds())

        if datetime.datetime.now().date() > end_date.date():
            await channel.send(f"{user.mention} 님의 학습 챌린지가 종료되었습니다 🎉")
            break

        await channel.send(f"{user.mention} 학습 챌린지 도전!")

bot.run(TOKEN)
