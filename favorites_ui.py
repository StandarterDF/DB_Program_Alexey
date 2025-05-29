

import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as db_manager 

class FavoritesUI:
    def __init__(self, parent_notebook, app_instance):
        """
        Инициализирует UI для вкладки "Избранное и Лайки".
        :param parent_notebook: ttk.Notebook, в который будет добавлена эта вкладка.
        :param app_instance: Экземпляр основного класса приложения (OnlineSchoolApp)
                              для доступа к общим данным и методам (например, словарям ID).
        """
        self.app_instance = app_instance
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text='Избранное и Лайки')

        
        self.sort_column_idx = 0 
        self.sort_order_asc = True
        
        
        self.selected_fav_student_id = None
        self.selected_fav_course_id = None

        
        self.tree_display_columns = ("student", "course", "is_favorite", "likes")
        self.tree_column_display_texts = {
            "student": "Студент", 
            "course": "Курс", 
            "is_favorite": "В избранном?", 
            "likes": "Лайки"
        }
        
        self.tree_all_columns = self.tree_display_columns + ("student_id", "course_id")


        self._setup_widgets()
        self.populate_comboboxes() 
        self.refresh_favorites_list()

    def _setup_widgets(self):
        
        add_update_frame = ttk.LabelFrame(self.frame, text="Управление избранным (добавить/изменить статус)")
        add_update_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(add_update_frame, text="Студент*:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(add_update_frame, textvariable=self.student_var, state="readonly", width=38)
        self.student_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(add_update_frame, text="Курс*:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(add_update_frame, textvariable=self.course_var, state="readonly", width=38)
        self.course_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.is_favorite_var = tk.BooleanVar(value=False) 
        fav_check_frame = ttk.Frame(add_update_frame)
        fav_check_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.is_favorite_check = ttk.Checkbutton(fav_check_frame, text="В избранном?", variable=self.is_favorite_var)
        self.is_favorite_check.pack(side=tk.LEFT)
        
        add_update_frame.columnconfigure(1, weight=1)

        fav_button_frame = ttk.Frame(add_update_frame)
        fav_button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(fav_button_frame, text="Добавить/Обновить статус", command=self.add_or_update_favorite_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(fav_button_frame, text="Очистить поля выше", command=self.clear_add_form_fields).pack(side=tk.LEFT, padx=5)

        
        list_likes_frame = ttk.LabelFrame(self.frame, text="Список избранного и управление лайками")
        list_likes_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.favorites_tree = ttk.Treeview(list_likes_frame, columns=self.tree_all_columns, show="headings")

        for i, col_id in enumerate(self.tree_display_columns): 
            text = self.tree_column_display_texts[col_id]
            self.favorites_tree.heading(col_id, text=text, command=lambda c_idx=i: self._sort_by_column(c_idx))
        
        
        self.favorites_tree.heading("student_id", text="Student ID")
        self.favorites_tree.heading("course_id", text="Course ID")

        self.favorites_tree.column("student", width=180)
        self.favorites_tree.column("course", width=180)
        self.favorites_tree.column("is_favorite", width=100, anchor="center")
        self.favorites_tree.column("likes", width=70, anchor="center")
        self.favorites_tree.column("student_id", width=0, stretch=tk.NO, minwidth=0) 
        self.favorites_tree.column("course_id", width=0, stretch=tk.NO, minwidth=0)

        self.favorites_tree.pack(side=tk.LEFT, padx=5, pady=5, fill="both", expand=True)
        self.favorites_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        fav_tree_scrollbar_y = ttk.Scrollbar(list_likes_frame, orient="vertical", command=self.favorites_tree.yview)
        fav_tree_scrollbar_y.pack(side=tk.LEFT, fill='y')
        self.favorites_tree.configure(yscrollcommand=fav_tree_scrollbar_y.set)

        
        likes_control_frame = ttk.Frame(list_likes_frame)
        likes_control_frame.pack(side=tk.LEFT, padx=10, fill="y", anchor="n")
        ttk.Button(likes_control_frame, text="👍 Лайк (+1)", command=lambda: self.change_likes(1)).pack(pady=5, fill="x")
        ttk.Button(likes_control_frame, text="👎 Дизлайк (-1)", command=lambda: self.change_likes(-1)).pack(pady=5, fill="x")
        ttk.Separator(likes_control_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(likes_control_frame, text="Удалить из избранного", command=self.delete_favorite, style="Danger.TButton").pack(pady=5, fill="x")
        
        
        style = ttk.Style()
        style.configure("Danger.TButton", foreground="red", font=('Arial', 10, 'bold'))
        
        bottom_button_frame = ttk.Frame(self.frame)
        bottom_button_frame.pack(pady=5, fill="x", padx=10)
        ttk.Button(bottom_button_frame, text="Обновить весь список", command=self.refresh_favorites_list).pack(side=tk.RIGHT, padx=5)

    def _sort_by_column(self, column_idx):
        """Обрабатывает клик по заголовку для сортировки."""
        if self.sort_column_idx == column_idx:
            self.sort_order_asc = not self.sort_order_asc
        else:
            self.sort_column_idx = column_idx
            self.sort_order_asc = True
        self.refresh_favorites_list()

    def populate_comboboxes(self):
        """Заполняет комбобоксы студентов и курсов."""
        
        
        
        
        current_student_selection = self.student_var.get()
        current_course_selection = self.course_var.get()

        student_names = [""] + sorted(list(self.app_instance.student_name_to_id.keys()))
        self.student_combo['values'] = student_names
        if current_student_selection in student_names:
            self.student_combo.set(current_student_selection)
        elif student_names:
            self.student_combo.current(0)

        course_titles = [""] + sorted(list(self.app_instance.course_title_to_id.keys()))
        self.course_combo['values'] = course_titles
        if current_course_selection in course_titles:
            self.course_combo.set(current_course_selection)
        elif course_titles:
            self.course_combo.current(0)

    def add_or_update_favorite_status(self):
        """Добавляет новую запись в избранное или обновляет статус is_favorite существующей."""
        student_name_selected = self.student_var.get()
        course_title_selected = self.course_var.get()

        if not student_name_selected or not course_title_selected or student_name_selected == "" or course_title_selected == "":
            messagebox.showerror("Ошибка валидации", "Необходимо выбрать студента и курс.", parent=self.frame)
            return

        student_id = self.app_instance.student_name_to_id.get(student_name_selected)
        course_id = self.app_instance.course_title_to_id.get(course_title_selected)

        if student_id is None or course_id is None:
            messagebox.showerror("Ошибка", "Не удалось определить ID студента или курса.\nВозможно, списки устарели. Обновите их на соответствующих вкладках.", parent=self.frame)
            return
            
        is_favorite_val = self.is_favorite_var.get()
        
        current_likes = 0 
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT likes FROM favorites WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        existing_fav = cursor.fetchone()
        conn.close()
        
        if existing_fav:
            current_likes = existing_fav['likes'] 

        if db_manager.add_or_update_favorite_db(student_id, course_id, is_favorite_val, current_likes):
            action = "статус обновлен" if existing_fav else "добавлена"
            messagebox.showinfo("Успех", f"Запись в избранном {action}.", parent=self.frame)
            self.refresh_favorites_list()
            
            self.is_favorite_var.set(False) 
        

    def refresh_favorites_list(self):
        """Обновляет список избранного в Treeview."""
        for i in self.favorites_tree.get_children():
            self.favorites_tree.delete(i)
        
        sort_order_str = "ASC" if self.sort_order_asc else "DESC"
        favorites_data = db_manager.get_all_favorites_db(
            sort_by_col_index=self.sort_column_idx, 
            sort_order=sort_order_str
        )
        for fav_row in favorites_data:
            is_fav_display = "Да" if fav_row['is_favorite'] else "Нет"
            values_to_insert = (
                fav_row['student_name'], fav_row['course_title'], 
                is_fav_display, fav_row['likes'],
                fav_row['student_id'], fav_row['course_id'] 
            )
            self.favorites_tree.insert("", "end", values=values_to_insert)
        
        
        self.selected_fav_student_id = None 
        self.selected_fav_course_id = None

    def on_tree_select(self, event):
        """Обрабатывает выбор строки в Treeview (для лайков и удаления)."""
        selected_item_iid = self.favorites_tree.focus()
        if not selected_item_iid:
            self.selected_fav_student_id = None
            self.selected_fav_course_id = None
            return

        item_values = self.favorites_tree.item(selected_item_iid, 'values')
        if item_values and len(item_values) == len(self.tree_all_columns):
            student_id_idx = self.tree_all_columns.index("student_id")
            course_id_idx = self.tree_all_columns.index("course_id")
            self.selected_fav_student_id = item_values[student_id_idx]
            self.selected_fav_course_id = item_values[course_id_idx]
            
            
            
            student_name_display = ""
            for name, sid in self.app_instance.student_name_to_id.items():
                if sid == self.selected_fav_student_id:
                    student_name_display = name
                    break
            self.student_var.set(student_name_display)

            course_title_display = ""
            for title, cid in self.app_instance.course_title_to_id.items():
                if cid == self.selected_fav_course_id:
                    course_title_display = title
                    break
            self.course_var.set(course_title_display)
            
            is_fav_idx = self.tree_all_columns.index("is_favorite")
            self.is_favorite_var.set(item_values[is_fav_idx] == "Да")

        else:
            self.selected_fav_student_id = None
            self.selected_fav_course_id = None


    def change_likes(self, amount):
        """Изменяет количество лайков для выбранной записи."""
        if self.selected_fav_student_id is None or self.selected_fav_course_id is None:
            messagebox.showwarning("Лайки", "Сначала выберите запись в списке избранного.", parent=self.frame)
            return

        current_likes = 0
        selected_item_iid = self.favorites_tree.focus()
        if selected_item_iid:
            item_values = self.favorites_tree.item(selected_item_iid)['values']
            likes_idx = self.tree_all_columns.index("likes")
            if item_values and len(item_values) > likes_idx:
                try:
                    current_likes = int(item_values[likes_idx])
                except (ValueError, TypeError):
                    pass 
        
        new_likes = max(0, current_likes + amount)

        if db_manager.update_favorite_likes_db(self.selected_fav_student_id, self.selected_fav_course_id, new_likes):
            if selected_item_iid: 
                current_row_values = list(self.favorites_tree.item(selected_item_iid, 'values'))
                current_row_values[likes_idx] = new_likes
                self.favorites_tree.item(selected_item_iid, values=tuple(current_row_values))
        

    def delete_favorite(self):
        """Удаляет выбранную запись из избранного."""
        if self.selected_fav_student_id is None or self.selected_fav_course_id is None:
            messagebox.showerror("Ошибка", "Сначала выберите запись для удаления из списка.", parent=self.frame)
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись из избранного?", parent=self.frame):
            if db_manager.delete_favorite_db(self.selected_fav_student_id, self.selected_fav_course_id):
                messagebox.showinfo("Успех", "Запись из избранного успешно удалена.", parent=self.frame)
                self.refresh_favorites_list() 
                self.clear_add_form_fields() 
            

    def clear_add_form_fields(self):
        """Очищает поля формы добавления/обновления статуса избранного."""
        if self.student_combo['values']: 
            try: self.student_combo.current(0) 
            except tk.TclError: self.student_var.set("")
        else: self.student_var.set("")
        
        if self.course_combo['values']:
            try: self.course_combo.current(0)
            except tk.TclError: self.course_var.set("")
        else: self.course_var.set("")
        self.is_favorite_var.set(False)
        
        


if __name__ == '__main__':
    
    root_test = tk.Tk()
    root_test.title("Тест вкладки Избранное")
    root_test.geometry("900x600")

    db_manager.init_db()

    
    class MockApp:
        def __init__(self):
            self.student_name_to_id = {} 
            self.course_title_to_id = {} 
            self._populate_mock_data()

        def _populate_mock_data(self):
            
            if not db_manager.get_all_students_db():
                db_manager.add_student_db("Тест Студент 1", "test1@example.com")
                db_manager.add_student_db("Тест Студент 2", "test2@example.com")
            if not db_manager.get_all_courses_db():
                db_manager.add_course_db("Тест Курс A", "Описание А", "Лектор А", "Начальный", "")
                db_manager.add_course_db("Тест Курс B", "Описание Б", "Лектор Б", "Средний", "")

            students = db_manager.get_all_students_db()
            for s in students:
                name_display = f"{s['name']} (ID: {s['student_id']})"
                self.student_name_to_id[name_display] = s['student_id']

            courses = db_manager.get_all_courses_db()
            for c in courses:
                title_display = f"{c['title']} (ID: {c['course_id']})"
                self.course_title_to_id[title_display] = c['course_id']
        
        
        def populate_all_favorites_comboboxes(self):
            if hasattr(self, 'favorites_ui_instance') and self.favorites_ui_instance:
                print("MockApp: favorites_ui_instance.populate_comboboxes() called")
                self.favorites_ui_instance.populate_comboboxes()

    mock_app_instance = MockApp()

    test_notebook = ttk.Notebook(root_test)
    
    favorites_tab_ui = FavoritesUI(test_notebook, mock_app_instance)
    mock_app_instance.favorites_ui_instance = favorites_tab_ui 

    test_notebook.pack(expand=1, fill='both')
    
    root_test.mainloop()