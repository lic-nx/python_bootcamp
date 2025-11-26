import sys
import subprocess
import json
import os
import psycopg2
import pandas as pd
# import re

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
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
        """
        )
        return [table[0] for table in cur.fetchall()]


def fetch_column_comment(conn, table_name, column_name):
    """Возвращает комментарий к указанному столбцу."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT description
            FROM pg_description
            WHERE objoid = (
                SELECT oid
                FROM pg_class
                WHERE relname = %s
            ) AND objsubid = (
                SELECT attnum
                FROM pg_attribute
                WHERE attrelid = (
                    SELECT oid
                    FROM pg_class
                    WHERE relname = %s
                ) AND attname = %s
            );
        """,
            (table_name, table_name, column_name),
        )
        row = cur.fetchone()
        return row[0] if row else ""


def fetch_columns_and_metadata(conn, table_names):
    """Получает метаданные для указанных таблиц."""
    all_data = []
    with conn.cursor() as cur:
        for table_name in table_names:
            cur.execute(
                f"""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}';
            """
            )
            columns = cur.fetchall()

            for col in columns:
                column_name, data_type, char_len, nullable = col

                # Получаем комментарий для столбца
                comment = fetch_column_comment(conn, table_name, column_name)

                # Выполняем запрос для получения примера данных
                example_query = f"SELECT {column_name} FROM {table_name} LIMIT 1;"
                cur.execute(example_query)
                example_value = cur.fetchone()[0] if cur.rowcount > 0 else None

                all_data.append(
                    {
                        "Название атрибута": "",
                        "Обозначение атрибута (лат.)": column_name,
                        "Тип данных": data_type,
                        "Описание": comment,
                        # 'Пример данных': str(example_value) if example_value is not None else "",
                    }
                )
    return all_data


# def parse_dump_file(dump_path):
#     """Парсит SQL-дамп и извлекает структуру таблиц."""
#     all_data = []
#     table_name = None
#     in_table_definition = False

#     with open(dump_path, "r", encoding="utf-8") as file:
#         for line in file:
#             line = line.strip()

#             # Поиск создания таблицы
#             create_table_match = re.match(
#                 r"CREATE TABLE (`?)(\w+)\1\s*$", line, re.IGNORECASE
#             )
#             if create_table_match:
#                 table_name = create_table_match.group(2)
#                 columns_definition = create_table_match.group(3)
#                 columns = [col.strip() for col in columns_definition.split(",")]
#                 in_table_definition = True
#                 continue

#             # Если мы внутри определения таблицы, добавляем строки к текущему определению
#             if in_table_definition and line.endswith(");"):
#                 in_table_definition = False
#                 line = line.rstrip(");")
#                 columns.extend([col.strip() for col in line.split(",")])

#                 # Обработка столбцов
#                 for column in columns:
#                     if not column:
#                         continue
#                     column_parts = re.split(r"\s+", column, 1)
#                     column_name = column_parts[0].strip('`"')
#                     column_rest = column_parts[1] if len(column_parts) > 1 else ""

#                     data_type = "text"
#                     nullable = "YES"
#                     char_len = None

#                     # Определяем тип данных
#                     if "int" in column_rest:
#                         data_type = "int"
#                     elif "varchar" in column_rest:
#                         data_type = "varchar"
#                         char_len_match = re.search(r"$(\d+)$$", column_rest)
#                         if char_len_match:
#                             char_len = int(char_len_match.group(1))
#                     elif "text" in column_rest:
#                         data_type = "text"

#                     # Определяем возможность NULL
#                     if "NOT NULL" in column_rest:
#                         nullable = "NO"

#                     all_data.append(
#                         {
#                             "Название атрибута": "",
#                             "Обозначение атрибута (лат.)": column_name,
#                             "Тип данных": data_type,
#                             "Описание атрибута": "",
#                             "Критерий качества данных (если применимо)": "",
#                             "Предельно допустимое значение показателя качества данных (если применимо)": "",
#                             "Приоритет инцидента качества данных (если применимо)": "",
#                         }
#                     )

#                 continue

#             # Если мы внутри определения таблицы, добавляем строки к текущему определению
#             if in_table_definition:
#                 columns.extend([col.strip() for col in line.split(",")])

#     return all_data


def save_data_to_file(df, base_path):
    """Сохраняет данные в файл, создавая новый файл, если текущий слишком большой."""
    file_number = 1
    new_path = base_path

    # Проверяем, существует ли файл и превышает ли он лимит строк
    while os.path.exists(new_path):
        try:
            existing_df = (
                pd.read_excel(new_path)
                if new_path.endswith(".xlsx")
                else pd.read_csv(new_path)
            )
            if len(existing_df) + len(df) <= MAX_ROWS_PER_FILE:
                break
        except:
            pass

        # Создаем новый файл с номером
        base, ext = os.path.splitext(base_path)
        new_path = f"{base}_{file_number}{ext}"
        file_number += 1

    # Добавляем номер строки
    df["№"] = range(1, len(df) + 1)

    # Добавляем два новых поля
    df["Критерий качества данных"] = ""
    df["Приоритет инцидента качества данных"] = ""

    # Сохраняем данные
    ordered_columns = [
        "№",
        "Название атрибута",
        "Обозначение атрибута (лат.)",
        "Тип данных",
        "Описание атрибута",
        "Критерий качества данных (если применимо)",
        "Предельно допустимое значение показателя качества данных (если применимо)",
        "Приоритет инцидента качества данных (если применимо)",
    ]
    df = pd.DataFrame(df, columns=ordered_columns)

    if new_path.endswith(".xlsx"):
        df.to_excel(new_path, index=False, engine="openpyxl")
    else:
        df.to_csv(new_path, index=False)

    return new_path


def connect_database(host, port, user, password, dbname, tables_input=None):
    """
    Подключается к базе данных и парсит указанные таблицы.
    Параметр tables_input может содержать список таблиц, разделённых запятыми.
    """
    tables = [t.strip() for t in tables_input.split(",")] if tables_input else None
    try:
        conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )

        if not tables:
            tables = fetch_tables(conn)

        all_data = fetch_columns_and_metadata(conn, tables)
        df = pd.DataFrame(all_data)

        # Переименовываем столбцы на русские названия
        df.columns = [
            "Название атрибута",
            "Обозначение атрибута (лат.)",
            "Тип данных",
            "Описание",
        ]

        # Пользователь вводит путь для сохранения файла
        save_path = input(
            "Введите полный путь для сохранения файла (например /path/to/file.xlsx): "
        )

        if not save_path:
            raise ValueError("Необходимо ввести путь для сохранения файла.")

        # Сохраняем данные с учётом ограничения на количество строк
        final_path = save_data_to_file(df, save_path)

        print(f"\n\n🔥 Данные успешно сохранены в {final_path}\n")

        # Сохраняем текущие настройки
        current_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "dbname": dbname,
            "save_path": os.path.dirname(final_path),
        }
        save_config(current_config)

    except psycopg2.Error as e:
        print(f"❌ Произошла ошибка подключения к базе данных:\n{e}")
    except Exception as e:
        print(f"⚠️ Произошла непредвиденная ошибка:\n{e}")


if __name__ == "__main__":
    config = load_config()
    host = input(
        f"Введите IP-адрес хоста или нажмите Enter для подключения к хосту {config.get('host', 'localhost')} "
    ) or config.get("host", "localhost")
    port = input(
        f"Введите порт или нажмите Enter для подключения к порту {config.get('port', '5432')} "
    ) or config.get("port", "5432")
    user = input(
        f"Введите имя пользователя или нажмите Enter для подключения от имени {config.get('user', 'postgres')} "
    ) or config.get("user", "postgres")
    password = input("Введите пароль: ") or config.get("password", "")
    dbname = input(
        f"Введите название базы данных или нажмите Enter для подключения к базе данных {config.get('dbname', 'postgres')} "
    ) or config.get("dbname", "postgres")
    tables_input = input(
        "Введите название таблиц, которые хотите спарсить (через запятую) или нажмите Enter для парсинга всех таблиц: "
    )

    connect_database(host, port, user, password, dbname, tables_input)
