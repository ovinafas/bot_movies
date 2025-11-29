import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8245533941:AAGZR2MPSn38ehCBlvO6VUmWDizmIbIKYAk"
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = f"https://uptv-bot-1.onrender.com/{TOKEN}"

URL = "https://uptvs.com"

# ------------------------------
# تابع اسکرپ فیلم‌ها
# ------------------------------
def scrape_uptv():
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("a.top-choices-item")

    movies = []
    for item in items[:20]:
        title = item.get("title", "عنوان موجود نیست")
        link = item.get("href")
        image = item.find("img").get("data-src", None)

        if link and not link.startswith("http"):
            link = "https://uptvs.com" + link

        movies.append({"title": title, "link": link, "image": image})
    return movies

# ------------------------------
# Handlers
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! ربات شما آماده است 🚀\n"
        "برای دریافت فیلم‌ها دستور زیر را بزنید:\n/movies"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستورات موجود:\n/start\n/help\n/movies")

async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت فیلم‌ها ...")
    try:
        data = scrape_uptv()
        if not data:
            await update.message.reply_text("❗هیچ فیلمی دریافت نشد.")
            return

        for movie in data:
            text = f"🎬 *{movie['title']}*\n🔗 لینک: {movie['link']}"
            if movie["image"]:
                await update.message.reply_photo(photo=movie["image"], caption=text, parse_mode="Markdown")
            else:
                await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در اسکرپ سایت:\n{e}")

# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("movies", movies))

    # Start webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
