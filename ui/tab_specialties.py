from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QPushButton, 
                               QDialog, QLineEdit, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
import psycopg2

# --- Диалоговое окно для добавления/редактирования ---
class SpecialtyDialog(QDialog):
    def __init__(self, parent=None, name=""):
        super().__init__(parent)
        self.setWindowTitle("Специальность")
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit(name)
        form.addRow("Название:", self.name_input)
        layout.addLayout(form)

        # Кнопки Сохранить / Отмена
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)   # accept() закрывает окно с кодом "ОК"
        self.cancel_btn.clicked.connect(self.reject) # reject() закрывает окно с кодом "Отмена"

    def get_name(self):
        return self.name_input.text().strip()

# --- Основная вкладка ---
class SpecialtiesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Панель с кнопками
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch() # Прижимает кнопку "Обновить" вправо
        btn_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Название специальности"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection) # Выделять только одну строку
        self.table.hideColumn(0) # ID нам в таблице не нужен, мы его спрячем
        
        layout.addWidget(self.table)

        # Подключаем кнопки к функциям (сигналы и слоты)
        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        data = self.db.get_specialties()
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            # В колонку 0 кладем ID, в колонку 1 - Название
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data[1]))

    def add_record(self):
        dialog = SpecialtyDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_name()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
                return
            try:
                self.db.add_specialty(name)
                self.load_data() # Обновляем таблицу
            except psycopg2.errors.UniqueViolation:
                QMessageBox.warning(self, "Ошибка", "Такая специальность уже существует!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для редактирования.")
            return
            
        spec_id = int(self.table.item(selected_row, 0).text())
        current_name = self.table.item(selected_row, 1).text()

        dialog = SpecialtyDialog(self, current_name)
        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.get_name()
            if not new_name:
                return
            try:
                self.db.update_specialty(spec_id, new_name)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для удаления.")
            return
            
        spec_id = int(self.table.item(selected_row, 0).text())
        name = self.table.item(selected_row, 1).text()

        # Подтверждение удаления
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Вы точно хотите удалить '{name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_specialty(spec_id)
                self.load_data()
            except psycopg2.errors.ForeignKeyViolation:
                # Вот она, защита БД, которую мы настраивали!
                QMessageBox.critical(self, "Ошибка", 
                    "Невозможно удалить специальность, так как на неё ссылаются безработные или вакансии!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))