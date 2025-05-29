import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as db_manager 
from utils import validate_email 

class StudentsUI:
    def __init__(self, parent_notebook, app_instance):
        """
        Инициализирует UI для вкладки "Студенты".
        :param parent_notebook: ttk.Notebook, в который будет добавлена эта вкладка.
        :param app_instance: Экземпляр основного класса приложения (OnlineSchoolApp)
                              для доступа к общим методам.
        """
        self.app_instance = app_instance
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text='Студенты')

        
        self.sort_column = 'name' 
        self.sort_order_asc = True
        self.selected_student_id = None

        
        self.column_map = {
            "id": "student_id", 
            "name": "name", 
            "email": "email"
        }
        
        self.tree_columns_ordered = ("id", "name", "email")

        self._setup_widgets()
        self.refresh_students_list()

    def _setup_widgets(self):
        
        input_frame = ttk.LabelFrame(self.frame, text="Данные студента")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Имя*:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Email*:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(input_frame, width=40)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        input_frame.columnconfigure(1, weight=1)

        
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=5, fill="x", padx=10)

        ttk.Button(button_frame, text="Добавить", command=self.add_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.update_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить поля", command=self.clear_input_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить список", command=self.refresh_students_list).pack(side=tk.RIGHT, padx=5)

        
        self.students_tree = ttk.Treeview(self.frame, columns=self.tree_columns_ordered, show="headings")
        
        for col_id in self.tree_columns_ordered:
            text = col_id.replace("_", " ").title()
            if col_id == "id": text = "ID"
            
            db_col_name = self.column_map[col_id] 
            self.students_tree.heading(col_id, text=text, command=lambda c=db_col_name: self._sort_by_column(c))

        self.students_tree.column("id", width=50, stretch=tk.NO, anchor="center")
        self.students_tree.column("name", width=200)
        self.students_tree.column("email", width=250)

        self.students_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.students_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        
        tree_scrollbar_y = ttk.Scrollbar(self.students_tree, orient="vertical", command=self.students_tree.yview)
        tree_scrollbar_y.pack(side='right', fill='y')
        self.students_tree.configure(yscrollcommand=tree_scrollbar_y.set)

    def _sort_by_column(self, column_name_db):
        """Обрабатывает клик по заголовку для сортировки."""
        if self.sort_column == column_name_db:
            self.sort_order_asc = not self.sort_order_asc
        else:
            self.sort_column = column_name_db
            self.sort_order_asc = True
        self.refresh_students_list()

    def refresh_students_list(self):
        """Обновляет список студентов в Treeview."""
        for i in self.students_tree.get_children():
            self.students_tree.delete(i)
        
        sort_order_str = "ASC" if self.sort_order_asc else "DESC"
        students_data = db_manager.get_all_students_db(
            sort_by=self.sort_column,
            sort_order=sort_order_str
        )
        
        for student in students_data:
            values_to_insert = (
                student['student_id'],
                student['name'],
                student['email']
            )
            self.students_tree.insert("", "end", values=values_to_insert)
            
        
        if hasattr(self.app_instance, 'populate_all_favorites_comboboxes'):
             self.app_instance.populate_all_favorites_comboboxes()

    def add_student(self):
        name = self.name_entry.get()
        email = self.email_entry.get()

        if not name or not email:
            messagebox.showerror("Ошибка валидации", "Имя и Email обязательны для заполнения.", parent=self.frame)
            return
        if not validate_email(email): 
            return

        add_result = db_manager.add_student_db(name, email)
        if add_result == True:
            messagebox.showinfo("Успех", "Студент успешно добавлен.", parent=self.frame)
            self.refresh_students_list()
            self.clear_input_fields()
        elif add_result == "integrity_error":
            messagebox.showerror("Ошибка валидации", "Студент с таким Email уже существует.", parent=self.frame)
        

    def update_student(self):
        if self.selected_student_id is None:
            messagebox.showerror("Ошибка", "Сначала выберите студента для обновления.", parent=self.frame)
            return

        name = self.name_entry.get()
        email = self.email_entry.get()

        if not name or not email:
            messagebox.showerror("Ошибка валидации", "Имя и Email обязательны для заполнения.", parent=self.frame)
            return
        if not validate_email(email):
            return

        update_result = db_manager.update_student_db(self.selected_student_id, name, email)
        if update_result == True:
            messagebox.showinfo("Успех", "Данные студента успешно обновлены.", parent=self.frame)
            self.refresh_students_list()
            
            if hasattr(self.app_instance, 'refresh_favorites_tab_data'):
                self.app_instance.refresh_favorites_tab_data()
            self.clear_input_fields()
            self.selected_student_id = None
        elif update_result == "integrity_error":
             messagebox.showerror("Ошибка валидации", "Студент с таким Email уже существует (возможно, вы пытаетесь присвоить email другого студента).", parent=self.frame)
        

    def delete_student(self):
        if self.selected_student_id is None:
            messagebox.showerror("Ошибка", "Сначала выберите студента для удаления.", parent=self.frame)
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого студента?\nЭто также удалит все связанные записи в 'Избранном'.", parent=self.frame):
            if db_manager.delete_student_db(self.selected_student_id):
                messagebox.showinfo("Успех", "Студент успешно удален.", parent=self.frame)
                self.refresh_students_list()
                
                if hasattr(self.app_instance, 'refresh_favorites_tab_data'):
                    self.app_instance.refresh_favorites_tab_data()
                self.clear_input_fields()
                self.selected_student_id = None
            

    def clear_input_fields(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.selected_student_id = None
        if self.students_tree.focus(): 
            self.students_tree.selection_remove(self.students_tree.focus())

    def on_tree_select(self, event):
        selected_item_iid = self.students_tree.focus()
        if not selected_item_iid:
            self.selected_student_id = None
            return

        item_values = self.students_tree.item(selected_item_iid, 'values')
        if item_values:
            col_order = self.tree_columns_ordered
            self.selected_student_id = item_values[col_order.index("id")]
            
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, item_values[col_order.index("name")])
            
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, item_values[col_order.index("email")])

if __name__ == '__main__':
    
    root_test = tk.Tk()
    root_test.title("Тест вкладки Студенты")
    root_test.geometry("700x500")

    db_manager.init_db() 

    class MockApp: 
        def populate_all_favorites_comboboxes(self):
            print("MockApp: populate_all_favorites_comboboxes called for students")
        def refresh_favorites_tab_data(self):
            print("MockApp: refresh_favorites_tab_data called for students")

    mock_app_instance = MockApp()

    test_notebook = ttk.Notebook(root_test)
    students_tab_ui = StudentsUI(test_notebook, mock_app_instance)
    test_notebook.pack(expand=1, fill='both')
    
    root_test.mainloop()