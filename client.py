import socket 
import encryption
import os
import info
import time
def start_client():
    
    HOST='127.0.0.1'
    PORT=61415
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            key = s.recv(1024)
        
            username = input("Логин: ")
            pwd = input("Пароль: ")

            #Собираем в формат сервера 
            auth_data=f"{username}:{pwd}"
            s.sendall(auth_data.encode("utf-8"))

            resp=s.recv(1024).decode("utf-8")
         
            if resp == "A_OK":
                print("Добро пожаловать!")
#############################################################################
            while True:
                command = input('''
            ВЫБОР КОММАНД:
            1 Отправить файл
            2 Вывести данные пользователя
            3 Сменить пароль
            4 Изменить данные пользователя
            5 Вывести весь список доступных вам файлов            
            6 Выйти      
             ''')
                
                match command:
                    case "1":
                        filename = input("Введите имя файла")
                        s.sendall("UPLOAD".encode("utf-8"))
                        send_file(s, filename, key)
                        if s.recv(1024).decode()=="FILE_RECEIVED_OK":
                            print(f"Файл {filename} успешно загружен")
                    case "2":
                        num = int(input(''' 1. Любимая шаурма
                                            2. Секретный рецепт
                                            3. Любимая песня Бритни Spears 
                                        '''))
                        s.send(num.encode())
                        time.sleep(0.1)
                        s.send("GET_INFO".encode())
                    case "6":
                        s.sendall("EXIT".encode())
                        if s.recv(1024).decode()=="CLOSE":
                            print("До свидания!")
                            break
                    case "5":
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


                            
                            

        except ConnectionRefusedError:
            print("Что-то не так с сервером...")
            




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
        
