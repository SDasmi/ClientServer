from cryptography.fernet import Fernet 
import struct

#Шифрование пока через пакет а не рса

def generate_key():
    return Fernet.generate_key()

#Само шифрование 
def encrypt_data(data, key):
#Создадим ключ- симметричное шифр фернет
    if isinstance(data, str):
        data=data.encode('utf-8') #превращаем в токен
    return Fernet(key).encrypt(data)

#FERNET еще + дата + HMAC - проверка целостности 
def decrypt_data(data, key):
    return Fernet(key).decrypt(data)


#Запакуем числа 
def pack_length(length):
    return struct.pack('>I', length )

def unpack_lenght(data):
    return struct.unpack('>I', data)[0]

#число обязательно 4 байта
# >I left->right unsigned INT

    

