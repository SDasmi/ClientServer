 
import sqlite3

def setup_db_files():
    conn = sqlite3.connect('file.db')
    cursor = conn.cursor()

    cursor.execute('''
                    create table if not exists file (
    id integer primary key autoincrement,
    user_id integer not null,
    filename text not null,
    filesize integer,
    foreign key (user_id) references users (id) on delete cascade
)''')
    
    conn.commit()
    conn.close()


def find_userid(username: str) -> int:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
    select id from users where username = ?''', (username,))

    id = cursor.fetchone()
    conn.close()
    return id[0] if id else None


def add_file(username: str, filename: str, filesize: int) -> bool:

    user_id = find_userid(username)
    if user_id is None: return False

    conn=sqlite3.connect('file.db')
    cursor = conn.cursor()

   
    #Короче, проверяем, сущ ли уже такой файл, если да, то либо удаляй, либо забудь
    
    cursor.execute('''
    select filename from file where filename = ? and user_id =?
''', (filename, user_id))

    double = cursor.fetchone()

    if cursor.fetchone():
        print(f"[-] Файл {filename} уже есть у {username}")
        conn.close()
        return False
    
    else:
        cursor.execute('''
    insert into files (user_id, filename, filesize) values (?, ?, ?)
''', (user_id, filename,filesize))
        conn.commit()
        conn.close()

#Надо написать, чтобы выводило все файлы по запросу 

def show_files(username: str, key):
    user_id = find_userid(username)
    if user_id is None:
        return [] 
        
    conn = sqlite3.connect('file.db') 
    cursor = conn.cursor()
    cursor.execute('SELECT filename, filesize FROM files WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows



    


    