import socket, threading, os, encryption, database, struct, time, files, info, random, base64, hmac
import hashlib
HOST ='127.0.0.1'
PORT = 61415



STORAGE_DIR = 'server_storage'
if not os.path.exists(STORAGE_DIR):
    os.mkdir(STORAGE_DIR)

def handle_client(conn, addr, key):
    print(f"[+] Новое подключение {addr}")
    conn.sendall(key)
    username = None
    ##Аутентификация/ добавление юзера
    try:
        client_choice = conn.recv(1024).decode('utf-8')
        
       
        if client_choice == "USER_YES":
            auth_data = encryption.decrypt_data(conn.recv(1024), key).decode()
            if ':' not in auth_data: return 
            
            username, pwd = auth_data.split(':')
            if database.authenticate_user(username, pwd):
                
                # КРАСИВО: Запрашиваем секрет через метод database.py, без прямого SQL-кода тут
                otp_secret = database.get_otp_secret(username)
                
                if otp_secret:
                    conn.sendall("REQ_2FA".encode()) # Просим ввести код 2FA
                    client_code = encryption.decrypt_data(conn.recv(1024), key).decode()
                    
                    current_interval = int(time.time() // 30)
                    valid_codes = [
                        verify_totp(otp_secret, current_interval),
                        verify_totp(otp_secret, current_interval - 1),
                        verify_totp(otp_secret, current_interval + 1)
                    ]
                    
                    if client_code in valid_codes:
                        print(f"[+] {username} успешно подтвердил сессию кодом 2FA")
                        conn.sendall("A_OK".encode('utf-8'))
                    else:
                        print(f"[-] {username} провалил проверку 2FA-кода")
                        conn.sendall("A_FAIL".encode('utf-8'))
                        return
                else:
                    conn.sendall("A_OK".encode('utf-8')) 
            else:
                print(f"[-] Пользователь {username} ввел неверный пароль")
                conn.sendall("A_FAIL".encode('utf-8'))
                return
                
        # --- СЦЕНАРИЙ РЕГИСТРАЦИИ С ИНИЦИАЛИЗАЦИЕЙ 2FA ---
        else:
            user = encryption.decrypt_data(conn.recv(1024), key).decode()
            pwd = encryption.decrypt_data(conn.recv(1024), key).decode()
            info_data = encryption.decrypt_data(conn.recv(1024), key).decode()
            
            shaurma, recipe, song = info_data.split(':')
            
            # ЭФФЕКТИВНО: Генерируем новый секрет СРАЗУ до внесения в базу
            otp_secret = generate_totp_secret()
            
            # Передаем секрет в add_user, сохраняя всё одним махом
            if database.add_user(user, pwd, shaurma, recipe, song, otp_secret):
                
                # Отправляем секрет клиенту для привязки в приложении
                conn.sendall(f"REG_2FA:{otp_secret}".encode())
                
                # Проверяем, что пользователь успешно настроил приложение
                verify_code = encryption.decrypt_data(conn.recv(1024), key).decode()
                current_interval = int(time.time() // 30)
                
                if verify_code == verify_totp(otp_secret, current_interval):
                    username = user
                    conn.sendall("AUTH_OK".encode())
                else:
                    # Если первый код не подошел, вызываем метод удаления из database.py
                    database.delete_user_by_username(user)
                    conn.sendall("AUTH_FAIL".encode())
                    return
            else:
                conn.sendall("AUTH_FAIL".encode())
                return
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

                case "DOWNLOAD":
                    case_download(conn, username, key)
                    
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
        
def case_download(conn, username, key):
    try:
       
        encrypted_filename = conn.recv(1024)
        if not encrypted_filename: return
        filename = encryption.decrypt_data(encrypted_filename, key).decode()
        
        filename = os.path.basename(filename)
        filepath = os.path.join(STORAGE_DIR, filename)
        
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            conn.sendall("FILE_EXISTS".encode())
            time.sleep(0.1)
            
            with open(filepath, 'rb') as f:
                file_data = f.read()
            

            encrypted_data = encryption.encrypt_data(file_data, key)
            
           
            conn.sendall(encryption.pack_length(len(encrypted_data)))
            time.sleep(0.1)
            
          
            conn.sendall(encrypted_data)
            print(f"[+] Файл {filename} успешно отправлен пользователю {username}")
        else:
            conn.sendall("FILE_NOT_FOUND".encode())
            print(f"[-] Файл {filename} не найден в хранилище для {username}")
    except Exception as e:
        print(f"[-] Ошибка при перессылке файла: {e}")


def case_change_info(conn, username, key):
    num = conn.recv(1024).decode()
    time.sleep(1)
    new_info = (encryption.decrypt_data(conn.recv(1024), key)).decode()

    if info.update_info(username, num, new_info):
        conn.send("OK".encode())
    else: 
        conn.send("NOK".encode())



def generate_totp_secret():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', k=16))

def verify_totp(secret, intervals_no):
    ##Генерация 6-значного кода
    missing_padding = len(secret) % 8
    if missing_padding:
        secret += '=' * (8 - missing_padding)
    key = base64.b32decode(secret, casefold=True)
    msg = struct.pack(">Q", intervals_no)
    hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()
    o = hmac_hash[19] & 15
    token = (struct.unpack(">I", hmac_hash[o:o+4])[0] & 0x7fffffff) % 1000000
    return f"{token:06d}"

if __name__ == "__main__":
    start_server()
        