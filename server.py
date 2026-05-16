import socket, threading, os, encryption, database, struct, time, files, info

HOST ='127.0.0.1'
PORT = 61415



STORAGE_DIR = 'server_storage'
if not os.path.exists(STORAGE_DIR):
    os.mkdir(STORAGE_DIR)

def handle_client(conn, addr, key):
    print(f"[+] Новое подключение {addr}")
    conn.sendall(key)

    ##Аутентификация/ добавление юзера
    try:
  
        client_choice = conn.recv(1024).decode('utf-8')
        
        if client_choice == "USER_YES":
            auth_data = encryption.decrypt_data(conn.recv(1024), key).decode()
            if ':' not in auth_data:
                print("Неправильный формат, нет :")
                return 
            
            username, pwd = auth_data.split(':')
  
            if database.authenticate_user(username, pwd):
                print(f'Пользователь {username} подключился к серверу')
                conn.send(f"A_OK".encode('utf-8')) 
            else:
                print(f"[-] Пользователь {username} ввел неверный пароль")
                conn.send(f"A_FAIL".encode('utf-8'))
                return
        else:
            ## Добавляем юзера
            b = 0
            while b != 4:
                username = encryption.decrypt_data(conn.recv(1024), key).decode()
                time.sleep(0.1)
                pwd = encryption.decrypt_data(conn.recv(1024), key).decode()
                time.sleep(0.1)
                info_data = encryption.decrypt_data(conn.recv(1024), key).decode()
                
                if ':' not in info_data:
                    print("Неправильный формат, нет :")
                    return 
                
                shaurama, recept, fav_song = info_data.split(':')
                if database.add_user(username, pwd, shaurama, recept, fav_song):
                    conn.send("AUTH_OK".encode())
                    b = 4
                else:
                    conn.send("NOT_OK".encode())
                    return

            # После успешной регистрации сервер провалится вниз 
            # в цикл 'while True' и будет ждать команд, как и клиент

    #блок принятия команд  
       ########################################################################################

        while True:
            command = conn.recv(1024).decode('utf-8')
            match command:
                
                case "UPLOAD":
                    server_file_upload(username, conn, key)
                    conn.send("FILE_RECEIVED_OK".encode('utf-8'))
                
                case "GET_INFO":
                    case_get_info(conn, username, pwd, key)

                case "CHANGE_PWD":
                    case_change_pwd(conn, username, key)

                case "CHANGE_INFO":
                    case_change_info(conn, username, key)
                    
                case "SHOW_FILES":
                    show_files(conn, username, key)
        
                case "EXIT":
                    break
    
        ###################################################################################        
       

    except Exception as e:
        print(f"[-] Произошла ошибка {e} у {username}")
        conn.send(f"Произошла ошибка {e}".encode('utf-8'))

    finally: 
        conn.send("CLOSE".encode())
        conn.close()
        print(f"[-] Подключение по {addr} закрыто")







      
def start_server(): 
    database.setup_db()
    files.setup_db_files()
   
    #IP_v4/ TCP
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Сервер запущен! на {HOST} {PORT}")

    while True:
        conn, addr = server.accept()
        #Создание потоков для клиента
        key = encryption.generate_key()
        thread=threading.Thread(target=handle_client, args=(conn, addr, key))
        thread.start()
        print(f"Кол-во активных соединений = {threading.active_count() -1}")

def server_file_upload(username, conn, key):

   
    # Читаем 4 байта заголовка 
    header_len_data = conn.recv(4)
    header_len = struct.unpack('>I', header_len_data)[0]

    encrypted_header = conn.recv(header_len)
    header_data = encryption.decrypt_data(encrypted_header, key).decode()


    filename, file_size = header_data.split(":")
    
    # Т.к фермет добавляет и метаданные, то просто читаем до конца потока

    encrypted_file = b""

    remaining = int(file_size) 

    while remaining > 0:
        #Читаем остатки либо 4 кб
        chunk = conn.recv(min(remaining, 4096))
        if not chunk:
            break
        encrypted_file += chunk
        remaining -= len(chunk) 

    # Сохраняем
    final_data = encryption.decrypt_data(encrypted_file, key)
    with open(os.path.join("server_storage", filename), "wb") as f:
        f.write(final_data)
    files.add_file(username, filename, file_size)
    print(f"[+] Файл {filename} успешно загружен")

###Разгребем кейсы на функции 




def case_get_info(conn, username, pwd, key):
    numg =  int(conn.recv(1024).decode())
    dataa=info.get_info(username, pwd, numg)
    conn.sendall(encryption.encrypt_data(dataa, key))
    print(f"[+]Информация {username} послана")

def show_files(conn, username, key):
    try:
        rows = files.show_files(username, key) # Убедись, что функция есть
        if not rows:
            conn.sendall("ALL".encode())
        else:
            for row in rows:
                # row[0] - имя, row[1] - дата, row[2] - размер
                file_info = f"{row[0]} | Размер: {row[1]} байт"
                encrypted_row = encryption.encrypt_data(file_info, key)
                conn.sendall(encrypted_row)
                time.sleep(0.1) 
            conn.sendall("ALL".encode())
            print(f"[+] Список файлов для {username} отправлен")
    except Exception as e:
        print(f"Ошибка при выводе файлов: {e}")

def case_change_pwd(conn, username, key):
    conn.sendall("OLD_PWD".encode())
    old_pwd = (encryption.decrypt_data(conn.recv(1024), key)).decode()
    if database.authenticate_user(username, old_pwd):
        print("Cont")
        conn.send("OK".encode())
        new_pwd = (encryption.decrypt_data(conn.recv(1024), key)).decode()
        if info.change_pwd(username, new_pwd):
            conn.send("OK".encode())
        
def case_change_info(conn, username, key):
    num = conn.recv(1024).decode()
    time.sleep(1)
    new_info = (encryption.decrypt_data(conn.recv(1024), key)).decode()

    if info.update_info(username, num, new_info):
        conn.send("OK".encode())
    else: 
        conn.send("NOK".encode())
if __name__ == "__main__":
    start_server()
        