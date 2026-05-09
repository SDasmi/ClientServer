import socket 
import threading
from database import authenticate_user

HOST ='127.0.0.1'
PORT =65432

def handle_client(conn, addr):
    print(f"[+] Новое подключение {addr}")
    
    try:
    #Аутентефикация (забираем 1КБ)
        auth_data = conn.recv(1024).decode('utf-8')
        if ':' not in auth_data:
            conn.send("Неправильный формат, нет :".encode('utf-8'))
            return 
        
        username, pwd = auth_data.split(':')

    #ЛОгин пароль 
        if authenticate_user(username, pwd):
            print(f'Пользователь {username} подключился к серверу')
            conn.send(f"A_OK".encode('utf-8'))
    #После сюда блок с RSA        
            while True:
                msg=conn.recv(1024).decode('utf-8')
                if not msg or msg=='exit':
                    break
                print(f" {username}: {msg}")
                conn.send(f"Сервер принял ваше сообщение {msg}")
                
        else:
            print(f"[-] Пользователь {username} ввел неверный пароль")
            conn.send(f"A_FAIL".encode('utf-8'))

    except Exception as e:
        print(f"[-] Произошла ошибка {e} у {username}")
        conn.send(f"Произошла ошибка {e}".encode('utf-8'))

    finally:
        conn.close()
        print(f"[-] Подключение по {addr} закрыто")

def start_server():
    #IP_v4/ TCP
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Сервер запущен! на {HOST} {PORT}")

    while True:
        conn, addr = server.accept()
        #Создание потоков для клиента
        thread=threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Кол-во активных соединений = {threading.active_count() -1}")


