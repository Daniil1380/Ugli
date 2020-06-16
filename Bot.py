import datetime

import telebot
from telebot import apihelper, types
from telebot.types import CallbackQuery, ReplyKeyboardRemove

import telebot_calendar

bot = telebot.TeleBot('1123689735:AAG2yufaFjC0lCaczAarw6Ozc4Cx16SrfPE')
calendar = telebot_calendar.CallbackData("calendar", "action", "year", "month", "day")
key_Button = []
dateUsers = dict()


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
            "Выберите дату",
            reply_markup=telebot_calendar.create_calendar(
                name=calendar.prefix,
                year=now.year,
                month=now.month, ), )


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
            dateUsers[call.from_user.id] = f"{date.strftime('%d.%m.%Y')}"
            print(dateUsers[call.from_user.id])
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Вы выбрали: {date.strftime('%d.%m.%Y')}",
                reply_markup=ReplyKeyboardRemove(),
            )
            key = types.InlineKeyboardMarkup(row_width=3)
            for i in range(0, 18, 1):
                key_Button.append(types.InlineKeyboardButton(text=str(15 + i % 18 // 2) + ':' + str(i % 2 * 3) + '0',
                                                             callback_data=str(15 + i % 18 // 2) + ':' + str(
                                                                 i % 2 * 3) + '0'))
            key_Button.append(types.InlineKeyboardButton(text="00:00", callback_data="00:00"))
            key_Button.append(types.InlineKeyboardButton(text="00:30", callback_data="00:30"))
            key_Button.append(types.InlineKeyboardButton(text="01:00", callback_data="01:00"))
            key_Button.reverse()
            for j in range(0, 7, 1):
                key.row(key_Button.pop(), key_Button.pop(), key_Button.pop())
            bot.send_message(call.from_user.id, "Выберите время", reply_markup=key)

        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете выбрать дату из прошлого",
                                      show_alert=True)
        print(f"{calendar}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Бронирование отменено",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar}: Cancellation")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: CallbackQuery):
    if call.message:
        for i in range(0, 48, 1):
            if i < 20:
                s = '0'
            else:
                s = ''
            s = s + str(i // 2) + ":" + str(3 * (i % 2)) + "0"
            if call.data == s:
                bot.send_message(
                    chat_id=call.from_user.id,
                    text="Вы выбрали: " + s,
                    reply_markup=ReplyKeyboardRemove(),
                )
                bot.delete_message(
                    chat_id=call.message.chat.id, message_id=call.message.message_id
                )
                bot.send_message('661902517',
                                 "Пользователь с ID: " + str(call.from_user.id) + "\n" + "забронировал столик \n"
                                 + dateUsers[call.from_user.id] + " в " + s)
                dateUsers.pop(call.from_user.id, None)


bot.polling()
