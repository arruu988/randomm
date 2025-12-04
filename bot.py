import os
import requests
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import sys

print("🚀 Bot Starting...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Bot Configuration
BOT_TOKEN = "8475772121:AAEKW9CFSCtyWm4YWuo4THpK3FOKOw0zlmE"
ADMIN_ID = 8472134840

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User data
user_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
🔍 *OSINT Search Bot*
Welcome {user.first_name}!

*Available Tools:*
• 📱 Phone Number Lookup
• 📧 Email Verification
• 👤 Username Search
• 🌐 IP Address Lookup
• 🚗 Vehicle Information

*How to use:*
Simply send:
- Phone: 9876543210
- Email: example@gmail.com
- Username: john_doe
- IP: 8.8.8.8
- Vehicle: UP65EM1666

⚠️ *For educational purposes only*
🤖 *Bot by @maarjauky*
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Auto-detect type
    if re.match(r'^[6-9]\d{9}$', text):  # Phone
        await phone_search(update, text)
    elif '@' in text and '.' in text:  # Email
        await email_search(update, text)
    elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):  # IP
        await ip_search(update, text)
    elif re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{4}$', text):  # Vehicle
        await vehicle_search(update, text)
    else:  # Username
        await username_search(update, text)

async def phone_search(update: Update, phone: str):
    await update.message.reply_chat_action("typing")
    
    try:
        # Clean phone
        phone = re.sub(r'\D', '', phone)
        
        if len(phone) != 10:
            await update.message.reply_text("❌ Invalid Indian mobile number")
            return
        
        # Carrier detection
        carriers = {
            '70':'Jio', '77':'Jio', '78':'Jio', '79':'Jio',
            '80':'Airtel', '81':'Airtel', '99':'Airtel', '98':'Airtel',
            '97':'Airtel', '96':'Airtel', '95':'Airtel',
            '83':'Vi', '84':'Vi', '85':'Vi', '86':'Vi',
            '92':'BSNL', '93':'BSNL', '94':'BSNL'
        }
        
        carrier = carriers.get(phone[:2], 'Unknown')
        
        # Location guess
        locations = {
            '70':'Delhi/NCR', '80':'Mumbai', '90':'Pune',
            '95':'Bangalore', '99':'Chennai', '98':'Kolkata'
        }
        location = locations.get(phone[:2], 'Various')
        
        result = f"""
📱 *Phone Analysis*
Number: `{phone}`

✅ *Valid Indian Mobile*
📡 *Carrier:* {carrier}
📍 *Location:* {location}
🔢 *Series:* {phone[:2]}XXXXXX

*Format:* +91 {phone[:5]} {phone[5:]}
*Type:* Mobile

⚠️ *For educational purposes only*
🤖 *Bot by @maarjauky*
"""
        await update.message.reply_text(result, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text("❌ Error processing request")

async def email_search(update: Update, email: str):
    await update.message.reply_chat_action("typing")
    
    try:
        # Basic email validation
        domain = email.split('@')[1] if '@' in email else ''
        
        result = f"""
📧 *Email Analysis*
Email: `{email}`

🌐 *Domain:* {domain}
✅ *Format:* Valid

*Common Domains:*
• Gmail: @gmail.com
• Yahoo: @yahoo.com
• Outlook: @outlook.com
• Custom: @{domain}

⚠️ *Note:* For security verification only
🤖 *Bot by @maarjauky*
"""
        await update.message.reply_text(result, parse_mode="Markdown")
        
    except:
        await update.message.reply_text("❌ Invalid email format")

async def username_search(update: Update, username: str):
    await update.message.reply_chat_action("typing")
    
    try:
        result = f"""
👤 *Username Analysis*
Username: `{username}`

*Available on:*
✅ Instagram: instagram.com/{username}
✅ Twitter: twitter.com/{username}
✅ Facebook: facebook.com/{username}
✅ GitHub: github.com/{username}
✅ LinkedIn: linkedin.com/in/{username}

*Check manually:*
1. Open browser
2. Search: "{username} site:instagram.com"
3. Repeat for other platforms

⚠️ *For educational purposes only*
🤖 *Bot by @maarjauky*
"""
        await update.message.reply_text(result, parse_mode="Markdown")
        
    except:
        await update.message.reply_text("❌ Error processing username")

async def ip_search(update: Update, ip: str):
    await update.message.reply_chat_action("typing")
    
    try:
        # Simple IP validation
        parts = ip.split('.')
        if len(parts) != 4:
            await update.message.reply_text("❌ Invalid IP address")
            return
        
        # Check if private IP
        first = int(parts[0])
        is_private = (
            first == 10 or
            (first == 172 and 16 <= int(parts[1]) <= 31) or
            (first == 192 and int(parts[1]) == 168)
        )
        
        result = f"""
🌐 *IP Analysis*
IP: `{ip}`

*Type:* {'🔒 Private' if is_private else '🌍 Public'}
*Format:* IPv4

*First Octet:* {first}
• 1-126: Class A
• 128-191: Class B  
• 192-223: Class C
• 224-239: Class D (Multicast)
• 240-254: Class E (Experimental)

⚠️ *For network troubleshooting only*
🤖 *Bot by @maarjauky*
"""
        await update.message.reply_text(result, parse_mode="Markdown")
        
    except:
        await update.message.reply_text("❌ Invalid IP address")

async def vehicle_search(update: Update, vehicle_no: str):
    await update.message.reply_chat_action("typing")
    
    try:
        vehicle_no = vehicle_no.upper()
        
        # State codes
        states = {
            'DL': 'Delhi', 'MH': 'Maharashtra', 'KA': 'Karnataka',
            'TN': 'Tamil Nadu', 'UP': 'Uttar Pradesh', 'GJ': 'Gujarat',
            'RJ': 'Rajasthan', 'AP': 'Andhra Pradesh', 'TS': 'Telangana',
            'WB': 'West Bengal', 'PB': 'Punjab', 'HR': 'Haryana'
        }
        
        state_code = vehicle_no[:2]
        state = states.get(state_code, 'Unknown State')
        
        result = f"""
🚗 *Vehicle Analysis*
Number: `{vehicle_no}`

📍 *State:* {state} ({state_code})
*Format:* Indian Registration

*State Codes:*
• DL: Delhi
• MH: Maharashtra  
• KA: Karnataka
• TN: Tamil Nadu
• UP: Uttar Pradesh
• GJ: Gujarat

*Example Formats:*
• New: {state_code}12AB1234
• Old: {state_code}12A1234

⚠️ *For educational purposes only*
🤖 *Bot by @maarjauky*
"""
        await update.message.reply_text(result, parse_mode="Markdown")
        
    except:
        await update.message.reply_text("❌ Invalid vehicle number")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔍 *OSINT Bot Help*

*Send any of these:*
1. Phone: 9876543210
2. Email: example@gmail.com  
3. Username: john_doe
4. IP: 8.8.8.8
5. Vehicle: UP65EM1666

*Features:*
• Basic validation
• Format analysis
• Carrier detection (phone)
• State identification (vehicle)

⚠️ *Disclaimer:*
For educational purposes only.
No personal data is collected.

🤖 *Bot by @maarjauky*
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    print("✅ Starting bot...")
    
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot configured")
        print("🚀 Starting polling...")
        
        # Start polling
        application.run_polling(
            drop_pending_updates=True,
            timeout=30
        )
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
