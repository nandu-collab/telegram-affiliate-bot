import os
import requests
from telegram import Bot, ParseMode
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

TRUSTED_DOMAINS = ["amazon", "flipkart", "myntra", "ajio", "meesho"]

def fetch_deals():
    url = "https://api.cuelinks.com/v2/deals.json?per_page=10&page=1"
    headers = {"Authorization": f"Token token={CUELINKS_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        deals = response.json().get("deals", [])
        return [
            deal for deal in deals
            if any(domain in deal["deal_link"] for domain in TRUSTED_DOMAINS)
        ][:5]
    except Exception as e:
        print("Error fetching deals:", e)
        return []

def post_deals():
    print("Posting new deals...")
    bot = Bot(token=BOT_TOKEN)
    deals = fetch_deals()

    if not deals:
        print("No valid deals found.")
        return

    for deal in deals:
        message = f"*{deal['title']}*\n{deal['description']}\n[Grab Deal]({deal['deal_link']})"
        bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)

scheduler = BlockingScheduler(timezone=pytz.utc)
scheduler.add_job(post_deals, "interval", hours=1)
post_deals()
scheduler.start()
