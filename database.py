import sqlite3
from security import verify_pwd, hash_pwd

#Подключим базу данных
def create_connection():
    return sqlite3.connect('users.db')

#Если у нас нет до сих пор таблицы пользователей, создадим ее 

def setup_db():

    connection = new_func()
    
    cursor= connection.cursor()

    cursor.execute( '''
    create table if not exists users(
        id integer primary key autoincrement,
        username text not null unique,
        password_hash text not null,
        favorite_shawarma text not null, 
        secret_recipe text not null,
        favorite_song_of_britney text not null
        )'''
    )

    connection.commit()
    connection.close()

def new_func():
    connection =create_connection()
    return connection

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
        return True
    except sqlite3.IntegrityError:
        print(f"The user with this name {username} already exists")
        return False
    finally:
        conn.close()

#Проверка юзера 
def authenticate_user(username: str, raw_pwd: str)->bool:

    conn = sqlite3.connect('users.db')
    cursor=conn.cursor()
 
    #Ищем пользователя
    cursor.execute(''' select password_hash from users where username = ?
            ''', (username, ))
    #достаем один 
    result = cursor.fetchone()
    conn.close()

    #Если не нашли 
    if not result:
        print("Пользователь-шаурмалюб не найден!")
        return False
    
    st_hash=result[0]

    #Проверяем пароль
    if verify_pwd(raw_pwd, st_hash):
        print(f"Пользователь {username}, приступите к вашей шаурме!")
        return True
    else:
        print(f"Неправильный пароль, Give me baby one more time!")
        return False
    

def delete_user(username: str, raw_pwd: str) -> bool:
    #А был ли мальчик?
    if not authenticate_user(username, raw_pwd):
        return False
    
    conn=sqlite3.connect("users.db")
    cursor=conn.cursor()

    try:
        cursor.execute('''
        delete from users where username = ?
                   ''',(username, ))
        conn.commit()
        print(f"Пользователь {username} удален! Mama I'm in love with a criminal")
        return True
    except Exception as e:
        print(f"Возникла ошибка {e}")
        return False 
    finally:
        conn.close()



   

    
    









