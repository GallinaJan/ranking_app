import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QDialogButtonBox, QMessageBox,
    QFileDialog, QComboBox, QTableWidget, QTableWidgetItem,
    QStackedLayout, QPushButton, QTabWidget, QLabel, QToolBar, QStatusBar, QCheckBox, QPushButton)
from PyQt6.QtGui import QPalette, QColor, QIcon, QAction, QFont
from PyQt6.QtCore import Qt, QSize
import pandas as pd
from topsis import compute_topsis


### Okno Główne ###

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.file_name = None

        self.resize(800, 600)  # rozmiar
        self.setWindowTitle('Aplikacja rankingowa')  # nazwa okna

        tabs = QTabWidget()  # zakładki Konfiguracja, Arkusz, Wykres
        tabs.setTabPosition(QTabWidget.TabPosition.North)  # pozycja zakłedek
        tabs.setMovable(False)  # przemieszczanie zakładek

        tabs.addTab(Config(self), 'Konfiguracja')  # dodanie zakładki Konfiguracja
        tabs.addTab(Sheet(self), 'Arkusz kalkulacyjny')  # dodanie zakładki Arkusz
        tabs.addTab(Chart(), 'Wykres')  # dodanie zakładek Wykres

        self.setCentralWidget(tabs)  # umieszczenie zakładek w oknie


### Zakładki ###


class Config(QWidget):

    def __init__(self, parent):
        super(Config, self).__init__()

        self.parent = parent  # wskaźnik na rodzica
        self.method = "TOPSIS"  # nazwa metody

        layout = QVBoxLayout()  # układ główny
        layout_config = QVBoxLayout()  # rozmieszczenie konfiguracji
        layout_choose_file = QHBoxLayout()  # rozmieszczenie układu z wyborem pliku
        layout_choose_method = QHBoxLayout()  # rozmieszczenie układu z wyborem metody

        layout.setContentsMargins(20, 20, 20, 20)  # wielkość ramki
        layout.setSpacing(40)  # odległości między widżetami

        ### Układ konfiguracji ###

        label_choose_file = QLabel("Wybierz plik .xlsx z bazą przedmiotów")  # etykieta z poleceniem
        font_choose_file = label_choose_file.font()
        font_choose_file.setPointSize(12)
        label_choose_file.setFont(font_choose_file)  # ustawienie wielkości czcionki
        label_choose_file.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # rozmieszczenie
        layout_choose_file.addWidget(label_choose_file)  # dodanie widżetu do układu

        button_choose_file = QPushButton(self)  # przycisk otwierający dialog wyboru
        button_choose_file.setText("Wybierz plik")  # nazwa przycisku
        font_button_choose_file = button_choose_file.font()
        font_button_choose_file.setPointSize(12)
        button_choose_file.setFont(font_button_choose_file)
        button_choose_file.clicked.connect(self.choose_file)  # przypisanie akcji
        layout_choose_file.addWidget(button_choose_file)  # dodanie widżetu do układu

        layout_config.addLayout(layout_choose_file)  # dodanie układu wyboru pliku do układu konfiguracji

        self.label_file_name = QLabel("Wybrany plik: ")  # etykieta z nazwą wybranego pliku
        font_file_name = self.label_file_name.font()
        font_file_name.setPointSize(12)
        self.label_file_name.setFont(font_file_name)  # ustawienie wielkości czcionki
        self.label_file_name.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # rozmieszczenie
        layout_config.addWidget(self.label_file_name)  # dodanie widżetu do układu

        label_method_name = QLabel("Wybrana metoda:")  # etykieta z nazwą wybranej metody
        font_method_name = label_method_name.font()
        font_method_name.setPointSize(12)
        label_method_name.setFont(font_method_name)  # ustawienie wielkości czcionki
        layout_choose_method.addWidget(label_method_name)  # dodanie widżetu do układu

        combo_method = QComboBox()  # lista wyboru metod
        combo_method.addItems(["TOPSIS", "RSM", "SP-CS"])  # dostępne metody
        font_combo_method = combo_method.font()
        font_combo_method.setPointSize(12)
        combo_method.setFont(font_combo_method)
        combo_method.currentTextChanged.connect(self.choose_method)  # przypisanie akcji
        layout_choose_method.addWidget(combo_method)  # dodanie widżetu do układu

        layout_config.addLayout(layout_choose_method)

        button_compute = QPushButton(self)  # przycisk wyliczający ranking
        button_compute.setText("Wylicz ranking")  # nazwa przycisku
        font_compute = button_compute.font()
        font_compute.setPointSize(12)
        button_compute.setFont(font_compute)
        button_compute.clicked.connect(self.compute)  # przypisanie akcji
        layout_config.addWidget(button_compute)

        label_results = QLabel("Wyniki metody:")  # etykieta z poleceniem
        font_results = label_results.font()
        font_results.setPointSize(12)
        font_results.setBold(True)
        label_results.setFont(font_results)  # ustawienie wielkości czcionki
        label_results.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)  # rozmieszczenie
        layout_config.addWidget(label_results)  # dodanie widżetu do układu

        layout.addLayout(layout_config)  # dodanie układu konfiguracji do głównego układu

        ### Układ główny ###

        self.results = QLabel("")  # etykieta z poleceniem
        self.results.setFont(QFont('Calibri', 12))  # ustawienie wielkości czcionki
        self.results.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)  # rozmieszczenie
        layout_config.addWidget(self.results)  # dodanie widżetu do układu

        self.setLayout(layout)  # ustanowienie układu

    ### Akcje ###

    def choose_file(self):
        self.parent.file_name = QFileDialog.getOpenFileName(self, filter="*.xlsx")[0]  # nazwa pliku
        self.label_file_name.setText("Wybrany plik: " + self.parent.file_name)  # aktualizacja etykiety

    def choose_method(self, method):
        self.method = method  # nazwa metody

    def compute(self):
        if self.parent.file_name is not None:
            if self.method == "TOPSIS":
                rank = compute_topsis(self.parent.file_name)
            elif self.method == "RMS":
                pass
            elif self.method == "SP-CS":
                pass
            else:
                rank = compute_topsis(self.parent.file_name)
            self.results.setText(rank)
        else:
            QMessageBox.warning(self, "Brak danych", "Najpierw załaduj dane w oknie Konfiguracja",
                                buttons=QMessageBox.StandardButton.Ok)


class Sheet(QWidget):

    def __init__(self, parent):
        super(Sheet, self).__init__()

        self.parent = parent  # wskaźnik na rodzica

        layout = QVBoxLayout()  # układ
        self.setLayout(layout)

        self.table = QTableWidget()  # widżet tabela
        layout.addWidget(self.table)

        self.button = QPushButton("Załaduj arkusz")  # przycisk na załadowanie arkusza
        self.button.clicked.connect(self.load_excel_data)  # przypisanie akcji
        layout.addWidget(self.button)

    def load_excel_data(self):
        if self.parent.file_name is not None:  # gdy jest ścieżka
            df = pd.read_excel(self.parent.file_name)  # załadowanie danych

            df.fillna('', inplace=True)  # zastąpienie NaN pustym str
            self.table.setRowCount(df.shape[0])
            self.table.setColumnCount(df.shape[1])
            self.table.setHorizontalHeaderLabels(df.columns)

            for row in df.iterrows():  # wypełnianie danych
                values = row[1]
                for col_idx, value in enumerate(values):
                    table_item = QTableWidgetItem(str(value))
                    self.table.setItem(row[0], col_idx, table_item)

            self.table.setColumnWidth(2, 300)  # szerokość kolumn
        else:
            QMessageBox.warning(self, "Brak danych", "Najpierw załaduj dane w oknie Konfiguracja",
                                buttons=QMessageBox.StandardButton.Ok)  # ostrzeżenie


class Chart(QWidget):

    def __init__(self):
        super(Chart, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('yellow'))
        self.setPalette(palette)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
