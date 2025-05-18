import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar
import os
from datetime import datetime
import subprocess

# Путь к Hugo-сайту (текущая директория)
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

        git_commit_and_push(f"Добавлен пост: {title}")
        subprocess.run(["hugo"], check=True)

        messagebox.showinfo("Успех", f"Пост '{title}' создан и задеплоен!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def git_commit_and_push(message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)

def open_post_manager():
    files = [f for f in os.listdir(POSTS_FOLDER) if f.endswith(".md")]
    if not files:
        messagebox.showinfo("Нет постов", "В папке постов ничего нет.")
        return

    def load_content(event):
        selection = listbox.curselection()
        if not selection:
            return
        file = files[selection[0]]
        path = os.path.join(POSTS_FOLDER, file)
        with open(path, "r", encoding="utf-8") as f:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, f.read())

    def save_changes():
        selection = listbox.curselection()
        if not selection:
            return
        file = files[selection[0]]
        path = os.path.join(POSTS_FOLDER, file)
        new_content = text_area.get("1.0", tk.END).strip()
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        git_commit_and_push(f"Обновлён пост: {file}")
        subprocess.run(["hugo"], check=True)
        messagebox.showinfo("Успех", f"Изменения в '{file}' сохранены и запушены.")

    def delete_post():
        selection = listbox.curselection()
        if not selection:
            return
        file = files[selection[0]]
        path = os.path.join(POSTS_FOLDER, file)
        confirm = messagebox.askyesno("Подтверждение", f"Удалить пост '{file}'?")
        if confirm:
            os.remove(path)
            git_commit_and_push(f"Удалён пост: {file}")
            subprocess.run(["hugo"], check=True)
            messagebox.showinfo("Удалено", f"Пост '{file}' удалён.")
            post_window.destroy()

    post_window = tk.Toplevel(root)
    post_window.title("Управление постами")

    left_frame = tk.Frame(post_window)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    listbox = Listbox(left_frame, width=40)
    listbox.pack(side=tk.LEFT, fill=tk.Y)
    scrollbar = Scrollbar(left_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    for f in files:
        listbox.insert(tk.END, f)

    listbox.bind("<<ListboxSelect>>", load_content)

    right_frame = tk.Frame(post_window)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    text_area = tk.Text(right_frame, wrap=tk.WORD, width=80, height=30)
    text_area.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(right_frame)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Сохранить изменения", command=save_changes).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить пост", command=delete_post).pack(side=tk.LEFT, padx=5)

# GUI
root = tk.Tk()
root.title("Hugo Пост-Менеджер")

tk.Label(root, text="Заголовок поста:").pack()
title_entry = tk.Entry(root, width=50)
title_entry.pack()

tk.Label(root, text="Текст поста (Markdown):").pack()
content_text = tk.Text(root, width=60, height=15)
content_text.pack()

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Создать и задеплоить", command=create_post).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Управление постами", command=open_post_manager).grid(row=0, column=1, padx=5)

root.mainloop()
