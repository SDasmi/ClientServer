from security import hash_pwd, verify_pwd

if __name__ == "__main__":
    my_pwd = "123456Okkk"

    hashed = hash_pwd(my_pwd)
    print("Saved pwd: ", hashed )

    est_vrai = verify_pwd(my_pwd, hashed)
    print("Одинаковые пароли: ", est_vrai)

    nest_pas_vrai = verify_pwd("ieefhwf", hashed)
    print("Not the same", nest_pas_vrai) 

    #Работает!

    