from database import *
if __name__ == "__main__":
    setup_db()

    add_user("Darya", "OneTwoThree", "Тэйсти", "В шаурму должен быть добавлен такой соус Тэйсти и в таком кол-ве, чтобы трепетало сердце", "Criminal")
    
    authenticate_user("Darya", "OneTwoThree")
    authenticate_user("Darya", "TwoThree")
    authenticate_user("Darcdya", "OneTwoThree")
    authenticate_user("", "")
    
    



