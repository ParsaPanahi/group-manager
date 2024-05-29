import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import sys
from kral import register_commands  # ایمپورت دستورات از فایل kral.py

if len(sys.argv) != 2:
    print("Usage: python3 vil.py <API_TOKEN>")
    sys.exit(1)

API_TOKEN = sys.argv[1]

bot = telebot.TeleBot(API_TOKEN)

# فراخوانی دستورات از kral.py
register_commands(bot)

# دیکشنری برای نگهداری تعداد اخطارهای کاربران
warnings = {}

# تابع برای چک کردن اینکه آیا کاربر ادمین است یا خیر
def is_user_admin(chat_id, user_id):
    chat_admins = bot.get_chat_administrators(chat_id)
    for admin in chat_admins:
        if admin.user.id == user_id:
            return True
    return False

# دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("دستورات", callback_data="commands"))
    markup.add(InlineKeyboardButton("راهنما", callback_data="help"))

    bot.send_message(message.chat.id, "به ربات مدیریت گروه خوش آمدید !", reply_markup=markup)

# inline Button -
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "commands":
        bot.send_message(call.message.chat.id, "• دستورات ربات به شرح زیر میباشد\n\n"
                                                "/addadmin ادمین کردن کاربر\n"
                                                "/deladmin ‌حذف از ادمینی\n"
                                                "/ban بن کردن کاربر\n"
                                                "/pin پین کردن پیام ریپلی شده\n"
                                                "/unpin حذف پیام پین شده\n"
                                                "/mute سکوت کردن کاربر\n"
                                                "/mute 00 سکوت کردن کاربر زمان معینی\n"
                                                "/unmute حذف از سکوتی\n"
                                                "/info اطلاعات کاربر\n\n"
                                                "programer @mrkral")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "متن راهنما")

# دستور /warn
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return
    
    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیام کاربری که می‌خواهید اخطار بدهید، ریپلای کنید.")
        return
    
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name

    if user_id not in warnings:
        warnings[user_id] = 0

    warnings[user_id] += 1

    if warnings[user_id] >= 3:
        try:
            bot.kick_chat_member(message.chat.id, user_id)
            bot.reply_to(message, f"کاربر @{user_name} به دلیل دریافت 3 اخطار از گروه بن شد.")
            warnings.pop(user_id, None)  # حذف کاربر از دیکشنری پس از بن شدن
        except Exception as e:
            bot.reply_to(message, f"مشکلی در بن کردن کاربر پیش آمد: {e}")
    else:
        bot.reply_to(message, f"کاربر @{user_name} اخطار {warnings[user_id]}/3 را دریافت کرد.")

# دستور /unwarn
@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return
    
    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیام کاربری که می‌خواهید اخطارها را حذف کنید، ریپلای کنید.")
        return
    
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name

    if user_id in warnings and warnings[user_id] > 0:
        warnings[user_id] -= 1
        bot.reply_to(message, f"یک اخطار از کاربر @{user_name} حذف شد. اخطارهای باقی‌مانده: {warnings[user_id]}")
        if warnings[user_id] == 0:
            warnings.pop(user_id)
    else:
        bot.reply_to(message, f"کاربر @{user_name} هیچ اخطاری ندارد.")

# دستور /ban
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return
    
    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیام کاربری که می‌خواهید بن کنید، ریپلای کنید.")
        return
    
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name

    try:
        bot.kick_chat_member(message.chat.id, user_id)
        bot.reply_to(message, f"کاربر @{user_name} از گروه بن شد.")
    except Exception as e:
        bot.reply_to(message, f"مشکلی در بن کردن کاربر پیش آمد: {e}")

# دستور /pin
@bot.message_handler(commands=['pin'])
def pin_message(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return
    
    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیامی که می‌خواهید پین کنید، ریپلای کنید.")
        return

    try:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.reply_to(message, "پیام مورد نظر پین شد.")
    except Exception as e:
        bot.reply_to(message, f"مشکلی در پین کردن پیام پیش آمد: {e}")

# دستور /unpin
@bot.message_handler(commands=['unpin'])
def unpin_message(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return
    
    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    try:
        bot.unpin_chat_message(message.chat.id)
        bot.reply_to(message, "پیام پین شده برداشته شد.")
    except Exception as e:
        bot.reply_to(message, f"مشکلی در برداشتن پین پیام پیش آمد: {e}")

# دستور /addadmin
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return

    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیام کاربری که می‌خواهید ادمین کنید، ریپلای کنید.")
        return

    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name

    try:
        bot.promote_chat_member(
            message.chat.id, user_id,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True
        )
        bot.reply_to(message, f"کاربر @{user_name} به عنوان ادمین اضافه شد.")
    except Exception as e:
        bot.reply_to(message, f"مشکلی در ادمین کردن کاربر پیش آمد: {e}")

# دستور /deladmin
@bot.message_handler(commands=['deladmin'])
def del_admin(message):
    if message.chat.type != "supergroup":
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")
        return

    if not is_user_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "این دستور فقط برای ادمین‌ها قابل استفاده است.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیام کاربری که می‌خواهید از ادمینی عزل کنید، ریپلای کنید.")
        return

    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name

    try:
        bot.promote_chat_member(
            message.chat.id, user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        bot.reply_to(message, f"کاربر @{user_name} از ادمینی عزل شد.")
    except Exception as e:
        bot.reply_to(message, f"مشکلی در عزل کردن کاربر از ادمینی پیش آمد: {e}")

# دستور /info
@bot.message_handler(commands=['info'])
def user_info(message):
    if not message.reply_to_message:
        bot.reply_to(message, "باید به پیام کاربری که می‌خواهید اطلاعاتش را ببینید، ریپلای کنید.")
        return
    
    user = message.reply_to_message.from_user

    try:
        profile_photos = bot.get_user_profile_photos(user.id)
        photo_count = profile_photos.total_count
        profile_photo = profile_photos.photos[0][0].file_id if photo_count > 0 else None
    except Exception as e:
        bot.reply_to(message, f"مشکلی در دریافت عکس پروفایل کاربر پیش آمد: {e}")
        return

    user_info = f"🔹 آیدی: {user.id}\n"
    user_info += f"🔹 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
    user_info += f"🔹 نام: {user.first_name} {user.last_name if user.last_name else ''}\n"
    user_info += f"🔹 تعداد عکس‌های پروفایل: {photo_count}\n"
    user_info += f"🔹 کاربر پرمیوم: {'بله' if user.is_premium else 'خیر'}\n"

    if profile_photo:
        bot.send_photo(message.chat.id, profile_photo, caption=user_info)
    else:
        bot.send_message(message.chat.id, user_info)

# شروع ربات
if __name__ == "__main__":
    bot.polling()