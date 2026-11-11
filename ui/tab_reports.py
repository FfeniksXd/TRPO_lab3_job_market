from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLabel)
from PySide6.QtCore import Qt

class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Выберите тип отчета:"))
        
        self.report_combo = QComboBox()
        # Заполняем список отчетов
        self.report_combo.addItem("Группировка по возрасту", "age")
        self.report_combo.addItem("Группировка по полу", "gender")
        self.report_combo.addItem("Группировка по образованию", "education")
        self.report_combo.addItem("Группировка по специальности", "specialty")
        self.report_combo.addItem("Группировка по стажу", "experience")
        
        control_layout.addWidget(self.report_combo)
        
        self.btn_generate = QPushButton("Сформировать")
        control_layout.addWidget(self.btn_generate)
        control_layout.addStretch() # Прижимаем всё влево
        
        layout.addLayout(control_layout)

        # Таблица для вывода
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Растягиваем колонки
        layout.addWidget(self.table)

        # Подключаем кнопку
        self.btn_generate.clicked.connect(self.generate_report)

    def generate_report(self):
        report_type = self.report_combo.currentData()
        
        # Получаем заголовки и данные из БД
        headers, data = self.db.get_report_data(report_type)
        
        # Настраиваем таблицу
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))
        
        # Заполняем данными
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                # Выравниваем числа по центру для красоты
                if isinstance(cell_data, int):
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)