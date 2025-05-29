

import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as db_manager 

class AuthUI:
    def __init__(self, root, app_callbacks):
        """
        Инициализирует UI для аутентификации.
        :param root: Корневое окно Tkinter.
        :param app_callbacks: Словарь с колбэками для вызова из основного приложения,
                              например, {'on_login_success': self.setup_main_application_ui}
        """
        self.root = root
        self.app_callbacks = app_callbacks 

        self.login_frame = None
        self.register_frame = None
        self.login_username_entry = None
        self.login_password_entry = None
        self.reg_username_entry = None
        self.reg_password_entry = None
        self.reg_confirm_password_entry = None
        
        self.show_login_screen()

    def clear_auth_frames(self):
        """Удаляет текущие фреймы входа или регистрации."""
        if self.login_frame and self.login_frame.winfo_exists():
            self.login_frame.destroy()
            self.login_frame = None
        if self.register_frame and self.register_frame.winfo_exists():
            self.register_frame.destroy()
            self.register_frame = None
        self.root.unbind('<Return>') 

    def show_login_screen(self):
        """Отображает экран входа."""
        self.clear_auth_frames()
        
        self.root.title("Онлайн Школа - Вход")
        self.root.geometry("400x250")

        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.pack(expand=True, fill="both")

        ttk.Label(self.login_frame, text="Логин:", font=("Arial", 12)).pack(pady=5)
        self.login_username_entry = ttk.Entry(self.login_frame, width=30, font=("Arial", 12))
        self.login_username_entry.pack(pady=5)
        self.login_username_entry.focus()

        ttk.Label(self.login_frame, text="Пароль:", font=("Arial", 12)).pack(pady=5)
        self.login_password_entry = ttk.Entry(self.login_frame, width=30, show="*", font=("Arial", 12))
        self.login_password_entry.pack(pady=5)

        login_button = ttk.Button(self.login_frame, text="Войти", command=self._handle_login_attempt)
        login_button.pack(pady=10)
        
        self.root.bind('<Return>', lambda event: login_button.invoke())

        register_button = ttk.Button(self.login_frame, text="Регистрация", command=self.show_registration_screen)
        register_button.pack(pady=5)
        
    def show_registration_screen(self):
        """Отображает экран регистрации."""
        self.clear_auth_frames()

        self.root.title("Онлайн Школа - Регистрация")
        

        self.register_frame = ttk.Frame(self.root, padding="20")
        self.register_frame.pack(expand=True, fill="both")

        ttk.Label(self.register_frame, text="Логин (мин. 3 симв.):", font=("Arial", 12)).pack(pady=5)
        self.reg_username_entry = ttk.Entry(self.register_frame, width=30, font=("Arial", 12))
        self.reg_username_entry.pack(pady=5)
        self.reg_username_entry.focus()

        ttk.Label(self.register_frame, text="Пароль (мин. 6 симв.):", font=("Arial", 12)).pack(pady=5)
        self.reg_password_entry = ttk.Entry(self.register_frame, width=30, show="*", font=("Arial", 12))
        self.reg_password_entry.pack(pady=5)
        
        ttk.Label(self.register_frame, text="Повторите пароль:", font=("Arial", 12)).pack(pady=5)
        self.reg_confirm_password_entry = ttk.Entry(self.register_frame, width=30, show="*", font=("Arial", 12))
        self.reg_confirm_password_entry.pack(pady=5)

        reg_button = ttk.Button(self.register_frame, text="Зарегистрироваться", command=self._handle_registration_attempt)
        reg_button.pack(pady=10)
        
        self.root.bind('<Return>', lambda event: reg_button.invoke())

        back_to_login_button = ttk.Button(self.register_frame, text="Назад ко входу", command=self.show_login_screen)
        back_to_login_button.pack(pady=5)

    def _handle_login_attempt(self):
        """Обрабатывает попытку входа пользователя."""
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка входа", "Логин и пароль не могут быть пустыми.", parent=self.root)
            return

        if db_manager.check_user_credentials_db(username, password):
            
            if 'on_login_success' in self.app_callbacks:
                self.app_callbacks['on_login_success'](username)
            else:
                
                messagebox.showinfo("Успешный вход", f"Добро пожаловать, {username}!", parent=self.root)
                self.clear_auth_frames() 
        else:
            messagebox.showerror("Ошибка входа", "Неверный логин или пароль.", parent=self.root)
            self.login_password_entry.delete(0, tk.END)

    def _handle_registration_attempt(self):
        """Обрабатывает попытку регистрации пользователя."""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Ошибка регистрации", "Все поля должны быть заполнены.", parent=self.root)
            return
        if len(username) < 3:
            messagebox.showerror("Ошибка регистрации", "Логин должен содержать не менее 3 символов.", parent=self.root)
            return
        if len(password) < 6:
            messagebox.showerror("Ошибка регистрации", "Пароль должен содержать не менее 6 символов.", parent=self.root)
            return
        if password != confirm_password:
            messagebox.showerror("Ошибка регистрации", "Пароли не совпадают.", parent=self.root)
            return

        reg_result = db_manager.add_user_db(username, password)
        if reg_result == True:
            messagebox.showinfo("Успешная регистрация", "Пользователь успешно зарегистрирован. Теперь вы можете войти.", parent=self.root)
            self.show_login_screen() 
        elif reg_result == "integrity_error":
            messagebox.showerror("Ошибка регистрации", "Пользователь с таким именем уже существует.", parent=self.root)
        

if __name__ == '__main__':
    
    root_test = tk.Tk()
    
    def test_login_success(logged_in_username):
        print(f"Пользователь {logged_in_username} успешно вошел (тест).")
        
        
        messagebox.showinfo("Тест", f"Успешный вход: {logged_in_username}", parent=root_test)
        auth_ui.clear_auth_frames() 
        


    callbacks_test = {'on_login_success': test_login_success}
    auth_ui = AuthUI(root_test, callbacks_test)
    
    
    db_manager.init_db()
    
    root_test.mainloop()