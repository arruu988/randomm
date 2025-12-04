import os
import requests
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from flask import Flask
from threading import Thread
from datetime import datetime

# ================= CONFIGURATION =================
BOT_TOKEN = "8475772121:AAEKW9CFSCtyWm4YWuo4THpK3FOKOw0zlmE"
ADMIN_ID = 8472134840  # Tumhara user ID

# OSINT API Endpoints
BASE_API = "https://osintbyxencryptic.netlify.app"

APIS = {
    "phone": f"{BASE_API}/phone",
    "email": f"{BASE_API}/email", 
    "username": f"{BASE_API}/username",
    "ip": f"{BASE_API}/ip",
    "vehicle": f"{BASE_API}/vehicle"
}

# ================= FLASK SERVER (FOR RENDER) =================
app = Flask('')

@app.route('/')
def home():
    return "🤖 OSINT Bot is Running! | @maarjauky"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

# ================= LOGGING =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= USER MANAGEMENT =================
user_data = {}
FREE_LIMIT = 5
PREMIUM_LIMIT = 100

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'searches_today': 0,
            'total_searches': 0,
            'is_premium': False,
            'premium_expiry': None,
            'last_reset': datetime.now().date()
        }
    return user_data[user_id]

def reset_daily_counts():
    today = datetime.now().date()
    for user_id, data in user_data.items():
        if data['last_reset'] != today:
            data['searches_today'] = 0
            data['last_reset'] = today

def can_search(user_id):
    user = get_user(user_id)
    reset_daily_counts()
    
    limit = PREMIUM_LIMIT if user['is_premium'] else FREE_LIMIT
    return user['searches_today'] < limit

def increment_search(user_id):
    user = get_user(user_id)
    user['searches_today'] += 1
    user['total_searches'] += 1

# ================= BOT HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = get_user(user.id)
    
    keyboard = [
        [InlineKeyboardButton("📱 Phone Lookup", callback_data="phone")],
        [InlineKeyboardButton("📧 Email Lookup", callback_data="email")],
        [InlineKeyboardButton("👤 Username Search", callback_data="username")],
        [InlineKeyboardButton("🌐 IP Lookup", callback_data="ip")],
        [InlineKeyboardButton("🚗 Vehicle Lookup", callback_data="vehicle")],
        [InlineKeyboardButton("💰 Buy Premium", callback_data="premium"),
         InlineKeyboardButton("📊 My Stats", callback_data="stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
🔍 *OSINT Search Bot*
Welcome {user.first_name}!

*Available Searches Today:* {user_info['searches_today']}/{PREMIUM_LIMIT if user_info['is_premium'] else FREE_LIMIT}
*Premium Status:* {'✅ ACTIVE' if user_info['is_premium'] else '❌ INACTIVE'}

*Select a search type:*
• 📱 Phone Number Lookup
• 📧 Email Verification
• 👤 Username Search
• 🌐 IP Address Lookup
• 🚗 Vehicle Information

⚠️ *For educational purposes only*
🤖 *Bot by @maarjauky*
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "phone":
        await query.edit_message_text(
            "📱 *Phone Number Lookup*\n\nSend phone number (10 digits)\nExample: `9876543210`\n\nOr send with country code: `+919876543210`",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "phone"
        
    elif data == "email":
        await query.edit_message_text(
            "📧 *Email Lookup*\n\nSend email address\nExample: `example@gmail.com`",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "email"
        
    elif data == "username":
        await query.edit_message_text(
            "👤 *Username Search*\n\nSend username\nExample: `john_doe`",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "username"
        
    elif data == "ip":
        await query.edit_message_text(
            "🌐 *IP Address Lookup*\n\nSend IP address\nExample: `8.8.8.8`",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "ip"
        
    elif data == "vehicle":
        await query.edit_message_text(
            "🚗 *Vehicle Information*\n\nSend vehicle number\nExample: `UP65EM1666`\n\nFormat: StateCode+Number",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "vehicle"
        
    elif data == "premium":
        keyboard = [
            [InlineKeyboardButton("1 Month - ₹150", callback_data="premium_1")],
            [InlineKeyboardButton("6 Months - ₹1200", callback_data="premium_6")],
            [InlineKeyboardButton("1 Year - ₹1350", callback_data="premium_12")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        premium_text = """
💰 *Premium Plans*

*Free Plan:*
• 5 searches/day
• Basic information

*Premium Benefits:*
• 100 searches/day
• Priority processing
• Detailed reports
• No ads

*Select Plan:*
1 Month - ₹150
6 Months - ₹1200 (Save ₹300)
1 Year - ₹1350 (Save ₹450)

*Payment:* UPI @maarjauky
"""
        await query.edit_message_text(premium_text, parse_mode="Markdown", reply_markup=markup)
        
    elif data == "stats":
        user_info = get_user(user_id)
        stats_text = f"""
📊 *Your Statistics*

*User ID:* `{user_id}`
*Searches Today:* {user_info['searches_today']}/{PREMIUM_LIMIT if user_info['is_premium'] else FREE_LIMIT}
*Total Searches:* {user_info['total_searches']}
*Premium Status:* {'✅ ACTIVE' if user_info['is_premium'] else '❌ INACTIVE'}

*Bot Info:*
• Version: 2.0
• Status: ✅ Operational
• API: osintbyxencryptic.netlify.app
• Developer: @maarjauky
"""
        await query.edit_message_text(stats_text, parse_mode="Markdown")
        
    elif data == "back":
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user can search
    if not can_search(user_id):
        await update.message.reply_text(
            "❌ *Daily limit reached!*\n\nUpgrade to premium for more searches.\n\nClick /start and select '💰 Buy Premium'",
            parse_mode="Markdown"
        )
        return
    
    text = update.message.text.strip()
    mode = context.user_data.get("mode", "auto")
    
    await update.message.reply_chat_action("typing")
    
    try:
        if mode == "phone" or (mode == "auto" and re.match(r'^[6-9]\d{9}$', text) or re.match(r'^\+?[0-9]{10,13}$', text)):
            await phone_search(update, text)
            increment_search(user_id)
            
        elif mode == "email" or (mode == "auto" and '@' in text and '.' in text):
            await email_search(update, text)
            increment_search(user_id)
            
        elif mode == "username" or (mode == "auto" and re.match(r'^[a-zA-Z0-9_.]{3,}$', text) and '@' not in text):
            await username_search(update, text)
            increment_search(user_id)
            
        elif mode == "ip" or (mode == "auto" and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text)):
            await ip_search(update, text)
            increment_search(user_id)
            
        elif mode == "vehicle" or (mode == "auto" and re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{4}$', text)):
            await vehicle_search(update, text)
            increment_search(user_id)
            
        else:
            await update.message.reply_text(
                "❌ *Invalid input!*\n\nPlease select a tool from menu or send:\n"
                "• Phone: 9876543210\n"
                "• Email: example@gmail.com\n"
                "• Username: john_doe\n"
                "• IP: 8.8.8.8\n"
                "• Vehicle: UP65EM1666\n\n"
                "Click /start for menu",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text("❌ Service temporarily unavailable. Please try again later.")

async def phone_search(update: Update, phone: str):
    """Search phone number information"""
    # Clean phone number
    phone = re.sub(r'\D', '', phone)
    
    if len(phone) < 10:
        await update.message.reply_text("❌ Invalid phone number")
        return
    
    try:
        response = requests.get(f"{APIS['phone']}/{phone}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Format response
            result = f"""
📱 *Phone Lookup Results*
Number: `{phone}`

"""
            
            if data.get('valid'):
                result += "✅ *Valid Number*\n\n"
            
            if data.get('country'):
                result += f"📍 *Country:* {data['country']}\n"
            
            if data.get('location'):
                result += f"🏙️ *Location:* {data['location']}\n"
            
            if data.get('carrier'):
                result += f"📡 *Carrier:* {data['carrier']}\n"
            
            if data.get('line_type'):
                result += f"📞 *Line Type:* {data['line_type']}\n"
            
            if data.get('timezone'):
                result += f"⏰ *Timezone:* {data['timezone']}\n"
            
            result += "\n" + "─" * 40 + "\n"
            result += "\n⚠️ *For educational purposes only*"
            result += "\n🤖 *Bot by @maarjauky*"
            
            await update.message.reply_text(result, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No information found for this number")
            
    except Exception as e:
        await update.message.reply_text("❌ API service temporarily unavailable")

async def email_search(update: Update, email: str):
    """Search email information"""
    try:
        response = requests.get(f"{APIS['email']}/{email}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            result = f"""
📧 *Email Lookup Results*
Email: `{email}`

"""
            
            if data.get('valid'):
                result += "✅ *Valid Email*\n\n"
            else:
                result += "❌ *Invalid Email*\n\n"
            
            if data.get('domain'):
                result += f"🌐 *Domain:* {data['domain']}\n"
            
            if data.get('disposable'):
                result += "🚫 *Disposable Email:* Yes\n"
            
            if data.get('free'):
                result += "🎫 *Free Service:* Yes\n"
            
            if data.get('deliverable'):
                result += "📨 *Deliverable:* Yes\n"
            
            if data.get('risk_score'):
                result += f"⚠️ *Risk Score:* {data['risk_score']}/10\n"
            
            result += "\n" + "─" * 40 + "\n"
            result += "\n⚠️ *For educational purposes only*"
            
            await update.message.reply_text(result, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No information found for this email")
            
    except:
        await update.message.reply_text("❌ API service temporarily unavailable")

async def username_search(update: Update, username: str):
    """Search username across platforms"""
    try:
        response = requests.get(f"{APIS['username']}/{username}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            result = f"""
👤 *Username Search Results*
Username: `{username}`

"""
            
            platforms = data.get('platforms', {})
            
            if platforms:
                result += "📱 *Found on Platforms:*\n"
                
                found = 0
                for platform, info in platforms.items():
                    if info.get('found'):
                        found += 1
                        result += f"✅ *{platform.title()}*"
                        if info.get('url'):
                            result += f": [Link]({info['url']})"
                        result += "\n"
                
                result += f"\n📊 *Total Found:* {found} platforms\n"
            else:
                result += "❌ *Not found on any platforms*\n"
            
            result += "\n" + "─" * 40 + "\n"
            result += "\n⚠️ *For educational purposes only*"
            
            await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text("❌ Username not found on tracked platforms")
            
    except:
        await update.message.reply_text("❌ API service temporarily unavailable")

async def ip_search(update: Update, ip: str):
    """Search IP address information"""
    try:
        response = requests.get(f"{APIS['ip']}/{ip}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            result = f"""
🌐 *IP Lookup Results*
IP: `{ip}`

"""
            
            if data.get('country'):
                result += f"📍 *Country:* {data['country']}\n"
            
            if data.get('city'):
                result += f"🏙️ *City:* {data['city']}\n"
            
            if data.get('region'):
                result += f"🗺️ *Region:* {data['region']}\n"
            
            if data.get('isp'):
                result += f"🏢 *ISP:* {data['isp']}\n"
            
            if data.get('org'):
                result += f"🏛️ *Organization:* {data['org']}\n"
            
            if data.get('timezone'):
                result += f"⏰ *Timezone:* {data['timezone']}\n"
            
            if data.get('proxy') or data.get('vpn'):
                result += "🛡️ *Proxy/VPN:* Detected\n"
            
            result += "\n" + "─" * 40 + "\n"
            result += "\n⚠️ *For educational purposes only*"
            
            await update.message.reply_text(result, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No information found for this IP")
            
    except:
        await update.message.reply_text("❌ API service temporarily unavailable")

async def vehicle_search(update: Update, vehicle_no: str):
    """Search vehicle information"""
    try:
        response = requests.get(f"{APIS['vehicle']}/{vehicle_no}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            result = f"""
🚗 *Vehicle Lookup Results*
Vehicle: `{vehicle_no}`

"""
            
            if data.get('registration_number'):
                result += f"🔢 *Reg Number:* {data['registration_number']}\n"
            
            if data.get('owner_name'):
                name = data['owner_name']
                if len(name) > 4:
                    masked = name[0] + "*" * (len(name)-2) + name[-1]
                    result += f"👤 *Owner:* {masked}\n"
            
            if data.get('rto'):
                result += f"🏛️ *RTO:* {data['rto']}\n"
            
            if data.get('maker'):
                result += f"🏭 *Maker:* {data['maker']}\n"
            
            if data.get('model'):
                result += f"🚘 *Model:* {data['model']}\n"
            
            if data.get('fuel_type'):
                result += f"⛽ *Fuel Type:* {data['fuel_type']}\n"
            
            if data.get('vehicle_color'):
                result += f"🎨 *Color:* {data['vehicle_color']}\n"
            
            if data.get('insurance_company'):
                result += f"🏢 *Insurance:* {data['insurance_company']}\n"
            
            result += "\n" + "─" * 40 + "\n"
            result += "\n⚠️ *For educational purposes only*"
            result += "\n🤖 *Bot by @maarjauky*"
            
            await update.message.reply_text(result, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Vehicle not found in database")
            
    except:
        await update.message.reply_text("❌ API service temporarily unavailable")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔍 *OSINT Bot - Help*

*Commands:*
/start - Start bot with menu
/help - Show this help
/stats - Your search statistics

*Search Types:*
1. *Phone Lookup* - Carrier, location, validity
2. *Email Lookup* - Verification, breaches check
3. *Username Search* - Social media presence
4. *IP Lookup* - Geolocation, ISP, threats
5. *Vehicle Lookup* - RTO details, owner info

*Usage Limits:*
• Free: 5 searches/day
• Premium: 100 searches/day

*Premium Plans:*
1 Month - ₹150
6 Months - ₹1200
1 Year - ₹1350

*Payment:* UPI @maarjauky

⚠️ *Educational use only*
🤖 *Developer:* @maarjauky
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user(user_id)
    
    stats_text = f"""
📊 *Your Statistics*

*User ID:* `{user_id}`
*Searches Today:* {user_info['searches_today']}/{PREMIUM_LIMIT if user_info['is_premium'] else FREE_LIMIT}
*Total Searches:* {user_info['total_searches']}
*Premium Status:* {'✅ ACTIVE' if user_info['is_premium'] else '❌ INACTIVE'}

*Bot Status:* ✅ Operational
*API Source:* osintbyxencryptic.netlify.app
*Developer:* @maarjauky
"""
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin commands"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Admin access required")
        return
    
    if context.args and context.args[0] == "stats":
        # Show all users stats
        total_users = len(user_data)
        total_searches = sum(user['total_searches'] for user in user_data.values())
        
        admin_stats = f"""
👑 *Admin Statistics*

*Total Users:* {total_users}
*Total Searches:* {total_searches}
*Active Today:* {sum(1 for user in user_data.values() if user['searches_today'] > 0)}

*Recent Users (last 10):*
"""
        
        # Show recent users
        recent_users = list(user_data.items())[-10:]
        for uid, data in recent_users:
            admin_stats += f"\n• User {uid}: {data['searches_today']} searches today"
        
        await update.message.reply_text(admin_stats, parse_mode="Markdown")
    
    elif context.args and context.args[0] == "premium":
        if len(context.args) >= 2:
            target_id = int(context.args[1])
            if target_id in user_data:
                user_data[target_id]['is_premium'] = True
                await update.message.reply_text(f"✅ Premium activated for user {target_id}")
            else:
                await update.message.reply_text("❌ User not found")
        else:
            await update.message.reply_text("Usage: /admin premium <user_id>")

# ================= MAIN FUNCTION =================
def main():
    print("=" * 50)
    print("🚀 Starting OSINT Search Bot")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"🔗 API Base: {BASE_API}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("⚡ By: @maarjauky")
    print("=" * 50)
    
    try:
        # Start Flask server for Render
        keep_alive()
        print("🌐 Flask server started on port 8080")
        
        # Create bot application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot configured successfully!")
        print("⏳ Starting polling...")
        print("📲 Bot should be live now!")
        
        # Start polling
        application.run_polling(
            drop_pending_updates=True,
            timeout=30,
            pool_timeout=30
        )
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check bot token")
        print("2. Check internet connection")
        print("3. Check if port 8080 is available")

if __name__ == "__main__":
    main()