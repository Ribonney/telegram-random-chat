#!/usr/bin/env python
from config import token
from collections import defaultdict
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
"""
users - карта пользователей: статусы и кто с кем связан
Структура:
{
    '<user_id>': {'status': 'free/busy', 'interlocutor': '<interlocutor_id>',
    '<user_id>': ...,
}

user_id и interlocutor_id - это номер чатов (update.message.chat_id)
"""
users = defaultdict(dict)


def scan(current):
    """
    Поиск свободных собеседников для пользователя current
    """
    for key, value in users.items():
        if key != current and value.get('status') == 'free':
            return key
    return None


def connect(user, interlocutor):
    """
    Соединение двух пользователей.
    Установка статусов "занят" и взаимная привязка.
    """
    users[user]['status'] = 'busy'
    users[user]['interlocutor'] = interlocutor
    users[interlocutor]['status'] = 'busy'
    users[interlocutor]['interlocutor'] = user


def find(bot, update):
    """
    Выставление статуса "свободен", запуск поиска и подключение,
    если собеседник найден
    """
    user = update.message.chat_id
    bot.sendMessage(user, text='Kullanıcı Aranıyor...')
    interlocutor = users[user].get('interlocutor')
    if interlocutor:
        bot.sendMessage(interlocutor, text='Bağlantı Kesildi!')
        users[interlocutor]['interlocutor'] = None
        users[user]['interlocutor'] = None
    interlocutor = scan(user)
    if interlocutor:
        connect(user, interlocutor)
        bot.sendMessage(user, text='Bağlantı Başarılı!')
        bot.sendMessage(interlocutor, text='Bağlantı Başarılı!')
    else:
        users[user]['status'] = 'free'


def disconnect(bot, update):
    """
    Отключение от чата с сохранением статуса "занят",
    чтобы не принимать новых сбеседников
    """
    user = update.message.chat_id
    bot.sendMessage(user, text='Bağlantı Kesildi!')
    users[user]['status'] = 'busy'
    interlocutor = users[user].get('interlocutor')
    if interlocutor:
        bot.sendMessage(interlocutor, text='Bağlantı Kesildi!')
        users[interlocutor]['interlocutor'] = None
        users[user]['interlocutor'] = None


def send(bot, update):
    """
    Пересылка сообщения, если у пользователя был собеседник
    """
    user = update.message.chat_id
    interlocutor = users[user].get('interlocutor')
    if not interlocutor:
        bot.sendMessage(user, text="Henüz Bir Konuşma Yok Bağlanmak İçin /find Yazınız!")
    else:
        bot.sendMessage(interlocutor, text=update.message.text)


def start(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Sohbete Hoşgeldin /help Yazarak Yardım Alabilirsin.')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Bu Bot Eğlence Amaçlı [Burak](tg://user?id=991103511) Tarafından Geliştirildi.\n\n/find Yazarak /find yazan kullanıcılar ile bağlantı kurabilir ve onlarla anonim olarak sohbet edebilirsiniz.', parse_mode='MarkDown')


def main():
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('find', find))
    dp.add_handler(CommandHandler('disconnect', disconnect))
    dp.add_handler(MessageHandler([Filters.text], send))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
