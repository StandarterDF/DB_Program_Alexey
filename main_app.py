

import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as db_manager
import auth_ui
import courses_ui
import students_ui
import favorites_ui


class OnlineSchoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Онлайн Школа") 
        

        
        db_manager.init_db()

        self.current_user = None
        self.main_app_frame = None 
        self.notebook = None

        
        
        self.student_name_to_id = {} 
        self.course_title_to_id = {}

        
        self.courses_tab_instance = None
        self.students_tab_instance = None
        self.favorites_tab_instance = None

        
        auth_callbacks = {'on_login_success': self._on_login_success}
        self.auth_interface = auth_ui.AuthUI(self.root, auth_callbacks)

    def _on_login_success(self, username):
        """Колбэк, вызываемый AuthUI после успешного входа."""
        self.current_user = username
        messagebox.showinfo("Успешный вход", f"Добро пожаловать, {username}!", parent=self.root)
        
        
        if hasattr(self.auth_interface, 'clear_auth_frames'):
            self.auth_interface.clear_auth_frames()
            
        self._setup_main_application_ui()

    def _setup_main_application_ui(self):
        """Настраивает основной интерфейс приложения после входа."""
        self.root.title(f"Онлайн Школа - CRUD (Пользователь: {self.current_user})")
        self.root.geometry("1050x750")

        self.main_app_frame = ttk.Frame(self.root)
        self.main_app_frame.pack(expand=True, fill="both")
        
        
        status_bar_frame = ttk.Frame(self.main_app_frame, relief=tk.SUNKEN, padding=2)
        status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_bar_frame, text=f"Пользователь: {self.current_user}").pack(side=tk.LEFT, padx=5)
        ttk.Button(status_bar_frame, text="Выход", command=self._logout).pack(side=tk.RIGHT, padx=5)

        self.notebook = ttk.Notebook(self.main_app_frame)

        
        self.courses_tab_instance = courses_ui.CoursesUI(self.notebook, self)
        self.students_tab_instance = students_ui.StudentsUI(self.notebook, self)
        self.favorites_tab_instance = favorites_ui.FavoritesUI(self.notebook, self) 

        self.notebook.pack(expand=1, fill='both', padx=5, pady=5)

        
        self._update_student_id_map()
        self._update_course_id_map()
        
        self.populate_all_favorites_comboboxes()


    def _logout(self):
        """Обрабатывает выход пользователя."""
        self.current_user = None
        if self.main_app_frame and self.main_app_frame.winfo_exists():
            self.main_app_frame.destroy()
            self.main_app_frame = None 
        
        
        self.courses_tab_instance = None
        self.students_tab_instance = None
        self.favorites_tab_instance = None
        self.notebook = None 

        
        self.student_name_to_id.clear()
        self.course_title_to_id.clear()

        
        auth_callbacks = {'on_login_success': self._on_login_success}
        self.auth_interface = auth_ui.AuthUI(self.root, auth_callbacks)

    

    def _update_student_id_map(self):
        """Обновляет словарь self.student_name_to_id."""
        self.student_name_to_id.clear()
        students = db_manager.get_all_students_db() 
        for s in students:
            name_display = f"{s['name']} (ID: {s['student_id']})"
            self.student_name_to_id[name_display] = s['student_id']

    def _update_course_id_map(self):
        """Обновляет словарь self.course_title_to_id."""
        self.course_title_to_id.clear()
        courses = db_manager.get_all_courses_db() 
        for c in courses:
            title_display = f"{c['title']} (ID: {c['course_id']})"
            self.course_title_to_id[title_display] = c['course_id']

    def populate_all_favorites_comboboxes(self):
        """
        Вызывается из CoursesUI и StudentsUI после обновления их списков,
        чтобы обновить комбобоксы на вкладке FavoritesUI.
        """
        self._update_student_id_map() 
        self._update_course_id_map()
        if self.favorites_tab_instance:
            self.favorites_tab_instance.populate_comboboxes()

    def refresh_favorites_tab_data(self):
        """
        Вызывается, когда нужно полностью обновить данные на вкладке "Избранное"
        (например, после удаления студента или курса).
        """
        
        self._update_student_id_map()
        self._update_course_id_map()
        if self.favorites_tab_instance:
            self.favorites_tab_instance.refresh_favorites_list() 



if __name__ == "__main__":
    root_tk = tk.Tk()
    app = OnlineSchoolApp(root_tk)
    root_tk.mainloop()