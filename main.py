import db
from time import sleep
from telebot import TeleBot

TOKEN = '5725792179:AAHIAlFVHfb5cBfCs6IIvwAwAlyJnQlhlfw'
bot = TeleBot(TOKEN)

game = False
night = True


def get_killed(night):
    if not night:
        username_killed = db.citizens_kill()
        return f"Горожане выгнали: {username_killed}"
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'


def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, 'Добро пожаловать в игру!')
    sleep(60)
    while True:
        msg = get_killed()
        bot.send_message(message.chat.id, msg)
        if night:
            bot.send_message(
                message.chat.id, 'Город засыпает, просыпается мафия. Натупила ночь')
        else:
            bot.send_message(
                message.chat.id, 'Город просыпается, наступил день!')
        winner = db.check_winner()
        if winner is not None:
            game = False
            bot.send_message(message.chat.id, f'Игра окончена! Победили: {winner}')
            return 
        night = not night
        db.clear()
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(
            message.chat.id, f'В игре:\n {alive}')
        sleep(60)



@bot.message_handler(commands=['kick'])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого пользователя нет!')
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан!')
            return
        bot.send_message(message.chat.id, 'У Вас больше нет права голосовать')
    bot.send_message(message.chat.id, 'Сейчас ночь вы не можете голосовать')


@bot.message_handler(commands=["kill"])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    mafia_usernames = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafia_usernames:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote("mafia_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан')
            return
        bot.send_message(
            message.chat.id, 'У вас больше нет права голосовавать')
    bot.send_message(message.chat.id, 'Сейчас нельзя убивать')


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
        db.clear(dead=True)
        game_loop(message)
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
