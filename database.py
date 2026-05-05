import sqlite3
from security import verify_pwd, hash_pwd

#Подключим базу данных
def create_connection():
    return sqlite3.connect('users.db')

#Если у нас нет до сих пор таблицы пользователей, создадим ее 
def setup_db():
    connection = create_connection()
    cursor= connection.cursor()

    cursor.execute( '''
    create table if not exists users(
        id integer primary key autoincrement,
        username text not null unique,
        password_hash text not null,
        favorite_shawarma text not null, 
        secret_recipe text not null,
        favorite_song_of_britney text not null)
'''
    )

    connection.commit()
    connection.close()

    print("Users принялись за осбуждение шаурмы и Бритни Спирс!")


#Добавим пользователя
def add_user(username: str, pwd: str, shawarma: str, recipe: str, song: str):
    h_pwd = hash_pwd(pwd)

    conn = create_connection() #объект соединения 
    cursor = conn.cursor() #О, Вергилий 

#Само добавление 
    try:
        cursor.execute(''' insert into users (username, password_hash, favorite_shawarma, secret_recipe, favorite_song_of_britney)
        values (?, ?, ?, ?, ?)
        ''', (username, h_pwd, shawarma, recipe, song))
        conn.commit()
        print(f"The user {username} has been successfully added to the db")
    except sqlite3.IntegrityError:
        print(f"The user with this name {username} already exists")
    finally:
        conn.close()





