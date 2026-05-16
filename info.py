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
                return f"Et voila! Любимая шаурмулечка это - {favorite_shawarma}"
            case 2: 
                return f"Потаённый рецепт: {secret_recipe}"
            case 3:
                return f"Вездесущая Бритни и любимый ее хит - {favorite_song_of_britney}"
            case _:
                return "Сударыня, вы зашли не в тот переулок!"

    return "Шаурмалюб не найден("

def update_info(username: str, num: str, new_info: str):
    
    #Пароли и Нэйм будет в другой функции
    allowed_fields = ['favorite_shawarma', 'secret_recipe', 'favorite_song_of_britney']
    hol = int(num)
    field = allowed_fields[hol - 1] 

    if field not in allowed_fields:
        print(f"[-]Ошибочка: Поле '{field}' не меняется таким темным путем")
        return False
    
    #Подключение
    conn=sqlite3.connect('users.db')
    cursor=conn.cursor()


    try:
    #Изменение 

        cursor.execute(f'''update users set {field} = ? where username =? ''', 
                   (new_info, username))

        conn.commit()
        print(f"[+]{field} успешно обновлено на {new_info}!")
        return True
    
    except Exception as e:
        print(f"[-]Ошибочка вышла: Что-то пошло не так ... {e}")
        return False
    
    finally: 
        conn.close()

def change_pwd(username: str, new_pwd)-> bool:

    new_hash= hash_pwd(new_pwd)

    conn=sqlite3.connect('users.db')
    cursor=conn.cursor()
    try:

        cursor.execute('''
        update users set password_hash = ? where username = ?
        ''', (new_hash, username))   
        conn.commit()
        print(f"[+]Пароль для шаурмолюба {username} успешно изменен")
        return True 
    except Exception as e:
        print(f"[-]Произошла ошибка {e}")
        return False
    finally:
        conn.close()
   

    


