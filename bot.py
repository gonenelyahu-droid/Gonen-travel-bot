
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Bot token (replace with your actual bot token)
BOT_TOKEN = 8746267862:AAEhYMqTqt008Jl3tztgXcX9xFBRn3Yd_VM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    await update.message.reply_text("שלום! אני סוכן נסיעות חכם של Gonen Travel. אנא שלח לי פרטי מבצע נסיעות (יעד, תאריכים, מחיר, מה כלול) ואני אייצר עבורך פוסט לאינסטגרם.")

async def generate_instagram_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates an Instagram post based on user input."""
    user_input = update.message.text
    await update.message.reply_text(f"קיבלתי את המידע: {user_input}. עכשיו אני מייצר עבורך פוסט...")

    try:
        # Generate text with OpenAI GPT
        text_prompt = f"צור פוסט מקצועי ומושך לאינסטגרם בעברית עבור סוכנות נסיעות 'Gonen Travel' על מבצע נסיעות. המידע שסופק: {user_input}. הפוסט צריך לכלול כותרת, תיאור עם קריאה לפעולה, והאשטאגים רלוונטיים. \n\nדוגמה:\nכותרת: חופשה חלומית ביוון מחכה לכם!\nתיאור: בואו לחוות את הקסם של יוון עם חבילת נופש מפנקת הכוללת טיסות, מלונות 5 כוכבים וארוחות גורמה. אל תחמיצו את ההזדמנות! לפרטים והזמנות לחצו כאן.\nהאשטאגים: #יוון #חופשה #טיולים #GonenTravel #נופש"
        
        text_response = openai.chat.completions.create(
            model="gpt-4.1-mini", # Using the available model
            messages=[
                {"role": "system", "content": "אתה עוזר לסוכנות נסיעות ליצור תוכן שיווקי לאינסטגרם."},
                {"role": "user", "content": text_prompt}
            ],
            max_tokens=500
        )
        instagram_text = text_response.choices[0].message.content.strip()

        # Extract destination for image generation
        # A more robust parsing would be needed for production, but for now, a simple split
        destination = "".join(user_input.split(',')[0].split(' ')[1:]) if len(user_input.split(',')) > 0 else "travel destination"

        # Generate image with DALL-E
        image_prompt = f"תמונה מרהיבה של {destination} המתאימה לפוסט אינסטגרם של סוכנות נסיעות Gonen Travel."
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url

        await update.message.reply_text(f"הנה הפוסט שלך לאינסטגרם:\n\n{instagram_text}")
        await update.message.reply_photo(image_url)
        await update.message.reply_text("כפתור 'אשר ופרסם' יתווסף בעתיד.")

    except Exception as e:
        logging.error(f"Error generating Instagram post: {e}")
        await update.message.reply_text("אירעה שגיאה בעת יצירת הפוסט. אנא נסה שוב מאוחר יותר.")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_instagram_post))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
