import pytz
from datetime import datetime, timedelta
from telebot.types import ChatMember

def register_commands(bot):
    # منطقه زمانی ایران
    IRAN_TIMEZONE = pytz.timezone("Asia/Tehran")

    #/time
    @bot.message_handler(commands=['time'])
    def send_time(message):
        now = datetime.now(IRAN_TIMEZONE)
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        bot.reply_to(message, f"زمان فعلی در ایران: {formatted_time}")

    # /mute
    @bot.message_handler(commands=['mute'])
    def mute_user(message):
    
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ['administrator', 'creator']:
            bot.reply_to(message, "فقط ادمین‌های گروه مجاز به استفاده از این دستور هستند.")
            return

        if message.reply_to_message is None:
            bot.reply_to(message, "لطفاً این دستور را روی پیامی که می‌خواهید کاربر را سکوت کنید، استفاده کنید یا مدت زمان را وارد کنید.")
            return
        
        try:
            duration = int(message.text.split()[1])
            end_time = datetime.now(IRAN_TIMEZONE) + timedelta(minutes=duration)
        except (IndexError, ValueError):
            end_time = None
        
        if end_time:
            muted_user = message.reply_to_message.from_user
            bot.restrict_chat_member(message.chat.id, muted_user.id, until_date=end_time)
            bot.reply_to(message, f"کاربر {muted_user.first_name} به مدت {duration} دقیقه سکوت شد.")
        else:
            muted_user = message.reply_to_message.from_user
            bot.restrict_chat_member(message.chat.id, muted_user.id, until_date=None)
            bot.reply_to(message, f"کاربر {muted_user.first_name} به طور نامحدود سکوت شد.")

    # /unmute
    @bot.message_handler(commands=['unmute'])
    def unmute_user(message):
    
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ['administrator', 'creator']:
            bot.reply_to(message, "فقط ادمین‌های گروه مجاز به استفاده از این دستور هستند.")
            return
        
        if message.reply_to_message is None:
            bot.reply_to(message, "لطفاً این دستور را روی پیامی که می‌خواهید کاربر را از سکوت در بیاورید، استفاده کنید.")
            return
        
        unmuted_user = message.reply_to_message.from_user
        bot.restrict_chat_member(message.chat.id, unmuted_user.id, until_date=None)
        bot.reply_to(message, f"کاربر {unmuted_user.first_name} از سکوت در آمد.")
        
# توسعه دهنده و طراح این پروژه @mrkral میباشد
# این پروژه اولین بار در کانال @MeshkiTm به اشتراک گذاشته شده
# The developer and designer of this project is @mrkral
# This project was shared for the first time on @MeshkiTm channel
