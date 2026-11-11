from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QPushButton, 
                               QDialog, QLineEdit, QFormLayout, QMessageBox,
                               QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
                               QGroupBox, QTextEdit, QScrollArea)
from PySide6.QtCore import Qt
import psycopg2

class VacancyDialog(QDialog):
    def __init__(self, db, parent=None, data=None, skills_dict=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Данные вакансии")
        self.resize(700, 800)

        main_layout = QVBoxLayout(self)
        
        # --- Создаем прокручиваемую область ---
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        # --- Группа 1: Основная информация ---
        group_main = QGroupBox("Основная информация")
        form_main = QFormLayout(group_main)
        
        self.ent_combo = QComboBox()
        self.spec_combo = QComboBox()
        self.title_input = QLineEdit()
        self.is_active_check = QCheckBox("Вакансия активна")
        self.is_active_check.setChecked(True)

        # Заполняем комбобоксы
        for id, name in self.db.execute_query("SELECT id, name FROM enterprises ORDER BY name"):
            self.ent_combo.addItem(name, id)
        for id, name in self.db.get_specialties():
            self.spec_combo.addItem(name, id)

        form_main.addRow("Предприятие:", self.ent_combo)
        form_main.addRow("Специальность:", self.spec_combo)
        form_main.addRow("Должность:", self.title_input)
        form_main.addRow("", self.is_active_check)
        layout.addWidget(group_main)

        # --- Группа 2: Требования ---
        group_req = QGroupBox("Требования к кандидату")
        form_req = QFormLayout(group_req)
        
        self.edu_combo = QComboBox()
        self.edu_combo.addItem("Не важно", None) # None сохранится как NULL в БД
        for id, name in self.db.get_education_levels():
            self.edu_combo.addItem(name, id)
            
        self.gender_combo = QComboBox()
        self.gender_combo.addItem("Любой", None)
        self.gender_combo.addItem("Мужской", "M")
        self.gender_combo.addItem("Женский", "F")
        
        self.exp_spin = QSpinBox()
        self.exp_spin.setSuffix(" лет")
        
        self.min_age_spin = QSpinBox()
        self.min_age_spin.setSpecialValueText("Не важно")
        self.min_age_spin.setMaximum(100)
        
        self.max_age_spin = QSpinBox()
        self.max_age_spin.setSpecialValueText("Не важно")
        self.max_age_spin.setMaximum(100)

        form_req.addRow("Образование:", self.edu_combo)
        form_req.addRow("Мин. стаж:", self.exp_spin)
        form_req.addRow("Пол:", self.gender_combo)
        form_req.addRow("Мин. возраст:", self.min_age_spin)
        form_req.addRow("Макс. возраст:", self.max_age_spin)
        layout.addWidget(group_req)

        # --- Группа 3: Условия труда ---
        group_cond = QGroupBox("Условия труда и оплата")
        form_cond = QFormLayout(group_cond)
        
        self.workday_input = QLineEdit()
        self.weekends_input = QLineEdit()
        self.vacation_spin = QSpinBox()
        self.vacation_spin.setSpecialValueText("Не указано")
        self.vacation_spin.setMaximum(100)
        self.vacation_spin.setSuffix(" дней")
        
        self.sal_min_spin = QDoubleSpinBox()
        self.sal_min_spin.setMaximum(10000000)
        self.sal_min_spin.setSpecialValueText("Не указано")
        
        self.sal_max_spin = QDoubleSpinBox()
        self.sal_max_spin.setMaximum(10000000)
        self.sal_max_spin.setSpecialValueText("Не указано")

        self.benefits_input = QTextEdit()
        self.benefits_input.setMaximumHeight(60)
        
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(60)

        form_cond.addRow("Рабочий день:", self.workday_input)
        form_cond.addRow("Выходные:", self.weekends_input)
        form_cond.addRow("Отпуск:", self.vacation_spin)
        form_cond.addRow("Зарплата от:", self.sal_min_spin)
        form_cond.addRow("Зарплата до:", self.sal_max_spin)
        form_cond.addRow("Льготы:", self.benefits_input)
        form_cond.addRow("Описание:", self.desc_input)
        layout.addWidget(group_cond)

        # --- Группа 4: Навыки ---
        group_skills = QGroupBox("Требуемые навыки (галочка + обязательность)")
        skills_layout = QVBoxLayout(group_skills)
        
        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(2)
        self.skills_table.setHorizontalHeaderLabels(["Навык", "Обязательный?"])
        self.skills_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.skills_table.setSelectionMode(QTableWidget.NoSelection)
        self.skills_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.fill_skills(skills_dict)
        skills_layout.addWidget(self.skills_table)
        layout.addWidget(group_skills)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        if data:
            self.fill_data(data)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def fill_skills(self, skills_dict):
        all_skills = self.db.get_skills()
        self.skills_table.setRowCount(len(all_skills))
        for row, (id, name) in enumerate(all_skills):
            # Колонка 0: Выбор навыка
            item_skill = QTableWidgetItem(name)
            item_skill.setData(Qt.UserRole, id)
            item_skill.setFlags(item_skill.flags() | Qt.ItemIsUserCheckable)
            
            # Колонка 1: Обязательность
            item_req = QTableWidgetItem()
            item_req.setFlags(item_req.flags() | Qt.ItemIsUserCheckable)
            item_req.setCheckState(Qt.Unchecked) 
            
            if skills_dict and id in skills_dict:
                item_skill.setCheckState(Qt.Checked)
                item_req.setCheckState(Qt.Checked if skills_dict[id] else Qt.Unchecked)
            else:
                item_skill.setCheckState(Qt.Unchecked)
                
            self.skills_table.setItem(row, 0, item_skill)
            self.skills_table.setItem(row, 1, item_req)

    def fill_data(self, data):
        idx = self.ent_combo.findData(data[0])
        if idx >= 0: self.ent_combo.setCurrentIndex(idx)
        
        idx = self.spec_combo.findData(data[1])
        if idx >= 0: self.spec_combo.setCurrentIndex(idx)
        
        self.title_input.setText(data[2] or "")
        
        idx = self.edu_combo.findData(data[3])
        if idx >= 0: self.edu_combo.setCurrentIndex(idx)
        
        self.exp_spin.setValue(data[4] or 0)
        
        idx = self.gender_combo.findData(data[5])
        if idx >= 0: self.gender_combo.setCurrentIndex(idx)
        
        self.min_age_spin.setValue(data[6] or 0)
        self.max_age_spin.setValue(data[7] or 0)
        
        self.workday_input.setText(data[8] or "")
        self.weekends_input.setText(data[9] or "")
        self.vacation_spin.setValue(data[10] or 0)
        
        if data[11] is not None: self.sal_min_spin.setValue(float(data[11]))
        if data[12] is not None: self.sal_max_spin.setValue(float(data[12]))
        
        self.benefits_input.setText(data[13] or "")
        self.desc_input.setText(data[14] or "")
        self.is_active_check.setChecked(data[15])

    def get_data(self):
        def val(text): return text.strip() if text.strip() else None
        
        # Если значение 0, сохраняем NULL
        min_age = self.min_age_spin.value() if self.min_age_spin.value() > 0 else None
        max_age = self.max_age_spin.value() if self.max_age_spin.value() > 0 else None
        vac = self.vacation_spin.value() if self.vacation_spin.value() > 0 else None
        sal_min = self.sal_min_spin.value() if self.sal_min_spin.value() > 0 else None
        sal_max = self.sal_max_spin.value() if self.sal_max_spin.value() > 0 else None
        
        data_tuple = (
            self.ent_combo.currentData(), self.spec_combo.currentData(),
            val(self.title_input.text()), self.edu_combo.currentData(),
            self.exp_spin.value(), self.gender_combo.currentData(),
            min_age, max_age, val(self.workday_input.text()),
            val(self.weekends_input.text()), vac, sal_min, sal_max,
            val(self.benefits_input.toPlainText()), val(self.desc_input.toPlainText()),
            self.is_active_check.isChecked()
        )
        
        # Собираем навыки в словарь {id: обязательность}
        selected_skills = {}
        for row in range(self.skills_table.rowCount()):
            item_skill = self.skills_table.item(row, 0)
            item_req = self.skills_table.item(row, 1)
            if item_skill.checkState() == Qt.Checked:
                skill_id = item_skill.data(Qt.UserRole)
                is_req = (item_req.checkState() == Qt.Checked)
                selected_skills[skill_id] = is_req
                
        return data_tuple, selected_skills


class VacanciesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
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

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Предприятие", "Специальность", "Должность", "З/П от", "З/П до", "Активна"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.hideColumn(0)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        data = self.db.get_vacancies()
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data[1] or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row_data[2] or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row_data[3] or ""))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row_data[4]) if row_data[4] is not None else ""))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(row_data[5]) if row_data[5] is not None else ""))
            self.table.setItem(row_idx, 6, QTableWidgetItem("Да" if row_data[6] else "Нет"))

    def add_record(self):
        dialog = VacancyDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            data, skills = dialog.get_data()
            try:
                self.db.add_vacancy(data, skills)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для редактирования.")
            return
            
        v_id = int(self.table.item(selected_row, 0).text())
        
        try:
            full_data, skills_dict = self.db.get_vacancy_by_id(v_id)
            dialog = VacancyDialog(self.db, self, full_data, skills_dict)
            
            if dialog.exec() == QDialog.Accepted:
                new_data, new_skills = dialog.get_data()
                self.db.update_vacancy(v_id, new_data, new_skills)
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для удаления.")
            return
            
        v_id = int(self.table.item(selected_row, 0).text())
        title = self.table.item(selected_row, 3).text()

        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить вакансию '{title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_vacancy(v_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))