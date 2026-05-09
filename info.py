from database import *

def get_info(username: str, raw_pwd: str, num: int) ->str:
   
    #Проверяем еще разочек
    if not authenticate_user(username, raw_pwd):
        return  "Куда вы лезете! Логин или пароль неправильны"
        
 
    conn=sqlite3.connect('users.db')
    cursor=conn.cursor()

    cursor.execute('''
    select favorite_shawarma, secret_recipe, favorite_song_of_britney from users where username = ? 
                   ''', (username, ))

    row=cursor.fetchone()
    conn.close()


    if row:
        favorite_shawarma, secret_recipe, favorite_song_of_britney = row 
        match num:
            case 1:
                print(f"Et voila! Любимая шаурмулечка это - {favorite_shawarma}")
            case 2: 
                print (f"Потаённый рецепт: {secret_recipe}")
            case 3:
                print (f"Вездесущая Бритни и любимый ее хит - {favorite_song_of_britney}")
            case _:
                print("Сударыня, вы зашли не в тот переулок!")

    return "Шаурмалюб не найден("

def update_info(username: str, raw_pwd: str, field: str, new_info: str):
    if not authenticate_user(username, raw_pwd):
        print(f"Пользователь {username} не найден!")
        return
    
    #Пароли и Нэйм будет в другой функции
    allowed_fields = ['favorite_shawarma', 'secret_recipe', 'favorite_song_of_britney']
    
    if field not in allowed_fields:
        print(f"Ошибочка: Поле '{field}' не меняется таким темным путем")
        return 
    
    #Подключение
    conn=sqlite3.connect('users.db')
    cursor=conn.cursor()


    try:
    #Изменение 

        cursor.execute(f'''update users set {field} = ? where username =? ''', 
                   (new_info, username))

        conn.commit()
        print(f"{field} успешно обновлено на {new_info}!")
        return 
    
    except Exception as e:
        print(f"Ошибочка вышла: Что-то пошло не так ... {e}")
        return
    
    finally: 
        conn.close()


