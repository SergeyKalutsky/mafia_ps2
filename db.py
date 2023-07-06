from random import shuffle
import sqlite3


def insert_player(player_id, username):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"INSERT INTO players (player_id, username) VALUES ('{player_id}', '{username}')"
    cur.execute(sql)
    con.commit()
    con.close()


def players_amount():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = 'SELECT * FROM players'
    cur.execute(sql)
    rows = cur.fetchall()  # [(2231, 'sd'...), (), ()]
    con.close()
    return len(rows)


def get_mafia_usernames():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE role = 'mafia' "
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    con.close()
    return names


def get_players_roles():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def get_all_alive():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE dead = 0 "
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    con.close()
    return data


def set_roles(players):
    game_roles = ['citizen'] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_roles[i] = 'mafia'
    shuffle(game_roles)
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT player_id FROM players"
    cur.execute(sql)
    player_ids = cur.fetchall()
    player_ids = [row[0] for row in player_ids]
    for player_id, role in zip(player_ids, game_roles):
        sql = f"UPDATE players SET role = '{role}' where player_id = {player_id}"
        cur.execute(sql)
    con.commit()
    con.close()


def vote(type, username, player_id):
    # mafia_vote, citizen_vote
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE player_id = {player_id} AND dead = 0 AND voted = 0"
    cur.execute(sql)
    can_vote = cur.fetchone()  # ('Sergey')/ ()
    if can_vote:
        sql = f"UPDATE players SET {type} = {type} + 1 WHERE username = '{username}' "
        cur.execute(sql)
        sql = f"UPDATE players SET voted = 1 WHERE player_id = {player_id}"
        cur.execute(sql)
        con.commit()
        con.close()
        return True
    con.close()
    return False


def mafia_kill():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute('SELECT MAX(mafia_vote) FROM players')
    max_vote = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia' ")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    if mafia_alive == max_vote:
        cur.execute(f'SELECT username FROM players WHERE mafia_vote = {max_vote}')
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}' ")
        con.commit()
    con.close()
    return username_killed
