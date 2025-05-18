import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar
import os
from datetime import datetime
import subprocess

# Путь к текущей директории (где находится Hugo-сайт)
HUGO_SITE_PATH = os.getcwd()
POSTS_FOLDER = os.path.join(HUGO_SITE_PATH, "content/posts")

def create_post():
    title = title_entry.get().strip()
    content = content_text.get("1.0", tk.END).strip()

    if not title or not content:
        messagebox.showwarning("Ошибка", "Пожалуйста, заполните заголовок и текст поста.")
        return

    filename = title.lower().replace(" ", "-") + ".md"
    filepath = os.path.join(POSTS_FOLDER, filename)
    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    front_matter = f"""---
title: "{title}"
date: {date_str}
draft: false
---

{content}
"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter)

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Добавлен пост: {title}"], check=True)
        subprocess.run(["git", "push"], check=True)
        subprocess.run(["hugo"], check=True)

        messagebox.showinfo("Успех", f"Пост '{title}' создан и запушен!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def delete_post():
    # Получаем список файлов в папке постов
    files = [f for f in os.listdir(POSTS_FOLDER) if f.endswith(".md")]

    if not files:
        messagebox.showinfo("Нет постов", "В папке постов ничего нет.")
        return

    # Окно выбора поста
    def confirm_delete():
        selection = listbox.curselection()
        if not selection:
            return
        file_to_delete = files[selection[0]]
        full_path = os.path.join(POSTS_FOLDER, file_to_delete)

        try:
            os.remove(full_path)
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Удалён пост: {file_to_delete}"], check=True)
            subprocess.run(["git", "push"], check=True)
            subprocess.run(["hugo"], check=True)
            messagebox.showinfo("Успех", f"Пост '{file_to_delete}' удалён.")
            delete_window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # Создаём отдельное окно для выбора
    delete_window = tk.Toplevel(root)
    delete_window.title("Удалить пост")

    listbox = Listbox(delete_window, width=50)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for f in files:
        listbox.insert(tk.END, f)

    scrollbar = Scrollbar(delete_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    tk.Button(delete_window, text="Удалить выбранный пост", command=confirm_delete).pack(pady=5)

# GUI
root = tk.Tk()
root.title("Hugo Пост-Менеджер")

tk.Label(root, text="Заголовок поста:").pack()
title_entry = tk.Entry(root, width=50)
title_entry.pack()

tk.Label(root, text="Текст поста (Markdown):").pack()
content_text = tk.Text(root, width=60, height=20)
content_text.pack()

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Создать и задеплоить", command=create_post).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Удалить пост", command=delete_post).grid(row=0, column=1, padx=5)

root.mainloop()
