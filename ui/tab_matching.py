from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLabel, QMessageBox)
from PySide6.QtCore import Qt

class MatchingTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_users()  # Загружаем список людей при старте

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Выберите безработного:"))
        
        self.user_combo = QComboBox()
        control_layout.addWidget(self.user_combo)
        
        self.btn_match = QPushButton("Подобрать вакансии")
        control_layout.addWidget(self.btn_match)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Подсказка
        info_label = QLabel("Показаны вакансии с процентом соответствия 60% и выше (сортировка по убыванию).")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Соответствие", "Предприятие", "Должность", "Зарплата", "Описание"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch) # Описание растягиваем
        layout.addWidget(self.table)

        self.btn_match.clicked.connect(self.find_matches)

        self.btn_hire = QPushButton("Нанять на выбранную вакансию")
        control_layout.addWidget(self.btn_hire)
        self.btn_hire.clicked.connect(self.hire_selected)


    def load_users(self):
        # Запоминаем, кто был выбран, чтобы не сбрасывать выбор при обновлении
        current_id = self.user_combo.currentData()
        
        self.user_combo.blockSignals(True) # Блокируем сигналы на время обновления
        self.user_combo.clear()
        
        users = self.db.get_unemployed_list()
        for u_id, name in users:
            self.user_combo.addItem(name, u_id)
            
        # Если человек, который был выбран, еще существует в базе — восстанавливаем выбор
        if current_id is not None:
            idx = self.user_combo.findData(current_id)
            if idx >= 0:
                self.user_combo.setCurrentIndex(idx)
                
        self.user_combo.blockSignals(False)

    def find_matches(self):
        u_id = self.user_combo.currentData()
        if u_id is None:
            QMessageBox.warning(self, "Ошибка", "В базе нет безработных!")
            return

        # Получаем результаты из БД
        matches = self.db.get_matching_vacancies(u_id)
        
        # Отображаем в таблице
        self.table.setRowCount(len(matches))
        for row_idx, m in enumerate(matches):
            score, v_id, ent_name, title, salary, desc = m
            
            item_score = QTableWidgetItem(f"{score}%")
            item_score.setTextAlignment(Qt.AlignCenter)
            item_score.setData(Qt.UserRole, v_id)
            # Красим высокий балл в зеленый
            if score >= 80:
                item_score.setBackground(Qt.green)
            elif score >= 60:
                item_score.setBackground(Qt.yellow)

            self.table.setItem(row_idx, 0, item_score)
            self.table.setItem(row_idx, 1, QTableWidgetItem(ent_name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(title))
            self.table.setItem(row_idx, 3, QTableWidgetItem(salary))
            self.table.setItem(row_idx, 4, QTableWidgetItem(desc))

    def hire_selected(self):
        row = self.table.currentRow()
        u_id = self.user_combo.currentData()
        if row == -1 or u_id is None:
            QMessageBox.information(self, "Внимание", "Выберите вакансию в таблице.")
            return
        v_id = self.table.item(row, 0).data(Qt.UserRole)
        ent = self.table.item(row, 1).text()
        title = self.table.item(row, 2).text()
        name = self.user_combo.currentText()

        reply = QMessageBox.question(self, "Подтверждение",
                                    f"Нанять '{name}' на вакансию '{title}' ({ent})?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.hire(u_id, v_id)
                self.table.setRowCount(0)
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))


    # Этот метод срабатывает автоматически каждый раз, когда вкладка становится видимой
    def showEvent(self, event):
        super().showEvent(event)
        self.load_users()