import socket
import encryption
import time
import os
import struct
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog

HOST = '127.0.0.1'
PORT = 61415

class ShawarmaClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ Shawarma Client: Britney Edition ✨")
        self.geometry("550x700")
        self.resizable(False, False)
        
        # Яркая стилизация а-ля Britney Pop Star
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
       
        self.style.configure('.', background='#FFF0F5', foreground='#4B0082', font=('Segoe UI', 10))
        self.style.configure('TLabel', background='#FFF0F5', foreground='#C71585', font=('Segoe UI', 10, 'bold'))
        self.style.configure('Header.TLabel', background='#FFF0F5', foreground='#FF1493', font=('Segoe UI', 14, 'bold'))
        
        # Розовые глянцевые кнопки
        self.style.configure('TButton', background='#FF1493', foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=1, focuscolor='none')
        self.style.map('TButton', background=[('active', '#FF69B4')], foreground=[('active', 'white')])
        
        # Золотая кнопка для особых действий
        self.style.configure('Gold.TButton', background='#FFD700', foreground='#4B0082', font=('Segoe UI', 10, 'bold'))
        self.style.map('Gold.TButton', background=[('active', '#FFF8DC')])

        # Стилизация вкладок (Notebook)
        self.style.configure('TNotebook', background='#FFF0F5', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#DA70D6', foreground='white', font=('Segoe UI', 10, 'bold'), padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', '#FF1493')], foreground=[('selected', 'white')])
        
        self.style.configure('TEntry', fieldbackground='#FFFFFF', bordercolor='#FF1493', lightcolor='#FF1493', darkcolor='#FF1493')
        self.style.configure('TRadiobutton', background='#FFF0F5', foreground='#4B0082', font=('Segoe UI', 10))

        self.sock = None
        self.key = None
        self.username = None
        self.pwd = None

       
        self.main_container = tk.Frame(self, bg='#FFF0F5')
        self.main_container.pack(fill="both", expand=True)

        self.show_auth_screen()

    def connect_to_server(self):
       
        try:
            if not self.sock:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((HOST, PORT))
                self.key = self.sock.recv(1024)
            return True
        except Exception as e:
            messagebox.showerror("Network Error ", f"итс бритни бич, сервер упал:\n{e}")
            self.sock = None
            return False

    def disconnect_from_server(self):
       
        if self.sock:
            try:
                self.sock.sendall("EXIT".encode())
                if self.sock.recv(1024).decode() == "CLOSE":
                    pass
            except:
                pass
            finally:
                self.sock.close()
                self.sock = None

    def show_auth_screen(self):
        self.clear_frame()
        
        # Верхний баннер
        banner = ttk.Label(self.main_container, text=" Welcome to the Zone, Shawarma Lover! ", style='Header.TLabel', anchor="center")
        banner.pack(fill="x", pady=(15, 5))
        
        notebook = ttk.Notebook(self.main_container)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Вкладка Входа
        login_frame = ttk.Frame(notebook, padding=20)
        notebook.add(login_frame, text="  Войти ")

        ttk.Label(login_frame, text="Логин:").pack(anchor="w", pady=(10, 2))
        self.ent_login_user = ttk.Entry(login_frame, font=("Segoe UI", 11))
        self.ent_login_user.pack(fill="x", pady=5)

        ttk.Label(login_frame, text="Пароль:").pack(anchor="w", pady=(10, 2))
        self.ent_login_pwd = ttk.Entry(login_frame, show="*", font=("Segoe UI", 11))
        self.ent_login_pwd.pack(fill="x", pady=5)

        ttk.Button(login_frame, text=" Авторизоваться !", command=self.process_login).pack(pady=25, fill="x")

        # Вкладка Регистрации
        reg_frame = ttk.Frame(notebook, padding=20)
        notebook.add(reg_frame, text="  Стать Шаурмолюбом ")

        ttk.Label(reg_frame, text="Придумайте Логин:").pack(anchor="w")
        self.ent_reg_user = ttk.Entry(reg_frame)
        self.ent_reg_user.pack(fill="x", pady=2)

        ttk.Label(reg_frame, text="Придумайте Пароль:").pack(anchor="w", pady=(5, 0))
        self.ent_reg_pwd = ttk.Entry(reg_frame, show="*")
        self.ent_reg_pwd.pack(fill="x", pady=2)

        ttk.Label(reg_frame, text="Любимая шаурма:").pack(anchor="w", pady=(5, 0))
        self.ent_reg_shaurma = ttk.Entry(reg_frame)
        self.ent_reg_shaurma.pack(fill="x", pady=2)

        ttk.Label(reg_frame, text="Секретный рецепт:").pack(anchor="w", pady=(5, 0))
        self.ent_reg_recipe = ttk.Entry(reg_frame)
        self.ent_reg_recipe.pack(fill="x", pady=2)

        ttk.Label(reg_frame, text="Любимая песня Бритни Спирс:").pack(anchor="w", pady=(5, 0))
        self.ent_reg_song = ttk.Entry(reg_frame)
        self.ent_reg_song.pack(fill="x", pady=2)

        ttk.Button(reg_frame, text=" Зарегистрироваться !!! ", command=self.process_registration, style='Gold.TButton').pack(pady=20, fill="x")

    def process_login(self):
        username = self.ent_login_user.get().strip()
        pwd = self.ent_login_pwd.get().strip()

        if not username or not pwd:
            messagebox.showwarning("Gimme More info", "Заполните все поля, крошка!")
            return

        if not self.connect_to_server(): return

        try:
            self.sock.send("USER_YES".encode())
            auth_data = f"{username}:{pwd}"
            self.sock.sendall(encryption.encrypt_data(auth_data, self.key))
            
            resp = self.sock.recv(1024).decode()
            
            if resp == "REQ_2FA":
                two_fa_code = simpledialog.askstring(" Oops!... I Did It Again 2FA ", "Введи 6-значный код безопасности из Google Authenticator:")
                if not two_fa_code:
                    two_fa_code = ""
                self.sock.sendall(encryption.encrypt_data(two_fa_code.strip(), self.key))
                resp = self.sock.recv(1024).decode()

            if resp == "A_OK":
                self.username = username
                self.pwd = pwd
                self.show_main_screen()
            else:
                messagebox.showerror("Toxic ", "Неверный логин, пароль или код 2FA!")
                self.sock.close()
                self.sock = None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка авторизации: {e}")

    def process_registration(self):
        user = self.ent_reg_user.get().strip()
        pwd = self.ent_reg_pwd.get().strip()
        shaurma = self.ent_reg_shaurma.get().strip()
        recipe = self.ent_reg_recipe.get().strip()
        song = self.ent_reg_song.get().strip()

        if not all([user, pwd, shaurma, recipe, song]):
            messagebox.showwarning("Внимание", "Все поля должны быть заполнены!")
            return

        if not self.connect_to_server(): return

        try:
            self.sock.send("USER_NO".encode())
            time.sleep(0.1)
            self.sock.send(encryption.encrypt_data(user, self.key))
            time.sleep(0.1)
            self.sock.send(encryption.encrypt_data(pwd, self.key))
            time.sleep(0.1)
            
            info_data = f"{shaurma}:{recipe}:{song}"
            self.sock.send(encryption.encrypt_data(info_data, self.key))

            server_status_raw = self.sock.recv(1024)
            server_status = encryption.decrypt_data(server_status_raw, self.key).decode()
            
            if server_status.startswith("REG_2FA:"):
                otp_secret = server_status.split(":")[1]
                messagebox.showinfo(" Настройка 2FA ", f"Твой секретный ключ генерации TOTP:\n\n{otp_secret}\n\nДобавь его в свое приложение аутентификации!")
                
                verify_code = simpledialog.askstring(" Подтверждение ", "Введи первый сгенерированный код для проверки:")
                if not verify_code:
                    verify_code = ""
                self.sock.sendall(encryption.encrypt_data(verify_code.strip(), self.key))
                
                final_status = self.sock.recv(1024).decode()
                if final_status == "AUTH_OK":
                    messagebox.showinfo("Circus ", "Пользователь успешно добавлен в базу!")
                    self.username = user
                    self.pwd = pwd
                    self.show_main_screen()
                else:
                    messagebox.showerror("Ошибка", "Первичный код проверки 2FA неверен!")
                    self.sock.close()
                    self.sock = None
            else:
                messagebox.showerror("Ошибка", "Такой логин уже занят!")
                self.sock.close()
                self.sock = None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {e}")

    def show_main_screen(self):
        self.clear_frame()

        # Верхняя гламурная панель приветствия
        top_bar = tk.Frame(self.main_container, bg='#FFF0F5')
        top_bar.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_bar, text=f" Star: {self.username}", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(top_bar, text="Bye-Bye ", command=self.logout, style='Gold.TButton').pack(side="right")

        # Главный блок вкладок
        main_notebook = ttk.Notebook(self.main_container)
        main_notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # ВКЛАДКА 1: Просмотр и изменение данных
        info_tab = ttk.Frame(main_notebook, padding=15)
        main_notebook.add(info_tab, text="  My Secret Info ")

        ttk.Label(info_tab, text=" Посмотреть информацию:", style='Header.TLabel').pack(anchor="w", pady=5)
        btn_grid = ttk.Frame(info_tab)
        btn_grid.pack(fill="x", pady=5)
        
        ttk.Button(btn_grid, text=" Шаурма", command=lambda: self.get_server_info(1)).grid(row=0, column=0, padx=2, sticky="we")
        ttk.Button(btn_grid, text=" Рецепт", command=lambda: self.get_server_info(2)).grid(row=0, column=1, padx=2, sticky="we")
        ttk.Button(btn_grid, text=" Бритни Спирс", command=lambda: self.get_server_info(3)).grid(row=0, column=2, padx=2, sticky="we")
        btn_grid.columnconfigure((0,1,2), weight=1)

        ttk.Separator(info_tab, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(info_tab, text=" Изменить поле:", style='Header.TLabel').pack(anchor="w", pady=5)
        
        self.change_choice = tk.StringVar(value="1")
        ttk.Radiobutton(info_tab, text="Любимая шаурма", variable=self.change_choice, value="1").pack(anchor="w")
        ttk.Radiobutton(info_tab, text="Секретный рецепт", variable=self.change_choice, value="2").pack(anchor="w")
        ttk.Radiobutton(info_tab, text="Песня Бритни", variable=self.change_choice, value="3").pack(anchor="w")
        
        ttk.Label(info_tab, text="Новое значение:").pack(anchor="w", pady=(10, 0))
        self.ent_new_info = ttk.Entry(info_tab, font=("Segoe UI", 10))
        self.ent_new_info.pack(fill="x", pady=5)
        ttk.Button(info_tab, text=" Обновить данные ", command=self.change_server_info).pack(fill="x", pady=5)

        ttk.Separator(info_tab, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(info_tab, text=" Смена пароля:", style='Header.TLabel').pack(anchor="w", pady=5)
        
        ttk.Label(info_tab, text="Старый пароль:").pack(anchor="w")
        self.ent_old_pwd = ttk.Entry(info_tab, show="*")
        self.ent_old_pwd.pack(fill="x", pady=2)
        
        ttk.Label(info_tab, text="Новый пароль:").pack(anchor="w")
        self.ent_new_pwd = ttk.Entry(info_tab, show="*")
        self.ent_new_pwd.pack(fill="x", pady=2)
        
        ttk.Button(info_tab, text=" Изменить пароль ", command=self.password_changing, style='Gold.TButton').pack(fill="x", pady=5)

        # ВКЛАДКА 2: Файлы
        files_tab = ttk.Frame(main_notebook, padding=15)
        main_notebook.add(files_tab, text="  Storage ")

        ttk.Button(files_tab, text=" Отправить файл на сервер", command=self.upload_file_dialog).pack(fill="x", pady=5)
        
        ttk.Separator(files_tab, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(files_tab, text="Доступные файлы на сервере:", style='Header.TLabel').pack(anchor="w", pady=5)
        
        list_frame = ttk.Frame(files_tab)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        self.files_box = tk.Listbox(list_frame, font=("Segoe UI", 10), bg='#FFF5EE', fg='#C71585', selectbackground='#FF69B4', highlightcolor='#FF1493')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.files_box.yview)
        self.files_box.configure(yscrollcommand=scrollbar.set)
        
        self.files_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Новые добавленные кнопки управления файлами
        ttk.Button(files_tab, text=" Скачать выбранный файл", command=self.download_file_dialog).pack(fill="x", pady=2)
        ttk.Button(files_tab, text=" Обновить список файлов", command=self.refresh_files_list).pack(fill="x", pady=5)

        # Сразу при открытии обновляем список файлов
        self.refresh_files_list()

    def get_server_info(self, num):
        try:
            self.sock.send("GET_INFO".encode())
            time.sleep(0.1)
            self.sock.send(str(num).encode())
            
            data = self.sock.recv(1024)
            decrypted_msg = encryption.decrypt_data(data, self.key).decode()
            messagebox.showinfo(" VIP Информация ", decrypted_msg)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")

    def change_server_info(self):
        num = self.change_choice.get()
        new_val = self.ent_new_info.get().strip()
        if not new_val:
            messagebox.showwarning("Внимание", "Введите новые данные!")
            return
        try:
            self.sock.sendall("CHANGE_INFO".encode())
            time.sleep(0.1)
            self.sock.send(num.encode())
            time.sleep(0.1)
            self.sock.sendall(encryption.encrypt_data(new_val, self.key))

            if self.sock.recv(1024).decode() == "OK":
                messagebox.showinfo("Успех ", "Данные успешно изменены!")
                self.ent_new_info.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Сервер отклонил изменение данных.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")

    def password_changing(self):
        old_p = self.ent_old_pwd.get().strip()
        new_p = self.ent_new_pwd.get().strip()
        if not old_p or not new_p:
            messagebox.showwarning("Внимание", "Заполните оба поля!")
            return
        try:
            self.sock.sendall("CHANGE_PWD".encode())
            if self.sock.recv(1024).decode() == "OLD_PWD":
                self.sock.sendall(encryption.encrypt_data(old_p, self.key))
                if self.sock.recv(1024).decode() == "OK":
                    self.sock.sendall(encryption.encrypt_data(new_p, self.key))
                    if self.sock.recv(1024).decode() == "OK":
                        messagebox.showinfo("Успех", "Пароль успешно обновлен, детка!")
                        self.pwd = new_p
                        self.ent_old_pwd.delete(0, tk.END)
                        self.ent_new_pwd.delete(0, tk.END)
                        return
            messagebox.showerror("Ошибка", "Не удалось сменить пароль. Проверь старый!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {e}")

    def refresh_files_list(self):
        try:
            self.sock.sendall("SHOW_FILES".encode())
            self.files_box.delete(0, tk.END)
            n = 0
            while True:
                data_from_server = self.sock.recv(1024)
                if data_from_server == b'ALL' or data_from_server.decode(errors='ignore') == 'ALL':
                    break
                try:
                    decrypted_name = encryption.decrypt_data(data_from_server, self.key).decode('utf-8')
                    self.files_box.insert(tk.END, f" {n+1}. {decrypted_name}")
                    n += 1
                except:
                    continue
            if n == 0:
                self.files_box.insert(tk.END, "Хранилище пустое, как чарты без Бритни...")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список файлов: {e}")

    def upload_file_dialog(self):
        filepath = filedialog.askopenfilename()
        if not filepath: return
        
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            self.sock.sendall("UPLOAD".encode("utf-8"))
            time.sleep(0.1)

            e_data = encryption.encrypt_data(data, self.key)
            e_header = encryption.encrypt_data(f'{filename}:{len(e_data)}', self.key)

            self.sock.sendall(encryption.pack_length(len(e_header)))
            self.sock.sendall(e_header)
            self.sock.sendall(e_data)

            if self.sock.recv(1024).decode() == "FILE_RECEIVED_OK":
                messagebox.showinfo("Успех ", f"Файл {filename} успешно улетел на server!")
                self.refresh_files_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить файл: {e}")

    def download_file_dialog(self):
        """Парсинг выбранного файла из Listbox и скачивание с сервера"""
        selected = self.files_box.curselection()
        if not selected:
            messagebox.showwarning("Внимание ", "Пожалуйста, выберите файл из списка для скачивания!")
            return
        
        item_text = self.files_box.get(selected[0])
        if "Хранилище пустое" in item_text :
            return

        try:
           
            raw_name = item_text.split(". ", 1)[1]
            filename = raw_name.split(" | ")[0].strip()
            
          
            filepath = filedialog.asksaveasfilename(initialfile=filename, title="Куда сохранить файл?")
            if not filepath: 
                return 
            
           
            self.sock.sendall("DOWNLOAD".encode())
            time.sleep(0.1)
            
            encrypted_filename = encryption.encrypt_data(filename, self.key)
            self.sock.sendall(encrypted_filename)

            server_resp = self.sock.recv(1024).decode()
            if server_resp == "FILE_EXISTS":
                length_bytes = self.sock.recv(4)
                if not length_bytes:
                    messagebox.showerror("Ошибка ", "Не удалось прочитать размер файла от сервера.")
                    return
                
                # Используем метод распаковки длины из твоего модуля encryption (с твоей опечаткой lenght)
                content_length = encryption.unpack_lenght(length_bytes)

                encrypted_file_data = b""
                while len(encrypted_file_data) < content_length:
                    packet = self.sock.recv(min(content_length - len(encrypted_file_data), 4096))
                    if not packet:
                        break
                    encrypted_file_data += packet

                # Расшифровываем байты файла
                decrypted_file_data = encryption.decrypt_data(encrypted_file_data, self.key)

                # Записываем на диск
                with open(filepath, 'wb') as f:
                    f.write(decrypted_file_data)
                    
                messagebox.showinfo("Gimme More ", f"Файл успешно скачан и сохранен как:\n{filepath}")
            else:
                messagebox.showerror("Ошибка ", "Сервер ответил, что файл не найден в хранилище.")
        except Exception as e:
            messagebox.showerror("Ошибка ", f"Не удалось скачать файл: {e}")

    def logout(self):
        self.disconnect_from_server()
        self.username = None
        self.pwd = None
        self.show_auth_screen()

    def clear_frame(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = ShawarmaClientGUI()
    app.protocol("WM_DELETE_WINDOW", lambda: [app.logout(), app.destroy()])
    app.mainloop()