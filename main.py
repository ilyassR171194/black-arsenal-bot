import logging
import random
import json
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

# === الإعدادات ===
TOKEN = os.environ['TOKEN']
CHANNEL_ID = -1003947955231
CHANNEL_USERNAME = "@BlackArsenalStore"
ADMIN_ID = 6795018161

# === قاعدة البيانات ===
DB_FILE = "database.json"
PRODUCTS_FILE = "products.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "apps_free": [
            {"name": "تطبيق تيرمكس", "price": 0.0, "stock": 9909, "desc": "تطبيق تيرمكس اخر اصدار", "content": "termux-app_v0.118.3+github-debug_arm64-v8a.apk"},
            {"name": "تطبيق اف درويد", "price": 0.0, "stock": 9827, "desc": "تطبيق اف درويد احترافي", "content": "afdroid.apk"}
        ],
        "tools_free": [
            {"name": "OSINT", "price": 0.0, "stock": 9952, "desc": "أداة جمع معلومات", "content": "OSINT Tool"},
            {"name": "جمع معلومات رقم هاتف", "price": 0.0, "stock": 9845, "desc": "هذه الاداة قوية جدا لجمع معلومات عن ارقام الهواتف", "content": "pkg update && pkg upgrade -y\npkg install git golang -y\ngit clone https://github.com/sundowndev/phoneinfoga.git\ncd phoneinfoga\ngo build -o phoneinfoga.\nmv phoneinfoga $PREFIX/bin/\nphoneinfoga version"},
            {"name": "جمع معلومات ايميل", "price": 0.0, "stock": 9935, "desc": "أداة جمع معلومات الايميل", "content": "Email OSINT Tool"},
            {"name": "اختراق انستا", "price": 0.0, "stock": 9851, "desc": "أداة اختراق انستا", "content": "Insta Hack Tool"},
            {"name": "اختراق كاميرا", "price": 0.0, "stock": 9921, "desc": "أداة اختراق كاميرا", "content": "Camera Hack Tool"},
            {"name": "اختراق هواتف", "price": 0.0, "stock": 9852, "desc": "أداة اختراق هواتف", "content": "Phone Hack Tool"},
            {"name": "تيرمكس فيد", "price": 0.0, "stock": 9946, "desc": "سكربتات تيرمكس", "content": "Termux Feed Scripts"}
        ]
    }

def save_products(data):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user(user_id):
    db = load_db()
    user_id = str(user_id)
    if user_id not in db:
        db[user_id] = {
            "balance": 0.03,
            "last_daily": "2000-01-01",
            "verified": False,
            "referrals": 0,
            "captcha_solved": False
        }
        save_db(db)
    return db[user_id]

def update_user(user_id, data):
    db = load_db()
    db[str(user_id)].update(data)
    save_db(db)

# === الواجهة الرئيسية ===
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("المنتجات 🛍️"), KeyboardButton("العروض 🎁")],
        [KeyboardButton("التطبيقات 📱"), KeyboardButton("تحويل عملة 💱")],
        [KeyboardButton("شراء رصيد 💰"), KeyboardButton("كود هدية 🎫")],
        [KeyboardButton("معلوماتي 📋")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# === التحقق من الاشتراك ===
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except: pass
    return False

async def send_subscription_msg(message_obj):
    keyboard = [[InlineKeyboardButton("🔔 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check_sub")]]
    await message_obj.reply_text(
        f"❌ يجب عليك الاشتراك في القناة أولاً:\n\n👉 {CHANNEL_USERNAME}\n\nمن بعد ما تشترك ضغط على 'تحققت من الاشتراك'",
        reply_markup=InlineKeyboardMarkup(keyboard))

# === الكابتشا بحال السوري ===
async def send_captcha(message_obj):
    keyboard = [
        [InlineKeyboardButton("10", callback_data="captcha_10"), InlineKeyboardButton("9", callback_data="captcha_9")]
    ]
    await message_obj.reply_text(
        "تحقق سريع قبل الدخول: 🔐\n\nكم ناتج: 8 + 2 =? ❓",
        reply_markup=InlineKeyboardMarkup(keyboard))

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id)

    # 1. تحقق الكابتشا أولاً
    if not user_data.get("captcha_solved", False):
        await send_captcha(update.message)
        return

    # 2. تحقق الاشتراك الإجباري
    if not await check_subscription(update, context):
        await send_subscription_msg(update.message)
        return

    # 3. دخول للبوت
    update_user(user.id, {"verified": True})
    await update.message.reply_text(
        f"اهلا وسهلا {user.first_name} 😍\n\n💰 شكرا لك لاختيار متجرنا 🏪\n\n🌼 نتمى لك وقتا ممتعا",
        reply_markup=main_menu_keyboard())

# === أزرار الكابتشا ===
async def captcha_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "captcha_10":
        update_user(user_id, {"captcha_solved": True})
        await query.message.delete()
        # من بعد الكابتشا نشوفو الاشتراك
        if not await check_subscription(update, context):
            await send_subscription_msg(query.message)
        else:
            await start(update, context)
    else:
        await query.answer("❌ إجابة خاطئة! جرب مرة أخرى", show_alert=True)

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_subscription(update, context):
        await query.message.delete()
        await start(update, context)
    else:
        await query.answer("❌ ما زال ما مشتركش في القناة", show_alert=True)

# === معلوماتي ===
async def info_menu(message_obj):
    keyboard = [
        [InlineKeyboardButton("هدية يومية 🎁", callback_data="daily_gift"), InlineKeyboardButton("رابط الإحالة 🔗", callback_data="ref_link")],
        [InlineKeyboardButton("حسابي 👤", callback_data="my_account"), InlineKeyboardButton("الشكوى 📢", callback_data="complaint")]
    ]
    await message_obj.reply_text("معلوماتي – اختر ما تريد:", reply_markup=InlineKeyboardMarkup(keyboard))

# === الأزرار الرئيسية ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user_data = get_user(user_id)

    # لازم يكون داز من الكابتشا والاشتراك
    if not user_data.get("captcha_solved", False):
        await send_captcha(update.message)
        return

    if not await check_subscription(update, context):
        await send_subscription_msg(update.message)
        return

    if text == "معلوماتي 📋":
        await info_menu(update.message)

    elif text == "التطبيقات 📱":
        keyboard = [[InlineKeyboardButton("تطبيقات مجانية 📱", callback_data="apps_free")],
                    [InlineKeyboardButton("تطبيقات مدفوعة 💵", callback_data="apps_paid")],
                    [InlineKeyboardButton("رجوع 🔙", callback_data="back_main")]]
        await update.message.reply_text("اختر نوع التطبيقات:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "المنتجات 🛍️":
        keyboard = [
            [InlineKeyboardButton("أرقام تلجرام ✈️", callback_data="prod_tg"), InlineKeyboardButton("أرقام واتساب 📱", callback_data="prod_wa")],
            [InlineKeyboardButton("أدوات مدفوعة 🛠️", callback_data="prod_tools"), InlineKeyboardButton("حسابات قديمة 👤", callback_data="prod_accounts")],
            [InlineKeyboardButton("كورسات مدفوعة 🎓", callback_data="prod_courses"), InlineKeyboardButton("أدوات مجانية 🆓", callback_data="tools_free")],
            [InlineKeyboardButton("شحن ألعاب وبرامج 🎮", callback_data="prod_games"), InlineKeyboardButton("كورسات مجانية 📚", callback_data="prod_freecourse")],
            [InlineKeyboardButton("عروض 📦", callback_data="prod_offers"), InlineKeyboardButton("خدمات مدفوعة 💼", callback_data="prod_services")],
            [InlineKeyboardButton("رجوع 🔙", callback_data="back_main")]
        ]
        await update.message.reply_text("اختر قسم المنتجات:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "العروض 🎁":
        await update.message.reply_text("لا توجد عروض حالياً. ⚠️")

    elif text == "تحويل عملة 💱":
        await update.message.reply_text("💱 قريباً... خدمة تحويل العملات")

    elif text == "شراء رصيد 💰":
        await update.message.reply_text(f"💰 لشراء الرصيد تواصل مع الإدارة:\n{CHANNEL_USERNAME}")

    elif text == "كود هدية 🎫":
        await update.message.reply_text("🎫 ارسل كود الهدية لي عندك:")

# === أزرار الإنلاين ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_data = get_user(user_id)
    products = load_products()

    if data == "back_main":
        await query.message.delete()

    # معلوماتي
    elif data == "daily_gift":
        last_daily = datetime.strptime(user_data["last_daily"], "%Y-%m-%d")
        if datetime.now() - last_daily >= timedelta(days=1):
            reward = 0.05 # الهدية 0.05$ فقط
            new_balance = round(user_data["balance"] + reward, 2)
            update_user(user_id, {"balance": new_balance, "last_daily": datetime.now().strftime("%Y-%m-%d")})
            await query.edit_message_text(f"🎉 مبروك! ربحتي {reward}$ هدية يومية\n💰 رصيدك دابا: {new_balance}$")
        else:
            await query.answer("⏳ راه خديتي الهدية اليومية ديالك", show_alert=True)

    elif data == "ref_link":
        await query.edit_message_text(f"🔗 رابط الإحالة ديالك:\nhttps://t.me/{context.bot.username}?start={user_id}\n\nكل شخص يدخل من الرابط ديالك تربح 1$")

    elif data == "my_account":
        await query.edit_message_text(f"👤 حسابي:\n\n💰 الرصيد: ${user_data['balance']}\n👥 الإحالات: {user_data['referrals']}\n🆔 ID: {user_id}")

    elif data == "complaint":
        await query.edit_message_text("📢 اكتب الشكوى ديالك وغادي توصل للإدارة")

    # التطبيقات
    elif data == "apps_free":
        buttons = []
        for i, app in enumerate(products["apps_free"]):
            buttons.append([InlineKeyboardButton(f"{app['stock']}📦 | ${app['price']} - {app['name']} 🛒", callback_data=f"buy_app_{i}")])
        buttons.append([InlineKeyboardButton("رجوع 🔙", callback_data="back_main")])
        await query.edit_message_text("اختر المنتج 🛍️:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("buy_app_"):
        idx = int(data.split("_")[2])
        app = products["apps_free"][idx]
        text = f"تطبيق {app['name']} 🛒\n\n{app['desc']} 📝\nالسعر: ${app['price']} 💵\nالمخزون: {app['stock']} 📦\nرصيدك: ${user_data['balance']} 💳"
        keyboard = [[InlineKeyboardButton("تأكيد الشراء ✅", callback_data=f"confirm_app_{idx}")], [InlineKeyboardButton("رجوع 🔙", callback_data="apps_free")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("confirm_app_"):
        idx = int(data.split("_")[2])
        app = products["apps_free"][idx]
        if user_data["balance"] >= app["price"]:
            new_balance = round(user_data["balance"] - app["price"], 2)
            update_user(user_id, {"balance": new_balance})
            products["apps_free"][idx]["stock"] -= 1
            save_products(products)
            await query.edit_message_text(f"تم الشراء بنجاح! ✅\n\nالمنتج: تطبيق {app['name']} 🛍️\nالمبلغ: ${app['price']} 💰\n\nمحتوى المنتج 📦:\n{app['content']}")
        else:
            await query.answer("❌ رصيدك غير كافي", show_alert=True)

    # الأدوات المجانية
    elif data == "tools_free":
        buttons = []
        for i, tool in enumerate(products["tools_free"]):
            buttons.append([InlineKeyboardButton(f"{tool['stock']}📦 | ${tool['price']} - {tool['name']} 🛒", callback_data=f"buy_tool_{i}")])
        buttons.append([InlineKeyboardButton("رجوع 🔙", callback_data="back_main")])
        await query.edit_message_text("اختر من القائمة:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("buy_tool_"):
        idx = int(data.split("_")[2])
        tool = products["tools_free"][idx]
        text = f"جمع معلومات {tool['name']} 🛒\n\n{tool['desc']} 📝\nالسعر: ${tool['price']} 💵\nالمخزون: {tool['stock']} 📦\nرصيدك: ${user_data['balance']} 💳"
        keyboard = [[InlineKeyboardButton("تأكيد الشراء ✅", callback_data=f"confirm_tool_{idx}")], [InlineKeyboardButton("رجوع 🔙", callback_data="tools_free")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("confirm_tool_"):
        idx = int(data.split("_")[2])
        tool = products["tools_free"][idx]
        if user_data["balance"] >= tool["price"]:
            new_balance = round(user_data["balance"] - tool["price"], 2)
            update_user(user_id, {"balance": new_balance})
            products["tools_free"][idx]["stock"] -= 1
            save_products(products)
            await query.edit_message_text(f"تم الشراء بنجاح! ✅\n\nالمنتج: {tool['name']} 🛍️\nالمبلغ: ${tool['price']} 💰\n\nمحتوى المنتج 📦:\n{tool['content']}")
        else:
            await query.answer("❌ رصيدك غير كافي", show_alert=True)

# === تشغيل البوت ===
def main():
    keep_alive()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(captcha_callback, pattern="^captcha_"))
    app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("البوت خدام...")
    app.run_polling()

if __name__ == '__main__':
    main()
