import db
from telebot import TeleBot

TOKEN = '5725792179:AAHIAlFVHfb5cBfCs6IIvwAwAlyJnQlhlfw'
bot = TeleBot(TOKEN)

game = False


@bot.message_handler(commands=['play'])
def play(message):
    if not game:
        bot.send_message(
            message.chat.id, 'Если хотите играть напишите боту в ЛС "готов играть"')


@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def add_player(message):
    db.insert_player(message.from_user.id, message.from_user.first_name)
    bot.send_message(
        message.chat.id, f'Вы {message.from_user.first_name} добавлены в игру!')


if __name__ == '__main__':
    bot.polling()
