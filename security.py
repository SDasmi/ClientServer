import bcrypt

#Хэшируем 
def hash_pwd(password: str)->str:
    pwd_bytes=password.encode('utf-8')
    #Добавим соль и захэшируем 
    hashed_pwd=bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    #После же вернем к привычному виду, декодируя.( Чтобы в бд было красиво)
    return hashed_pwd.decode('utf-8')

def verify_pwd(inserted_pwd: str, stored_hash: str) -> bool:
    #Берет пароль, добавляет соль из того, что хранится, и сравнивает два хэша 
    return bcrypt.checkpw(inserted_pwd.encode('utf-8'), stored_hash.encode('utf-8') )





