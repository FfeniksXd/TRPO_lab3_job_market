import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QWidget
from db import Database
from ui.tab_specialties import SpecialtiesTab
from ui.tab_enterprises import EnterprisesTab  
from ui.tab_vacancies import VacanciesTab
from ui.tab_unemployed import UnemployedTab
from ui.tab_reports import ReportsTab
from ui.tab_matching import MatchingTab
from ui.tab_candidates_matching import CandidatesMatchingTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Рынок труда - Лабораторная работа №3")
        self.resize(1000, 700)

        try:
            self.db = Database()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД:\n{e}")
            sys.exit(1)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Добавляем вкладки
        self.tabs.addTab(UnemployedTab(self.db), "Безработные") 
        self.tabs.addTab(EnterprisesTab(self.db), "Предприятия") 
        self.tabs.addTab(VacanciesTab(self.db), "Вакансии")
        self.tabs.addTab(ReportsTab(self.db), "Отчеты")
        self.tabs.addTab(SpecialtiesTab(self.db), "Специальности")
        self.tabs.addTab(MatchingTab(self.db), "Подбор вакансий")
        self.tabs.addTab(CandidatesMatchingTab(self.db), "Подбор кандидатов")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())