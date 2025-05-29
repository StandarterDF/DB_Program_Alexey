

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import database_manager as db_manager 
from utils import validate_youtube_link, make_text_widget_clipboard_aware 

class CoursesUI:
    def __init__(self, parent_notebook, app_instance):
        """
        Инициализирует UI для вкладки "Курсы".
        :param parent_notebook: ttk.Notebook, в который будет добавлена эта вкладка.
        :param app_instance: Экземпляр основного класса приложения (OnlineSchoolApp)
                              для доступа к общим методам, таким как обновление других вкладок.
        """
        self.app_instance = app_instance 
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text='Курсы')

        
        self.sort_column = 'title'
        self.sort_order_asc = True
        self.current_search_term = None
        self.selected_course_id = None

        
        self.column_map = {
            "id": "course_id", 
            "title": "title", 
            "instructor": "instructor_name", 
            "level": "level"
            
        }
        
        self.tree_columns_ordered = ("id", "title", "description", "instructor", "level", "youtube")


        self._setup_widgets()
        self.refresh_courses_list()

    def _setup_widgets(self):
        
        input_frame = ttk.LabelFrame(self.frame, text="Данные курса")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Название*:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=50)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.description_text = tk.Text(input_frame, width=48, height=4, wrap=tk.WORD)
        make_text_widget_clipboard_aware(self.description_text) 
        self.description_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        desc_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.description_text.yview)
        desc_scrollbar.grid(row=1, column=2, sticky="ns")
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)

        ttk.Label(input_frame, text="Преподаватель:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.instructor_entry = ttk.Entry(input_frame, width=50)
        self.instructor_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Уровень:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.level_var = tk.StringVar()
        self.level_combo = ttk.Combobox(input_frame, textvariable=self.level_var,
                                        values=["Начальный", "Средний", "Продвинутый"], state="readonly")
        self.level_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.level_combo.set("Начальный")

        ttk.Label(input_frame, text="YouTube ссылка:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.youtube_entry = ttk.Entry(input_frame, width=50)
        self.youtube_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        input_frame.columnconfigure(1, weight=1)

        
        crud_button_frame = ttk.Frame(self.frame)
        crud_button_frame.pack(pady=5, fill="x", padx=10)
        ttk.Button(crud_button_frame, text="Добавить", command=self.add_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(crud_button_frame, text="Обновить", command=self.update_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(crud_button_frame, text="Удалить", command=self.delete_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(crud_button_frame, text="Очистить поля", command=self.clear_input_fields).pack(side=tk.LEFT, padx=5)
        
        
        search_refresh_frame = ttk.Frame(self.frame)
        search_refresh_frame.pack(pady=5, fill="x", padx=10)
        ttk.Label(search_refresh_frame, text="Поиск по названию:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_refresh_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_refresh_frame, text="Найти", command=self.perform_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_refresh_frame, text="Показать все", command=self.show_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_refresh_frame, text="Обновить список", command=self.refresh_courses_list).pack(side=tk.RIGHT, padx=5)

        
        self.courses_tree = ttk.Treeview(self.frame, columns=self.tree_columns_ordered, show="headings")
        
        
        for col_id in self.tree_columns_ordered:
            text = col_id.replace("_", " ").title()
            if col_id == "id": text = "ID"
            if col_id == "instructor": text = "Преподаватель" 

            if col_id in self.column_map: 
                db_col_name = self.column_map[col_id]
                self.courses_tree.heading(col_id, text=text, command=lambda c=db_col_name: self._sort_by_column(c))
            else: 
                 self.courses_tree.heading(col_id, text=text)
        
        self.courses_tree.column("id", width=40, stretch=tk.NO, anchor="center")
        self.courses_tree.column("title", width=200)
        self.courses_tree.column("description", width=250)
        self.courses_tree.column("instructor", width=150)
        self.courses_tree.column("level", width=100, anchor="center")
        self.courses_tree.column("youtube", width=200)

        self.courses_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.courses_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.courses_tree.bind("<Double-1>", self.on_tree_double_click)

        
        tree_scrollbar_y = ttk.Scrollbar(self.courses_tree, orient="vertical", command=self.courses_tree.yview)
        tree_scrollbar_y.pack(side='right', fill='y')
        self.courses_tree.configure(yscrollcommand=tree_scrollbar_y.set)
        
        tree_scrollbar_x = ttk.Scrollbar(self.courses_tree, orient="horizontal", command=self.courses_tree.xview)
        tree_scrollbar_x.pack(side='bottom', fill='x')
        self.courses_tree.configure(xscrollcommand=tree_scrollbar_x.set)

    def _sort_by_column(self, column_name_db):
        """Обрабатывает клик по заголовку для сортировки."""
        if self.sort_column == column_name_db:
            self.sort_order_asc = not self.sort_order_asc
        else:
            self.sort_column = column_name_db
            self.sort_order_asc = True
        self.refresh_courses_list()

    def refresh_courses_list(self):
        """Обновляет список курсов в Treeview."""
        for i in self.courses_tree.get_children():
            self.courses_tree.delete(i)
        
        sort_order_str = "ASC" if self.sort_order_asc else "DESC"
        courses_data = db_manager.get_all_courses_db(
            search_term=self.current_search_term,
            sort_by=self.sort_column,
            sort_order=sort_order_str
        )
        for course in courses_data:
            
            values_to_insert = (
                course['course_id'],
                course['title'],
                course['description'],
                course['instructor_name'],
                course['level'],
                course['youtube_link']
            )
            self.courses_tree.insert("", "end", values=values_to_insert)
            
        
        if hasattr(self.app_instance, 'populate_all_favorites_comboboxes'):
             self.app_instance.populate_all_favorites_comboboxes()


    def add_course(self):
        title = self.title_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        instructor = self.instructor_entry.get()
        level = self.level_var.get()
        youtube_link = self.youtube_entry.get().strip()

        if not title:
            messagebox.showerror("Ошибка валидации", "Название курса обязательно для заполнения.", parent=self.frame)
            return
        if not validate_youtube_link(youtube_link): 
            return

        if db_manager.add_course_db(title, description, instructor, level, youtube_link):
            messagebox.showinfo("Успех", "Курс успешно добавлен.", parent=self.frame)
            self.current_search_term = None 
            self.search_entry.delete(0, tk.END)
            self.refresh_courses_list()
            self.clear_input_fields()
        

    def update_course(self):
        if self.selected_course_id is None:
            messagebox.showerror("Ошибка", "Сначала выберите курс для обновления.", parent=self.frame)
            return

        title = self.title_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        instructor = self.instructor_entry.get()
        level = self.level_var.get()
        youtube_link = self.youtube_entry.get().strip()

        if not title:
            messagebox.showerror("Ошибка валидации", "Название курса обязательно для заполнения.", parent=self.frame)
            return
        if not validate_youtube_link(youtube_link):
            return

        if db_manager.update_course_db(self.selected_course_id, title, description, instructor, level, youtube_link):
            messagebox.showinfo("Успех", "Курс успешно обновлен.", parent=self.frame)
            self.refresh_courses_list()
            self.clear_input_fields()
            self.selected_course_id = None 
        

    def delete_course(self):
        if self.selected_course_id is None:
            messagebox.showerror("Ошибка", "Сначала выберите курс для удаления.", parent=self.frame)
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот курс?\nЭто также удалит все связанные записи в 'Избранном'.", parent=self.frame):
            if db_manager.delete_course_db(self.selected_course_id):
                messagebox.showinfo("Успех", "Курс успешно удален.", parent=self.frame)
                self.refresh_courses_list()
                
                if hasattr(self.app_instance, 'refresh_favorites_tab_data'):
                    self.app_instance.refresh_favorites_tab_data()
                self.clear_input_fields()
                self.selected_course_id = None
            

    def clear_input_fields(self):
        self.title_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.description_text.edit_reset() 
        self.instructor_entry.delete(0, tk.END)
        self.level_var.set("Начальный")
        self.youtube_entry.delete(0, tk.END)
        self.selected_course_id = None
        if self.courses_tree.focus(): 
            self.courses_tree.selection_remove(self.courses_tree.focus())

    def perform_search(self):
        self.current_search_term = self.search_entry.get().strip()
        self.refresh_courses_list()

    def show_all(self):
        self.current_search_term = None
        self.search_entry.delete(0, tk.END)
        self.refresh_courses_list()

    def on_tree_select(self, event):
        selected_item_iid = self.courses_tree.focus()
        if not selected_item_iid:
            self.selected_course_id = None
            return
        
        item_values = self.courses_tree.item(selected_item_iid, 'values')
        if item_values:
            
            col_order = self.tree_columns_ordered
            self.selected_course_id = item_values[col_order.index("id")]
            
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, item_values[col_order.index("title")])
            
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert("1.0", item_values[col_order.index("description")] or "")
            
            self.instructor_entry.delete(0, tk.END)
            self.instructor_entry.insert(0, item_values[col_order.index("instructor")] or "")
            
            self.level_var.set(item_values[col_order.index("level")] or "Начальный")
            
            self.youtube_entry.delete(0, tk.END)
            self.youtube_entry.insert(0, item_values[col_order.index("youtube")] or "")

    def on_tree_double_click(self, event):
        region = self.courses_tree.identify_region(event.x, event.y)
        if region != "cell": 
            return

        selected_item_iid = self.courses_tree.focus()
        if not selected_item_iid:
            return
        
        
        column_id_str = self.courses_tree.identify_column(event.x) 
        column_index = int(column_id_str.replace("#", "")) -1 
        
        clicked_column_name = self.tree_columns_ordered[column_index]

        if clicked_column_name != "youtube": 
            return

        item_values = self.courses_tree.item(selected_item_iid, 'values')
        youtube_link_value = item_values[self.tree_columns_ordered.index("youtube")]

        if youtube_link_value: 
            try:
                webbrowser.open_new_tab(youtube_link_value)
            except Exception as e:
                messagebox.showerror("Ошибка открытия ссылки", f"Не удалось открыть ссылку: {youtube_link_value}\n{e}", parent=self.frame)
        else:
             messagebox.showinfo("Информация", "Ссылка на YouTube для этого курса не указана.", parent=self.frame)


if __name__ == '__main__':
    
    root_test = tk.Tk()
    root_test.title("Тест вкладки Курсы")
    root_test.geometry("900x600")

    
    db_manager.init_db()

    
    class MockApp:
        def populate_all_favorites_comboboxes(self):
            print("MockApp: populate_all_favorites_comboboxes called")
        def refresh_favorites_tab_data(self):
            print("MockApp: refresh_favorites_tab_data called")

    mock_app_instance = MockApp()

    test_notebook = ttk.Notebook(root_test)
    courses_tab_ui = CoursesUI(test_notebook, mock_app_instance)
    test_notebook.pack(expand=1, fill='both')
    
    root_test.mainloop()