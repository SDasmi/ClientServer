from security import hash_pwd, verify_pwd
from info import * 

import database
import info

if __name__ == "__main__":
    database.add_user("CHER", "1111", "Страх Влада Дракулы", "Вкусный чесночныц соус", "Criminal" )
    info.get_info("CHER", "1111", 2)
    




    