import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import psycopg2
import pandas as pd
import re

# Файл для сохранения настроек
CONFIG_FILE = "db_config.json"
# Максимальное количество строк в одном файле
MAX_ROWS_PER_FILE = 1000000

def load_config():
    """Загружает сохранённые настройки из файла."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    """Сохраняет настройки в файл."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def fetch_tables(conn):
    """Получает список таблиц из базы данных."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
        """)
        return [table[0] for table in cur.fetchall()]

def fetch_columns_and_metadata(conn, table_names):
    """Получает метаданные для указанных таблиц."""
    all_data = []
    with conn.cursor() as cur:
        for table_name in table_names:
            cur.execute(f"""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}';
            """)
            columns = cur.fetchall()

            for col in columns:
                column_name, data_type, char_len, nullable = col
                example_query = f"SELECT {column_name} FROM {table_name} LIMIT 1;"
                cur.execute(example_query)
                example_value = cur.fetchone()[0] if cur.rowcount > 0 else None

                all_data.append({
                    'Таблица': table_name,
                    'Имя столбца': column_name,
                    'Тип данных': data_type,
                    'Максимальная длина': char_len if char_len else "",
                    'Может быть NULL': nullable,
                    'Пример данных': str(example_value) if example_value is not None else "",
                })
    return all_data

def parse_dump_file(dump_path):
    """Парсит SQL-дамп и извлекает структуру таблиц."""
    all_data = []
    table_name = None
    in_table_definition = False

    with open(dump_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Поиск создания таблицы
            create_table_match = re.match(r'CREATE TABLE (`?)(\w+)\1\s*\((.*)', line, re.IGNORECASE)
            if create_table_match:
                table_name = create_table_match.group(2)
                columns_definition = create_table_match.group(3)
                columns = [col.strip() for col in columns_definition.split(',')]
                in_table_definition = True
                continue

            # Если мы внутри определения таблицы, добавляем строки к текущему определению
            if in_table_definition and line.endswith(');'):
                in_table_definition = False
                line = line.rstrip(');')
                columns.extend([col.strip() for col in line.split(',')])

                # Обработка столбцов
                for column in columns:
                    if not column:
                        continue
                    column_parts = re.split(r'\s+', column, 1)
                    column_name = column_parts[0].strip('`"')
                    column_rest = column_parts[1] if len(column_parts) > 1 else ''

                    data_type = 'text'
                    nullable = 'YES'
                    char_len = None

                    # Определяем тип данных
                    if 'int' in column_rest:
                        data_type = 'int'
                    elif 'varchar' in column_rest:
                        data_type = 'varchar'
                        char_len_match = re.search(r'\((\d+)\)', column_rest)
                        if char_len_match:
                            char_len = int(char_len_match.group(1))
                    elif 'text' in column_rest:
                        data_type = 'text'

                    # Определяем возможность NULL
                    if 'NOT NULL' in column_rest:
                        nullable = 'NO'

                    all_data.append({
                        'Таблица': table_name,
                        'Имя столбца': column_name,
                        'Тип данных': data_type,
                        'Максимальная длина': char_len if char_len else "",
                        'Может быть NULL': nullable,
                        'Пример данных': "",
                        }
                    )

                continue

            # Если мы внутри определения таблицы, добавляем строки к текущему определению
            if in_table_definition:
                columns.extend([col.strip() for col in line.split(',')])

    return all_data


def save_data_to_file(df, base_path):
    """Сохраняет данные в файл, создавая новый файл, если текущий слишком большой."""
    file_number = 1
    new_path = base_path

    # Проверяем, существует ли файл и превышает ли он лимит строк
    while os.path.exists(new_path):
        try:
            existing_df = pd.read_excel(new_path) if new_path.endswith('.xlsx') else pd.read_csv(new_path)
            if len(existing_df) + len(df) <= MAX_ROWS_PER_FILE:
                break
        except:
            pass

        # Создаём новый файл с номером
        base, ext = os.path.splitext(base_path)
        new_path = f"{base}_{file_number}{ext}"
        file_number += 1

    # Сохраняем данные
    if new_path.endswith('.xlsx'):
        df.to_excel(new_path, index=False, engine='openpyxl')
    else:
        df.to_csv(new_path, index=False)

    return new_path

def parse_database():
    """Подключается к базе данных и парсит выбранные таблицы."""
    config = load_config()
    host = host_entry.get() or config.get("host", "127.0.0.1")
    port = port_entry.get() or config.get("port", "5432")
    user = user_entry.get() or config.get("user", "postgres")
    password = password_entry.get() or config.get("password", "")
    dbname = dbname_entry.get() or config.get("dbname", "postgres")
    tables_input = tables_entry.get()
    tables = [t.strip() for t in tables_input.split(",")] if tables_input else None

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        if not tables:
            tables = fetch_tables(conn)

        all_data = fetch_columns_and_metadata(conn, tables)
        df = pd.DataFrame(all_data)

        # Переименовываем столбцы на русские названия
        df.columns = [
            'Таблица',
            'Имя столбца',
            'Тип данных',
            'Максимальная длина',
            'Может быть NULL',
            'Пример данных'
        ]

        # Запрашиваем путь для сохранения файла
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            initialdir=config.get("save_path", ".")
        )

        if not save_path:
            return

        # Сохраняем данные с учётом ограничения на количество строк
        final_path = save_data_to_file(df, save_path)

        messagebox.showinfo("Успех", f"Данные успешно сохранены в {final_path}")

        # Сохраняем текущие настройки
        current_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "dbname": dbname,
            "save_path": os.path.dirname(final_path)
        }
        save_config(current_config)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения или парсинга: {e}")

def parse_dump():
    """Парсит SQL-дамп и сохраняет структуру таблиц."""
    dump_path = filedialog.askopenfilename(
        title="Выберите файл дампа",
        filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
    )

    if not dump_path:
        return

    try:
        all_data = parse_dump_file(dump_path)
        df = pd.DataFrame(all_data)

        # Переименовываем столбцы на русские названия
        df.columns = [
            'Таблица',
            'Имя столбца',
            'Тип данных',
            'Максимальная длина',
            'Может быть NULL',
            'Пример данных'
        ]

        # Запрашиваем путь для сохранения файла
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            initialdir=os.path.dirname(dump_path)
        )

        if not save_path:
            return

        # Сохраняем данные с учётом ограничения на количество строк
        final_path = save_data_to_file(df, save_path)

        messagebox.showinfo("Успех", f"Данные успешно сохранены в {final_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка парсинга дампа: {e}")

# Создаём главное окно
window = tk.Tk()
window.title("Парсер структур баз данных")
window.geometry("600x450")

# Загружаем сохранённые настройки
config = load_config()

# Виджеты для ввода данных подключения
tk.Label(window, text="IP базы данных:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
host_entry = tk.Entry(window, width=30)
host_entry.grid(row=0, column=1, padx=10, pady=5)
host_entry.insert(0, config.get("host", "127.0.0.1"))

tk.Label(window, text="Порт:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
port_entry = tk.Entry(window, width=30)
port_entry.grid(row=1, column=1, padx=10, pady=5)
port_entry.insert(0, config.get("port", "5432"))

tk.Label(window, text="Имя пользователя:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
user_entry = tk.Entry(window, width=30)
user_entry.grid(row=2, column=1, padx=10, pady=5)
user_entry.insert(0, config.get("user", "postgres"))

tk.Label(window, text="Пароль:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
password_entry = tk.Entry(window, width=30, show="*")
password_entry.grid(row=3, column=1, padx=10, pady=5)
password_entry.insert(0, config.get("password", ""))

tk.Label(window, text="Название базы данных:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
dbname_entry = tk.Entry(window, width=30)
dbname_entry.grid(row=4, column=1, padx=10, pady=5)
dbname_entry.insert(0, config.get("dbname", "postgres"))

tk.Label(window, text="Таблицы (через запятую, оставьте пустым для всех):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
tables_entry = tk.Entry(window, width=30)
tables_entry.grid(row=5, column=1, padx=10, pady=5)

# Кнопка для запуска парсинга с сервера
parse_button = tk.Button(window, text="Спарсить с сервера", command=parse_database)
parse_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Кнопка для выбора и парсинга дампа
dump_button = tk.Button(window, text="Спарсить из дампа", command=parse_dump)
dump_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

window.mainloop()
