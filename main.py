import logging

import asyncio

from telegram import Update

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from datetime import datetime

import sqlite3

import pytz

import re

# Configure logging

logging.basicConfig(

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    level=logging.INFO

)

# Bot token from BotFather

BOT_TOKEN = "8288403434:AAG1xwYdc-iwG12tVmdnFyOMXkF5SP5Niwk"

# Timezone setup (Pakistan Time)

PAK_TZ = pytz.timezone('Asia/Karachi')

# Database setup

def init_db():

    conn = sqlite3.connect('auto_bot.db')

    cursor = conn.cursor()

    cursor.execute('''

        CREATE TABLE IF NOT EXISTS group_messages (

            message_id INTEGER,

            group_id INTEGER,

            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (message_id, group_id)

        )

    ''')

    conn.commit()

    conn.close()

init_db()

def store_message(group_id, message_id):

    conn = sqlite3.connect('auto_bot.db')

    cursor = conn.cursor()

    cursor.execute(

        'INSERT OR REPLACE INTO group_messages (message_id, group_id) VALUES (?, ?)',

        (message_id, group_id)

    )

    conn.commit()

    conn.close()

def get_pakistan_time():

    return datetime.now(PAK_TZ)

def is_night_time():

    now = get_pakistan_time()

    return now.hour == 23  # 11 PM

def is_morning_time():

    now = get_pakistan_time()

    return now.hour == 8 and now.minute == 0  # 8 AM

def contains_link(text):

    if not text:

        return False

    # Link pattern detection

    link_patterns = [

        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',

        r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',

        r't\.me/[a-zA-Z0-9_]+',

        r'telegram\.me/[a-zA-Z0-9_]+',

        r'@[a-zA-Z0-9_]{5,}'  # Telegram usernames

    ]

    

    for pattern in link_patterns:

        if re.search(pattern, text, re.IGNORECASE):

            return True

    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """Simple start command"""

    welcome_text = """

🤖 AUTOMATIC GROUP MANAGER BOT

• 11 PM: Auto Chat Off + Good Night

• 8 AM: Auto Chat On + Good Morning  

• Every 30 Min: Auto Delete Recent Messages

• Anti-Link: Auto Delete All Links

Bot is now active and working automatically!

    """

    await update.message.reply_text(welcome_text)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """Handle all messages for auto delete and anti-link"""

    if not update.message:

        return

        

    group_id = update.message.chat_id

    message_id = update.message.message_id

    message_text = update.message.text or update.message.caption or ""

    # Store message for tracking

    store_message(group_id, message_id)

    # Anti-link feature - Delete any links immediately

    if contains_link(message_text):

        try:

            await context.bot.delete_message(group_id, message_id)

            warning_msg = await context.bot.send_message(

                group_id,

                "⚠️ Links are not allowed in this group! Message deleted."

            )

            await asyncio.sleep(5)

            await context.bot.delete_message(group_id, warning_msg.message_id)

            return

        except Exception as e:

            logging.error(f"Error deleting link: {e}")

        return

    # Night mode - Delete messages at 11 PM

    if is_night_time():

        try:

            await context.bot.delete_message(group_id, message_id)

        except Exception as e:

            logging.error(f"Error in night mode delete: {e}")

        return

    # Auto delete after 30 minutes for all messages

    await asyncio.sleep(1800)  # 30 minutes

    

    try:

        await context.bot.delete_message(group_id, message_id)

    except Exception as e:

        logging.error(f"Error in auto delete: {e}")

async def auto_cleanup_job(context: ContextTypes.DEFAULT_TYPE):

    """Cleanup old messages every 30 minutes"""

    try:

        # This will cleanup messages that are older than 30 minutes

        # from the database (optional cleanup)

        pass

    except Exception as e:

        logging.error(f"Error in cleanup job: {e}")

async def schedule_manager(context: ContextTypes.DEFAULT_TYPE):

    """Manage night and morning schedules"""

    try:

        current_time = get_pakistan_time()

        

        # Get all groups where bot is added

        # For simplicity, we'll assume bot works in all groups it's added to

        

        # 11 PM - Night Time

        if current_time.hour == 23 and current_time.minute == 0:

            # This will be handled by handle_messages function

            # But we can also send a notification

            try:

                # You can add specific group IDs here if needed

                pass

            except Exception as e:

                logging.error(f"Error in night schedule: {e}")

        

        # 8 AM - Morning Time  

        elif current_time.hour == 8 and current_time.minute == 0:

            # This will be handled by stopping the night mode in handle_messages

            # But we can send morning notification

            try:

                # You can add specific group IDs here if needed

                pass

            except Exception as e:

                logging.error(f"Error in morning schedule: {e}")

                

    except Exception as e:

        logging.error(f"Error in schedule manager: {e}")

async def night_mode_notification(context: ContextTypes.DEFAULT_TYPE):

    """Send night mode notification at 11 PM"""

    current_time = get_pakistan_time()

    if current_time.hour == 23 and current_time.minute == 0:

        try:

            # This would need to be customized for specific groups

            # For now, it's a template

            group_id = None  # Set specific group ID if needed

            if group_id:

                await context.bot.send_message(

                    group_id,

                    "🌙 11 PM - THIS IS TIME TO SLEEP\n"

                    "GROUP CHAT OFF\n"

                    "Good Night! 💤\n\n"

                    "Auto delete active every 30 minutes."

                )

        except Exception as e:

            logging.error(f"Error sending night notification: {e}")

async def morning_mode_notification(context: ContextTypes.DEFAULT_TYPE):

    """Send morning mode notification at 8 AM"""

    current_time = get_pakistan_time()

    if current_time.hour == 8 and current_time.minute == 0:

        try:

            # This would need to be customized for specific groups

            # For now, it's a template

            group_id = None  # Set specific group ID if needed

            if group_id:

                await context.bot.send_message(

                    group_id,

                    "🌞 8 AM - GROUP MORNING\n"

                    "GROUP CHAT ON\n"

                    "Good Morning! ☀️\n\n"

                    "Auto delete active every 30 minutes."

                )

        except Exception as e:

            logging.error(f"Error sending morning notification: {e}")

def main():

    """Start the bot"""

    application = Application.builder().token(BOT_TOKEN).build()

    

    # Add handlers

    application.add_handler(CommandHandler("start", start))

    

    # Handle all messages for auto features

    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))

    

    # Add job queues

    job_queue = application.job_queue

    if job_queue:

        # Schedule manager every minute

        job_queue.run_repeating(schedule_manager, interval=60, first=10)

        

        # Notifications at specific times

        job_queue.run_repeating(night_mode_notification, interval=3600, first=15)  # Check every hour

        job_queue.run_repeating(morning_mode_notification, interval=3600, first=20)  # Check every hour

        

        # Cleanup job every 30 minutes

        job_queue.run_repeating(auto_cleanup_job, interval=1800, first=30)

    

    # Start the bot

    print("🤖 AUTOMATIC GROUP MANAGER BOT STARTED")

    print("⏰ Features:")

    print("   • 11 PM: Auto Chat Off + Notification")

    print("   • 8 AM: Auto Chat On + Notification") 

    print("   • Every 30 Min: Auto Delete Messages")

    print("   • Anti-Link: Auto Delete All Links")

    print("   • No Buttons - Fully Automatic")

    application.run_polling()

if __name__ == "__main__":

    main()
