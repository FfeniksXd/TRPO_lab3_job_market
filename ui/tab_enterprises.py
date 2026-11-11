from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QPushButton, 
                               QDialog, QLineEdit, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
import psycopg2

class EnterpriseDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Данные предприятия")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Поля ввода
        self.name_input = QLineEdit()
        self.city_input = QLineEdit()
        self.street_input = QLineEdit()
        self.building_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.website_input = QLineEdit()
        self.telegram_input = QLineEdit()

        form.addRow("Название (обяз.):", self.name_input)
        form.addRow("Город:", self.city_input)
        form.addRow("Улица:", self.street_input)
        form.addRow("Дом:", self.building_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Сайт:", self.website_input)
        form.addRow("Telegram:", self.telegram_input)
        
        layout.addLayout(form)

        # Заполняем поля, если это редактирование (data передан)
        if data:
            # data = (id, name, city, street, building, phone, email, website, telegram)
            self.name_input.setText(data[1] or "")
            self.city_input.setText(data[2] or "")
            self.street_input.setText(data[3] or "")
            self.building_input.setText(data[4] or "")
            self.phone_input.setText(data[5] or "")
            self.email_input.setText(data[6] or "")
            self.website_input.setText(data[7] or "")
            self.telegram_input.setText(data[8] or "")

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        """Возвращает кортеж с данными. Пустые строки заменяем на None (NULL в БД)."""
        def val(text):
            return text.strip() if text.strip() else None
            
        return (
            val(self.name_input.text()),
            val(self.city_input.text()),
            val(self.street_input.text()),
            val(self.building_input.text()),
            val(self.phone_input.text()),
            val(self.email_input.text()),
            val(self.website_input.text()),
            val(self.telegram_input.text())
        )

class EnterprisesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Город", "Телефон", "Сайт"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.hideColumn(0) # Прячем ID
        
        layout.addWidget(self.table)

        # Сигналы
        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        data = self.db.get_enterprises()
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0]))) # ID
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data[1] or "")) # Name
            self.table.setItem(row_idx, 2, QTableWidgetItem(row_data[2] or "")) # City
            self.table.setItem(row_idx, 3, QTableWidgetItem(row_data[3] or "")) # Phone
            self.table.setItem(row_idx, 4, QTableWidgetItem(row_data[4] or "")) # Website

    def add_record(self):
        dialog = EnterpriseDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data[0]: # Проверка обязательного поля name
                QMessageBox.warning(self, "Ошибка", "Название предприятия обязательно!")
                return
            try:
                self.db.add_enterprise(*data) # Распаковываем кортеж через *
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для редактирования.")
            return
            
        # Нам нужны ПОЛНЫЕ данные для окна редактирования, 
        # а в таблице мы показываем только часть. Поэтому делаем запрос в БД по ID.
        ent_id = int(self.table.item(selected_row, 0).text())
        
        # Получаем полную запись
        full_data = self.db.execute_query(
            "SELECT id, name, city, street, building, phone, email, website, telegram FROM enterprises WHERE id = %s", 
            (ent_id,)
        )[0] # [0] берет первую (и единственную) строку из результата

        dialog = EnterpriseDialog(self, full_data)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            if not new_data[0]:
                QMessageBox.warning(self, "Ошибка", "Название предприятия обязательно!")
                return
            try:
                self.db.update_enterprise(ent_id, *new_data)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для удаления.")
            return
            
        ent_id = int(self.table.item(selected_row, 0).text())
        name = self.table.item(selected_row, 1).text()

        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить предприятие '{name}'?\nВНИМАНИЕ: Все вакансии этого предприятия также будут удалены!",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_enterprise(ent_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))