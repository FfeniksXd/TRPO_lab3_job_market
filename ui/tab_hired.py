from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QHeaderView, QPushButton,
                               QMessageBox)


class HiredTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отменить найм")
        self.btn_refresh = QPushButton("Обновить")
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Предприятие", "Должность", "Дата найма"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.hideColumn(0)
        layout.addWidget(self.table)

        self.btn_cancel.clicked.connect(self.cancel_hire)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        data = self.db.get_hired()
        self.table.setRowCount(len(data))
        for row_idx, (h_id, name, ent, title, hired_at) in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(h_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(ent or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(title or ""))
            date_str = hired_at.strftime("%d.%m.%Y") if hired_at else ""
            self.table.setItem(row_idx, 4, QTableWidgetItem(date_str))

    def cancel_hire(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.information(self, "Внимание", "Выберите запись.")
            return

        h_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Отменить найм '{name}'?\nВакансия снова станет активной, а человек вернётся в подбор.",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.cancel_hire(h_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()