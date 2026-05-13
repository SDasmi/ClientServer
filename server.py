import socket 
import threading
import os
import encryption
import database
import struct
import time
import files
import sqlite3
HOST ='127.0.0.1'
PORT = 61415



STORAGE_DIR = 'server_storage'
if not os.path.exists(STORAGE_DIR):
    os.mkdir(STORAGE_DIR)

def handle_client(conn, addr, key):
    print(f"[+] Новое подключение {addr}")
    conn.sendall(key)

    try:
    #Аутентефикация (забираем 1КБ)
        
        auth_data = conn.recv(1024).decode('utf-8')
        if ':' not in auth_data:
            conn.send("Неправильный формат, нет :".encode('utf-8'))
            return 
        
        username, pwd = auth_data.split(':')

    #ЛОгин пароль 
        if database.authenticate_user(username, pwd):
            print(f'Пользователь {username} подключился к серверу')
            conn.send(f"A_OK".encode('utf-8'))
        
    #блок принятия команд  
       ########################################################################################

            while True:
                command = conn.recv(1024).decode('utf-8')
                match command:
                    
                    case "UPLOAD":
                        server_file_upload(username, conn, key)
                        conn.send("FILE_RECEIVED_OK".encode('utf-8'))
                    case "GET_INFO":
                        conn.recv
                    case "SHOW_FILES":
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
                    case "EXIT":
                        break
        
        ###################################################################################        
        else:
            print(f"[-] Пользователь {username} ввел неверный пароль")
            conn.send(f"A_FAIL".encode('utf-8'))

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





if __name__=="__main__":

    start_server()
        