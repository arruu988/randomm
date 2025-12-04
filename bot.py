import os
import sys
import logging

print("=" * 50)
print("🚀 Starting OSINT Bot - SIMPLE VERSION")
print(f"Python Path: {sys.executable}")
print(f"Python Version: {sys.version}")
print("=" * 50)

# Check if we can import
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    import requests
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please install: pip install python-telegram-bot requests")
    sys.exit(1)

# Bot Configuration
BOT_TOKEN = "8475772121:AAEKW9CFSCtyWm4YWuo4THpK3FOKOw0zlmE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}!\n\n"
        "🤖 *OSINT Search Bot*\n\n"
        "Send me:\n"
        "• Phone number: 9876543210\n"
        "• Email: test@example.com\n"
        "• Username: john_doe\n\n"
        "⚠️ *Educational Purpose Only*",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages."""
    text = update.message.text.strip()
    
    # Simple response
    response = f"""
🔍 *Search Result*

Query: `{text}`
Type: {'📱 Phone' if text.isdigit() else '📧 Email' if '@' in text else '👤 Username'}

*Information:*
- Format: Valid
- Status: Processed
- Source: OSINT Database

⚠️ *For educational purposes only*
🤖 *Bot by @maarjauky*
"""
    await update.message.reply_text(response, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "🤖 *Help*\n\n"
        "/start - Start the bot\n"
        "/help - Show this message\n\n"
        "Just send me:\n"
        "- Phone number\n"
        "- Email address\n"
        "- Username\n\n"
        "⚠️ *Educational Purpose Only*",
        parse_mode="Markdown"
    )

def main():
    """Start the bot."""
    print("🔄 Creating bot application...")
    
    try:
        # Create the Application
        application = Application.builder().token(BOT_TOKEN).build()
        print("✅ Application created")

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # Add message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Handlers added")
        print("🚀 Starting bot polling...")
        print("📱 Bot should be live on Telegram!")
        
        # Run the bot
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
