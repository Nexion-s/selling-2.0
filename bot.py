import subprocess
import logging
import os
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from nexionn import TOKEN  # Import the TOKEN variable

ADMIN_ID = 1847934841

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Path to your binary
BINARY_PATH = "./om"

EXPIRY_DATE = datetime(2025, 11, 28)  # Script expiry date

# Global variables
process = None
target_ip = None
target_port = None

APPROVED_USERS_FILE = "approved_users.txt"  # File to store approved users and their expiry times

# Check if the script has expired
def check_expiry():
    current_date = datetime.now()
    return current_date > EXPIRY_DATE

# Load replies from an external JSON file
def load_replies():
    try:
        with open("replies.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("Replies configuration file not found!")
        return {}

# Load replies from external file at startup
REPLIES = load_replies()

# Load approved users with expiry times from file
def load_approved_users_with_expiry():
    if os.path.exists(APPROVED_USERS_FILE):
        with open(APPROVED_USERS_FILE, "r") as file:
            users_with_expiry = {}
            for line in file:
                user_id, expiry_time = line.strip().split(",")
                users_with_expiry[int(user_id)] = datetime.fromisoformat(expiry_time)
            return users_with_expiry
    return {}

# Save approved user with expiry time to file
def save_approved_user_with_expiry(user_id, expiry_time):
    with open(APPROVED_USERS_FILE, "a") as file:
        file.write(f"{user_id},{expiry_time.isoformat()}\n")

# Remove expired or disapproved users
def remove_approved_user(user_id):
    if user_id in approved_users_with_expiry:
        del approved_users_with_expiry[user_id]
        # Rewrite the file without the user
        with open(APPROVED_USERS_FILE, "w") as file:
            for uid, expiry_time in approved_users_with_expiry.items():
                file.write(f"{uid},{expiry_time.isoformat()}\n")

# Global dictionary to store approved users with expiry times
approved_users_with_expiry = load_approved_users_with_expiry()

# Check if the user is admin
def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID

# Check if the user is approved
def is_approved(user_id) -> bool:
    if user_id in approved_users_with_expiry:
        expiry_time = approved_users_with_expiry[user_id]
        if datetime.now() < expiry_time:
            return True
        else:
            # Remove expired user
            remove_approved_user(user_id)
            return False
    return user_id == ADMIN_ID

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if check_expiry():
        keyboard1 = [[InlineKeyboardButton("SEND MESSAGE", url="https://t.me/NEXION_OWNER")]]
        reply_markup1 = InlineKeyboardMarkup(keyboard1)
        await update.message.reply_text(
            "🚀This script has expired. DM for New Script. Made by t.me/NEXION_OWNER",
            reply_markup=reply_markup1
        )
        return

    if is_approved(user_id):
        keyboard = [[InlineKeyboardButton("🚀Attack🚀", callback_data='attack')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(REPLIES.get("start_approved", "You are approved!"), reply_markup=reply_markup)
    else:
        await update.message.reply_text(REPLIES.get("not_approved", "You are not approved."))

# Command for admin to approve users with a validity period
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("This action is for admin use only.")
        return

    try:
        user_id_to_approve = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 0
        hours = int(context.args[2]) if len(context.args) > 2 else 0
        minutes = int(context.args[3]) if len(context.args) > 3 else 0

        duration = timedelta(days=days, hours=hours, minutes=minutes)
        expiry_time = datetime.now() + duration

        if user_id_to_approve not in approved_users_with_expiry:
            approved_users_with_expiry[user_id_to_approve] = expiry_time
            save_approved_user_with_expiry(user_id_to_approve, expiry_time)
            await update.message.reply_text(
                f"User {user_id_to_approve} has been approved for {days} days, {hours} hours, and {minutes} minutes."
            )
        else:
            await update.message.reply_text(f"User {user_id_to_approve} is already approved.")
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Please provide a valid user ID and duration in the format: /approve <user_id> <days> <hours> <minutes>"
        )

# Command for admin to disapprove users
async def disapprove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("This action is for admin use only.")
        return

    try:
        user_id_to_disapprove = int(context.args[0])
        if user_id_to_disapprove in approved_users_with_expiry:
            remove_approved_user(user_id_to_disapprove)
            await update.message.reply_text(f"User {user_id_to_disapprove} has been disapproved.")
        else:
            await update.message.reply_text(f"User {user_id_to_disapprove} is not in the approved list.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid user ID to disapprove.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("disapprove", disapprove_user))

    application.run_polling()

if __name__ == "__main__":
    main()
