import socket 

def start_client():
    HOST='127.0.0.1'
    PORT=65432
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        username = input("Логин: ")
        pwd = input("Пароль: ")

        #Собираем в формат сервера 
        auth_data=f"{username}:{pwd}"
        s.sendall(auth_data.encode("utf-8"))

        resp=s.recv(1024).decode("utf-8")
        print(f"От сервера: {resp}")

        if resp == "A_OK":
            print("Добро пожаловать!")

        




