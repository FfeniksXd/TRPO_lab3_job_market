from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QPushButton, 
                               QDialog, QLineEdit, QFormLayout, QMessageBox,
                               QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, 
                               QListWidget, QListWidgetItem, QGroupBox)
from PySide6.QtCore import Qt, QDate
import psycopg2

class UnemployedDialog(QDialog):
    def __init__(self, db, parent=None, data=None, selected_skills=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Данные безработного")
        self.setMinimumWidth(600)

        layout = QVBoxLayout(self)
        
        # --- Группа 1: Личные данные ---
        group_personal = QGroupBox("Личные данные")
        form_personal = QFormLayout(group_personal)
        
        self.name_input = QLineEdit()
        self.gender_combo = QComboBox()
        self.gender_combo.addItem("Мужской", "M")
        self.gender_combo.addItem("Женский", "F")
        self.birth_date = QDateEdit()
        self.birth_date.setDisplayFormat("dd.MM.yyyy")
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate(1990, 1, 1)) # Дефолтная дата

        form_personal.addRow("ФИО (обяз.):", self.name_input)
        form_personal.addRow("Пол:", self.gender_combo)
        form_personal.addRow("Дата рождения:", self.birth_date)
        layout.addWidget(group_personal)

        # --- Группа 2: Адрес и контакты ---
        group_contacts = QGroupBox("Адрес и контакты")
        form_contacts = QFormLayout(group_contacts)
        
        self.city_input = QLineEdit()
        self.street_input = QLineEdit()
        self.building_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        form_contacts.addRow("Город:", self.city_input)
        form_contacts.addRow("Улица:", self.street_input)
        form_contacts.addRow("Дом:", self.building_input)
        form_contacts.addRow("Телефон:", self.phone_input)
        form_contacts.addRow("Email:", self.email_input)
        layout.addWidget(group_contacts)

        # --- Группа 3: Образование и работа ---
        group_job = QGroupBox("Образование и опыт")
        form_job = QFormLayout(group_job)
        
        self.edu_combo = QComboBox()
        self.spec_combo = QComboBox()
        self.reason_combo = QComboBox()
        self.exp_spin = QSpinBox()
        self.exp_spin.setSuffix(" лет")
        self.salary_spin = QDoubleSpinBox()
        self.salary_spin.setMaximum(1000000)
        self.salary_spin.setSuffix(" руб.")

        # Заполняем комбобоксы из БД
        self.fill_combos()

        form_job.addRow("Образование:", self.edu_combo)
        form_job.addRow("Специальность:", self.spec_combo)
        form_job.addRow("Стаж:", self.exp_spin)
        form_job.addRow("Причина безработицы:", self.reason_combo)
        form_job.addRow("Желаемая зарплата:", self.salary_spin)
        layout.addWidget(group_job)

        # --- Группа 4: Навыки ---
        group_skills = QGroupBox("Дополнительные навыки")
        skills_layout = QVBoxLayout(group_skills)
        self.skills_list = QListWidget()
        self.fill_skills(selected_skills)
        skills_layout.addWidget(self.skills_list)
        layout.addWidget(group_skills)

        # Заполнение полей при редактировании
        if data:
            self.fill_data(data)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def fill_combos(self):
        # Заполняем образование
        for id, name in self.db.get_education_levels():
            self.edu_combo.addItem(name, id)
        # Заполняем специальности
        for id, name in self.db.get_specialties():
            self.spec_combo.addItem(name, id)
        # Заполняем причины
        for id, name in self.db.get_unemployment_reasons():
            self.reason_combo.addItem(name, id)

    def fill_skills(self, selected_skills):
        # Заполняем список навыков чекбоксами
        all_skills = self.db.get_skills()
        for id, name in all_skills:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, id) # Сохраняем ID внутрь элемента
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if selected_skills and id in selected_skills:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.skills_list.addItem(item)

    def fill_data(self, data):
        self.name_input.setText(data[1] or "")
        # Устанавливаем пол
        idx = self.gender_combo.findData(data[2])
        if idx >= 0: self.gender_combo.setCurrentIndex(idx)
        # Устанавливаем дату
        if data[3]:
            self.birth_date.setDate(QDate(data[3].year, data[3].month, data[3].day))
        
        self.city_input.setText(data[4] or "")
        self.street_input.setText(data[5] or "")
        self.building_input.setText(data[6] or "")
        
        # Устанавливаем комбобоксы
        if data[8]:
            idx = self.edu_combo.findData(data[8])
            if idx >= 0: self.edu_combo.setCurrentIndex(idx)
        if data[10]:
            idx = self.spec_combo.findData(data[10])
            if idx >= 0: self.spec_combo.setCurrentIndex(idx)
        
        self.exp_spin.setValue(data[11] or 0)
        
        if data[12]:
            idx = self.reason_combo.findData(data[12])
            if idx >= 0: self.reason_combo.setCurrentIndex(idx)
            
        self.phone_input.setText(data[13] or "")
        self.email_input.setText(data[14] or "")
        if data[18] is not None:
            self.salary_spin.setValue(float(data[18]))

    def get_data(self):
        def val(text): return text.strip() if text.strip() else None
        
        # Собираем кортеж строго в том порядке, в котором он нужен для INSERT в db.py
        data_tuple = (
            val(self.name_input.text()), self.gender_combo.currentData(),
            self.birth_date.date().toPython(), val(self.city_input.text()),
            val(self.street_input.text()), val(self.building_input.text()), None,
            self.edu_combo.currentData(), None, self.spec_combo.currentData(),
            self.exp_spin.value(), self.reason_combo.currentData(),
            val(self.phone_input.text()), val(self.email_input.text()),
            None, None, None, self.salary_spin.value()
        )
        
        # Собираем ID отмеченных навыков
        selected_skills = []
        for i in range(self.skills_list.count()):
            item = self.skills_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_skills.append(item.data(Qt.UserRole))
                
        return data_tuple, selected_skills

class UnemployedTab(QWidget):
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
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Пол", "Дата рожд.", "Город", "Образование", "Специальность"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
        data = self.db.get_unemployed()
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0]))) # ID
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data[1] or "")) # ФИО
            gender = "М" if row_data[2] == 'M' else "Ж"
            self.table.setItem(row_idx, 2, QTableWidgetItem(gender))
            # Дата приходит как объект date, форматируем в строку
            date_str = row_data[3].strftime("%d.%m.%Y") if row_data[3] else ""
            self.table.setItem(row_idx, 3, QTableWidgetItem(date_str))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row_data[4] or "")) # Город
            self.table.setItem(row_idx, 5, QTableWidgetItem(row_data[5] or "")) # Образование
            self.table.setItem(row_idx, 6, QTableWidgetItem(row_data[6] or "")) # Специальность

    def add_record(self):
        dialog = UnemployedDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            data, skills = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, "Ошибка", "ФИО обязательно!")
                return
            try:
                self.db.add_unemployed(data, skills)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для редактирования.")
            return
            
        u_id = int(self.table.item(selected_row, 0).text())
        
        try:
            full_data, skill_ids = self.db.get_unemployed_by_id(u_id)
            dialog = UnemployedDialog(self.db, self, full_data, skill_ids)
            
            if dialog.exec() == QDialog.Accepted:
                new_data, new_skills = dialog.get_data()
                if not new_data[0]:
                    QMessageBox.warning(self, "Ошибка", "ФИО обязательно!")
                    return
                self.db.update_unemployed(u_id, new_data, new_skills)
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.information(self, "Внимание", "Выберите строку для удаления.")
            return
            
        u_id = int(self.table.item(selected_row, 0).text())
        name = self.table.item(selected_row, 1).text()

        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить безработного '{name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_unemployed(u_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))