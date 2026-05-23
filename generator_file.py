import random
import csv
import os
import time
from tkinter import Label
# from web import root, status_lbl
title = ["Хроники лунной пыли",
         "Тени прошлого",
         "Империя стекла",
         "Секрет третьего ключа",
         "Искусство войны в офисе",
         "Путешествие к центру разума",
         "Драконы мегаполиса",
         "Последний закат человечества"
         ]
genre = ["Фэнтези",
         "Детектив",
         "Научная фантастика",
         "Романтика",
         "Триллер",
         "Бизнес"]
author = [
    "Олег Северов",
    "Анна Краснова",
    "Виктор Гром",
    "София Мелоди",
    "Максим Шифр",
    "Петр Деловой",
]



def generation_csv(root, listbox):
    status_lbl = Label(root, text="Загрузка 0%",
                       font=("Arial", 11),
                       bg="#1e1e2e", fg="#ffffff")

    status_lbl.place(x=220, y=640)

    CHECK_INTERVAL = 85_000
    TARGET_BYTES = 1_073_741_824
    percent = 0
    with open("books.csv", "w", encoding = "utf-8-sig", newline = "") as file:
    
        writer = csv.writer(file)
        writer.writerow(["Book_ID", "Title", "Author", "Genre", "Year", "Pages", "Rating", "Is_read"])
    
        cnt = 0
        while True:
            rating = round(random.uniform(1, 5), 1)
            year = random.randint(1800, 2026)
            title_book = random.choice(title)
            author_book = random.choice(author)
            genre_book = random.choice(genre)
            book_id = random.randint(1000, 9999)
            pages = random.randint(40, 1000)
            is_read = random.choice([1, 0])
            writer.writerow([book_id, title_book, author_book, genre_book, year, pages, rating, is_read])
            cnt += 1
    
            if cnt % CHECK_INTERVAL == 0:
                current_size = os.fstat(file.fileno()).st_size
                percent = min(int((current_size / TARGET_BYTES) * 100), 100)
                status_lbl.config(text=f"Загрузка {percent}%")
                root.update()
                print(percent)
                file.flush()
                if os.fstat(file.fileno()).st_size >= TARGET_BYTES:
                    break

    status_lbl.config(text=f"Генерация завершена!")  # ✅ Обновляем существующий Label
    root.update()
    size = os.path.getsize("C:\\Users\\User\\Desktop\\PythonProject\\books.csv")
    avg_record = (size - 100) / 1000
    print(f"{avg_record:.2f}")

    with open("books.csv", "r", encoding = "utf-8-sig") as file:

        reader = csv.reader(file)
        next(reader)  # пропуск заголовка
        for i, row in enumerate(reader):
            if i >= 15:
                break

            listbox.insert("end", "|".join(row))

    # print(f"Записей для 1 ГБ: {1_000_000_000 / avg_record:,.0f}")



print(time.time())
# for _ in range()
# with open("Л5.csv", "w", encoding = "utf-8") as file:
#     file.write(f"")

