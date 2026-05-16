import socket, encryption, time

def start_client():
    
    HOST='127.0.0.1'
    PORT=61415
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            key = s.recv(1024) # Ну и колхоз!
            
            choice = input("Есть аккаунт? 1 - да. 0 - нет: ")
            resp = ""

            if choice == "1": 
                s.send("USER_YES".encode())
                username = input("Логин: ")
                pwd = input("Пароль: ") 
                auth_data = f"{username}:{pwd}"
                s.sendall(encryption.encrypt_data(auth_data, key))
                
                # Ждем ответ от сервера ТОЛЬКО при авторизации
                resp = s.recv(1024).decode()
                if resp == "A_OK":
                    print("Добро пожаловать!")
            else: 
                add_useeer(s, key)
                
                # Исправили .encode() на .decode()
                server_status = s.recv(1024).decode()
                if server_status == "AUTH_OK":
                    print("Пользователь успешно добавлен!")
                    resp = "A_OK" # Имитируем успех, чтобы пройти в меню команд
                else:
                    print("Попробуйте другой логин!")
                    return # Или обработай возврат к началу

            # Пере переходом к командам проверяем статус
        
#############################################################################
            while True:
                command = input('''
            ВЫБОР КОММАНД:
            1 Отправить файл
            2 Вывести данные пользователя
            3 Сменить пароль
            4 Изменить данные пользователя
            5 Вывести весь список доступных вам файлов   
            6 Скачать файлы с сервера         
            8 Выйти      
                ''')
                
                match command:
                    case "1":
                        case_send_file(s, key)

                    case "2":
                        case_get_info_sender(s, key)

                    case "3":
                        case_change_pwd(s, username, key)

                    case "4":
                        case_change_info(s, username, key)

                    case "5":
                        case_show_files(s,username, key)

                    case "6":
                        case_exit(s)
                        break

                            
        except ConnectionRefusedError:
            print("Что-то не так с сервером...")
            


#Кейсы 

def case_send_file(s, key):
    filename = input("Введите имя файла")
    s.sendall("UPLOAD".encode("utf-8"))
    send_file(s, filename, key)
    if s.recv(1024).decode()=="FILE_RECEIVED_OK":
        print(f"Файл {filename} успешно загружен")

def case_get_info_sender(s, key):
    num = (input('''1. Любимая шаурма
                    2. Секретный рецепт
                    3. Любимая песня Бритни Spears '''))
    s.send("GET_INFO".encode())
    time.sleep(0.1)
    s.send(num.encode())
    ###### Принимаем 

    dataa= s.recv(1024)
    print((encryption.decrypt_data(dataa,key)).decode())

def case_change_pwd(s, username, key):
    s.sendall("CHANGE_PWD".encode())
    if s.recv(1024).decode()=="OLD_PWD":
        s.sendall(encryption.encrypt_data(input("Введите старый пароль"), key))
        if s.recv(1024).decode()=="OK":
            s.sendall(encryption.encrypt_data(input("ВВедите новый пароль"), key))
            if s.recv(1024).decode()=="OK":
                print(f"Пароль для {username} успешно изменен")
            else:
                print(f"Не удалось изменить пароль для {username}")
                return 
        else:
            print("Старый пароль неверен!")
            return 
    else:
        print('Пароль не может быть изменен')
        return 

def case_change_info(s, username, key):
    s.sendall("CHANGE_INFO".encode())
    time.sleep(0.1)
    num = input('''Что хотели бы изменить: 
                      1 Любимая шаурма
                      2 Секретный рецепт 
                      3 Любимая песня Бритни Спирс''')
    if num != "1" and num!="2" and num!="3":
        print("Такого поля здесь нет, уж не туда попали вы!")
        return 
    else:
        s.send(num.encode())
        new_info = input("Впишите новые данные: ")
        time.sleep(0.1)
        s.sendall(encryption.encrypt_data(new_info, key))

        if s.recv(1024).decode() == "OK":
            print("Данные успешно изменены!")
        else:
            print("Произошла ошибочка, данные потерпели поражение!")

def case_show_files(s,username, key):
    s.sendall("SHOW_FILES".encode())
    n = 0
    while True: 
        data_from_server = s.recv(1024)
        

        if data_from_server == b'ALL':
            if n:
                print("Все файлы в вашем доступе выведены")
            else:
                print("У вас нет файлов на сервере")
            break
        
        
        try:
            decrypted_name = encryption.decrypt_data(data_from_server, key)
            print(f"{n+1}. {decrypted_name.decode('utf-8')}")
            n += 1
        except Exception as e:
            
            if data_from_server.decode(errors='ignore') == 'ALL':
                break
            print(f"Ошибка при получении данных: {e}")

def case_exit(s):
    s.sendall("EXIT".encode())
    if s.recv(1024).decode()=="CLOSE":
        print("До свидания!")
        

    pass

def add_useeer(s, key):
    s.send("USER_NO".encode())
    print("Введите данные о новом пользователе: ")
    username = input("Логин: ")
    while not username:
        print("ВВЕДИТЕ ПАРУ СИМВОЛОВ")
        username = input("Логин: ")
    s.send(encryption.encrypt_data(username, key))

    pwd = input("Пароль: ")
    while not pwd:
        print("ВВЕДИТЕ ПАРУ СИМВОЛОВ")
        pwd = input("Пароль: ")
    s.send(encryption.encrypt_data(pwd, key))

    ##Сразу запросим информацию 
    fav_shaurma = input("Ваша любимая шаурма: ")
    secret_recept = input("Секретный рецепт шаурмы: ")
    fav_song= input("Любимая песня Бритни Спирс: ")

    info_data = f"{fav_shaurma}:{secret_recept}:{fav_song}"
    s.send(encryption.encrypt_data(info_data, key))


def send_file(s,filename, key):
    #Нужно отправлять в том же формате, как и на сервере
    with open(filename, 'rb') as f:
        data = f.read()
    
   
    e_data = encryption.encrypt_data(data, key)
    e_header = encryption.encrypt_data(f'{filename}:{len(e_data)}', key)


    #сначала пошлем заголовок(size) 

    s.sendall(encryption.pack_length(len(e_header)))
    s.sendall(e_header)
    s.sendall(e_data)

    print(f"Файл {filename} отправлен")

if __name__=="__main__":

    start_client()
        




