import db
from time import sleep
from telebot import TeleBot

TOKEN = '5725792179:AAHIAlFVHfb5cBfCs6IIvwAwAlyJnQlhlfw'
bot = TeleBot(TOKEN)

game = False
night = True


def game_loop(message):
    global night
    bot.send_message(message.chat.id, 'Добро пожаловать в игру!')
    sleep(5)
    while True:
        if night:
            bot.send_message(
                message.chat.id, 'Город засыпает, просыпается мафия. Натупила ночь')
        else:
            bot.send_message(
                message.chat.id, 'Город просыпается, наступил день!')
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(
                message.chat.id, f'В игре:\n {alive}')
        sleep(5)


@bot.message_handler(commands=['test'])
def test(message):
    game_loop(message)


@bot.message_handler(commands=['game'])
def start_game(message):
    global game
    players = db.players_amount()
    if players >= 5 and not game:
        db.set_roles(players)
        players_roles = db.get_players_roles()
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, text=role)
            if role == 'mafia':
                bot.send_message(
                    player_id, text=f'Все члены мафии:\n{mafia_usernames}')
        game = True
        bot.send_message(message.chat.id, text='Игра началась!')
        return
    bot.send_message(message.chat.id, text='Недостаточно людей!')


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
