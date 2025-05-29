import re
from tkinter import messagebox

def validate_email(email_string):
    """
    Проверяет строку на соответствие базовому формату email.
    Возвращает True, если валидно, иначе False и показывает messagebox.
    """
    if re.match(r"[^@]+@[^@]+\.[^@]+", email_string):
        return True
    messagebox.showerror("Ошибка валидации", "Некорректный формат Email.")
    return False

def validate_youtube_link(link_string):
    """
    Проверяет, что ссылка на YouTube (если указана) содержит 'youtube.com/' или 'youtu.be/'.
    Возвращает True, если валидно или пусто, иначе False и показывает messagebox.
    """
    if not link_string: 
        return True
    if "youtube.com/" in link_string or "youtu.be/" in link_string:
        return True
    messagebox.showerror("Ошибка валидации", "Ссылка на YouTube должна содержать 'youtube.com/' или 'youtu.be/'.")
    return False

def make_text_widget_clipboard_aware(text_widget):
    """
    Обеспечивает стандартные операции буфера обмена для tk.Text виджета.
    В большинстве современных Tkinter это работает "из коробки",
    но функция оставлена для совместимости или если возникнут проблемы.
    Также добавляет undo=True.
    """
    text_widget.config(undo=True) 
    pass 




if __name__ == '__main__':
    print(f"Валидация 'test@example.com': {validate_email('test@example.com')}") 
    print(f"Валидация 'testexample.com': {validate_email('testexample.com')}") 
    print(f"Валидация YouTube 'https://www.youtube.com/watch?v=...': {validate_youtube_link('https://www.youtube.com/watch?v=...')}") 
    print(f"Валидация YouTube 'https://youtu.be/...': {validate_youtube_link('https://youtu.be/...')}") 
    print(f"Валидация YouTube 'https://example.com': {validate_youtube_link('https://example.com')}") 
    print(f"Валидация YouTube '': {validate_youtube_link('')}") 