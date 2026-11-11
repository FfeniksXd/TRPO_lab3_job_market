import sys
import psycopg2
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox

def main():
    # --- 1. Проверка подключения к БД ---
    print("Проверка подключения к БД...")
    try:
        conn = psycopg2.connect(
            dbname="laboratory_3",
            user="postgres",
            password="7ujm7UJM",  
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM education_levels")
        count = cursor.fetchone()[0]
        print(f"Успех! База данных подключена. Уровней образования: {count}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка БД: {e}")
        sys.exit(1) # Если БД нет, дальше не идем

    # --- 2. Проверка графики PySide6 ---
    print("Запуск графического интерфейса...")
    app = QApplication(sys.argv)
    
    # Простое окно для проверки
    window = QLabel("Привет! База данных подключена, PySide6 работает!")
    window.setWindowTitle("Тест успешен")
    window.resize(400, 100)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()