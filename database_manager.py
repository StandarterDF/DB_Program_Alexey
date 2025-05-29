import sqlite3
import hashlib
from tkinter import messagebox 

DB_NAME = 'online_school.db'

def get_db_connection():
    """Устанавливает соединение с БД и включает поддержку внешних ключей."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Инициализирует таблицы в базе данных, если они не существуют."""
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    )''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        instructor_name VARCHAR(100),
        level VARCHAR(50),
        youtube_link VARCHAR(255) 
    )''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    )''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        student_id INTEGER,
        course_id INTEGER,
        is_favorite BOOLEAN DEFAULT FALSE,
        likes INTEGER DEFAULT 0,
        PRIMARY KEY (student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
    )''')
    conn.commit()
    conn.close()


def hash_password_util(password): 
    """Хэширует пароль для сохранения в БД."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user_db(username, password):
    """Добавляет нового пользователя в БД."""
    password_hash = hash_password_util(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        
        
        return "integrity_error" 
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось зарегистрировать пользователя: {e}")
        return False
    finally:
        if conn:
            conn.close()

def check_user_credentials_db(username, password):
    """Проверяет учетные данные пользователя."""
    password_hash_to_check = hash_password_util(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result['password_hash'] == password_hash_to_check:
            return True
        return False
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Ошибка при проверке учетных данных: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_course_db(title, description, instructor, level, youtube_link):
    """Добавляет новый курс в БД."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO courses (title, description, instructor_name, level, youtube_link)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, description, instructor, level, youtube_link))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось добавить курс: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_courses_db(search_term=None, sort_by='title', sort_order='ASC'):
    """Получает все курсы из БД с возможностью поиска и сортировки."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    valid_sort_columns = ['course_id', 'title', 'instructor_name', 'level']
    if sort_by not in valid_sort_columns:
        sort_by = 'title' 
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'ASC'

    query = f"SELECT course_id, title, description, instructor_name, level, youtube_link FROM courses"
    params = []
    if search_term:
        query += " WHERE title LIKE ?"
        params.append(f"%{search_term}%")
    
    query += f" ORDER BY {sort_by} {sort_order.upper()}"
    
    cursor.execute(query, params)
    courses = cursor.fetchall()
    conn.close()
    return courses

def update_course_db(course_id, title, description, instructor, level, youtube_link):
    """Обновляет данные курса в БД."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE courses
        SET title = ?, description = ?, instructor_name = ?, level = ?, youtube_link = ?
        WHERE course_id = ?
        ''', (title, description, instructor, level, youtube_link, course_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось обновить курс: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_course_db(course_id):
    """Удаляет курс из БД."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось удалить курс: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_student_db(name, email):
    """Добавляет нового студента в БД."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        
        return "integrity_error" 
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось добавить студента: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_students_db(sort_by='name', sort_order='ASC'):
    """Получает всех студентов из БД с возможностью сортировки."""
    conn = get_db_connection()
    cursor = conn.cursor()
    valid_sort_columns = ['student_id', 'name', 'email']
    if sort_by not in valid_sort_columns:
        sort_by = 'name'
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'ASC'
        
    query = f"SELECT student_id, name, email FROM students ORDER BY {sort_by} {sort_order.upper()}"
    cursor.execute(query)
    students = cursor.fetchall()
    conn.close()
    return students

def update_student_db(student_id, name, email):
    """Обновляет данные студента в БД."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET name = ?, email = ? WHERE student_id = ?", (name, email, student_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        
        return "integrity_error"
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось обновить студента: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_student_db(student_id):
    """Удаляет студента из БД."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось удалить студента: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_or_update_favorite_db(student_id, course_id, is_favorite, likes):
    """Добавляет или обновляет запись в избранном."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO favorites (student_id, course_id, is_favorite, likes)
        VALUES (?, ?, ?, ?)
        ''', (student_id, course_id, is_favorite, likes))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось добавить/обновить избранное: {e}")
        return False
    finally:
        if conn:
            conn.close()
            
def update_favorite_likes_db(student_id, course_id, new_likes_count):
    """Обновляет количество лайков для записи в избранном."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE favorites
        SET likes = ?
        WHERE student_id = ? AND course_id = ?
        ''', (new_likes_count, student_id, course_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось обновить лайки: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_favorites_db(sort_by_col_index=0, sort_order='ASC'):
    """Получает все записи из избранного с возможностью сортировки."""
    sort_map = {
        0: "s.name",        
        1: "c.title",       
        2: "f.is_favorite", 
        3: "f.likes"        
    }
    sort_column_sql = sort_map.get(sort_by_col_index, "s.name") 
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'ASC'
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f'''
    SELECT s.name AS student_name, c.title AS course_title,
           f.is_favorite, f.likes, f.student_id, f.course_id
    FROM favorites f
    JOIN students s ON f.student_id = s.student_id
    JOIN courses c ON f.course_id = c.course_id
    ORDER BY {sort_column_sql} {sort_order.upper()}
    '''
    cursor.execute(query)
    favorites = cursor.fetchall()
    conn.close()
    return favorites

def delete_favorite_db(student_id, course_id):
    """Удаляет запись из избранного."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM favorites WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось удалить из избранного: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    
    print("Инициализация базы данных...")
    init_db()
    print("База данных готова (или уже существовала).")