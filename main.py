import os
import requests
from telegram import Bot, ParseMode
from apscheduler.schedulers.blocking import BlockingScheduler

# Load from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

# Platforms you want
TRUSTED_PLATFORMS = ["amazon", "flipkart", "myntra", "ajio", "meesho"]

# Telegram bot init
bot = Bot(token=BOT_TOKEN)

def fetch_cuelinks_deals():
    url = "https://api.cuelinks.com/v2/deals.json?per_page=10&page=1"
    headers = {
        "Authorization": f"Token token={CUELINKS_API_KEY}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        deals = data.get("deals", [])
        print(f"Total deals fetched: {len(deals)}")
        return deals
    except Exception as e:
        print("Error fetching deals:", e)
        return []

def post_deals():
    print("Posting new deals...")
    deals = fetch_cuelinks_deals()
    valid = []
    for deal in deals:
        domain = deal.get("domain", "").lower()
        if any(site in domain for site in TRUSTED_PLATFORMS):
            valid.append(deal)

    if not valid:
        print("No valid deals found.")
        return

    for deal in valid[:5]:
        title = deal.get("title")
        link = deal.get("deal_url")
        message = f"*{title}*\n[Buy Now]({link})"
        try:
            bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
        except Exception as e:
            print("Failed to send:", e)

# Scheduler for hourly
scheduler = BlockingScheduler()
scheduler.add_job(post_deals, "interval", hours=1)

# First run now
post_deals()
scheduler.start()
