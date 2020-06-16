import datetime

import telebot
from telebot import apihelper, types
from telebot.types import CallbackQuery, ReplyKeyboardRemove

import telebot_calendar

bot = telebot.TeleBot('1123689735:AAG2yufaFjC0lCaczAarw6Ozc4Cx16SrfPE')
calendar = telebot_calendar.CallbackData("calendar", "action", "year", "month", "day")


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    register = types.KeyboardButton("Забронировать")
    markup.add(register)
    bot.send_message(message.chat.id, "Добро пожаловать, " + message.from_user.first_name + "!",
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def calendar_message(message):
    if message.text == "Забронировать":
        now = datetime.datetime.now()  # Get the current date
        bot.send_message(
            message.chat.id,
            "Selected date",
            reply_markup=telebot_calendar.create_calendar(
                name=calendar.prefix,
                year=now.year,
                month=now.month,
            ),
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar.prefix))
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        if telebot_calendar.check_date(date):
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"You have chosen {date.strftime('%d.%m.%Y')}",
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Вы должны сосать хуй только в будущем", show_alert=True)
        print(f"{calendar}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Бронирование отменено",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar}: Cancellation")




bot.polling()
