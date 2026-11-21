from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLabel, QMessageBox)
from PySide6.QtCore import Qt

class CandidatesMatchingTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_vacancies()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Выберите вакансию:"))
        
        self.vacancy_combo = QComboBox()
        self.vacancy_combo.setMinimumWidth(400) # Сделаем пошире, т.к. названия длинные
        control_layout.addWidget(self.vacancy_combo)
        
        self.btn_match = QPushButton("Найти кандидатов")
        control_layout.addWidget(self.btn_match)
        self.btn_hire = QPushButton("Нанять выбранного")
        control_layout.addWidget(self.btn_hire)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        info_label = QLabel("Показаны кандидаты с процентом соответствия 60% и выше.")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Соответствие", "ФИО", "Стаж", "Ожид. ЗП", "Контакты"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.table)


        self.btn_match.clicked.connect(self.find_candidates)
        self.btn_hire.clicked.connect(self.hire_selected)

    def load_vacancies(self):
        current_id = self.vacancy_combo.currentData()
        self.vacancy_combo.clear()
        vacancies = self.db.get_vacancies_list()
        for v_id, name in vacancies:
            self.vacancy_combo.addItem(name, v_id)
        if current_id is not None:
            idx = self.vacancy_combo.findData(current_id)
            if idx >= 0: self.vacancy_combo.setCurrentIndex(idx)

    def find_candidates(self):
        v_id = self.vacancy_combo.currentData()
        if v_id is None:
            QMessageBox.warning(self, "Ошибка", "Нет активных вакансий!")
            return

        matches = self.db.get_matching_candidates(v_id)
        
        self.table.setRowCount(len(matches))
        for row_idx, m in enumerate(matches):
            score, u_id, full_name, exp, sal, contacts = m
            
            item_score = QTableWidgetItem(f"{score}%")
            item_score.setTextAlignment(Qt.AlignCenter)
            item_score.setData(Qt.UserRole, u_id)
            if score >= 80:
                item_score.setBackground(Qt.green)
            elif score >= 60:
                item_score.setBackground(Qt.yellow)

            self.table.setItem(row_idx, 0, item_score)
            self.table.setItem(row_idx, 1, QTableWidgetItem(full_name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(exp))
            self.table.setItem(row_idx, 3, QTableWidgetItem(sal))
            self.table.setItem(row_idx, 4, QTableWidgetItem(contacts))

    def hire_selected(self):
        row = self.table.currentRow()
        v_id = self.vacancy_combo.currentData()
        if row == -1 or v_id is None:
            QMessageBox.information(self, "Внимание", "Выберите кандидата в таблице.")
            return

        u_id = self.table.item(row, 0).data(Qt.UserRole)
        name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Нанять '{name}' на вакансию:\n{self.vacancy_combo.currentText()}?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.hire(u_id, v_id)
                self.table.setRowCount(0)
                self.load_vacancies()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))



    def showEvent(self, event):
        super().showEvent(event)
        self.load_vacancies()