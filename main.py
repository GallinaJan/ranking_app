import sys
from typing import List
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, \
    QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget, QLabel, QPushButton, QDialog, QDialogButtonBox,\
    QCheckBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSlot
import pandas as pd
from topsis import compute_topsis
from sp_cs import compute_sp_cs
from rsm import compute_rsm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')


### Okno Główne ###

class MainWindow(QMainWindow):

    def __init__(self):
        """
        Okno główne, wyświetlające aplikacje
        """
        super(MainWindow, self).__init__()

        ### Właściwości bazy danych ###

        self.file_name = None
        self.data_0 = []
        self.data_1 = []
        self.dap1 = []
        self.dap2 = []
        self.dap3 = []
        self.quo_point_mean = []
        self.quo_point_median = []
        self.quo_point_random = []
        self.method = "TOPSIS"
        self.n = 0
        self.N = []
        self.p_ideal = []
        self.p_anti_ideal = []
        self.criteria = []
        self.items_names = []
        self.crit_numbers = [] #lista zaznaczonych kryteriów (checkboxów)

        ### Ustawienia okna ###

        self.resize(800, 600)  # rozmiar
        self.setWindowTitle('Aplikacja rankingowa')  # nazwa okna

        tabs = QTabWidget()  # zakładki Konfiguracja, Arkusz, Wykres
        tabs.setTabPosition(QTabWidget.TabPosition.North)  # pozycja zakłedek
        tabs.setMovable(False)  # przemieszczanie zakładek

        tabs.addTab(Config(self), 'Konfiguracja')  # dodanie zakładki Konfiguracja
        tabs.addTab(Sheet(self), 'Arkusz kalkulacyjny')  # dodanie zakładki Arkusz
        tabs.addTab(Chart(self), 'Wykres')  # dodanie zakładek Wykres

        self.setCentralWidget(tabs)  # umieszczenie zakładek w oknie


### Zakładki ###


class Config(QWidget):

    def __init__(self, parent: MainWindow):
        """
        Zakładka z konfiguracją danych do obliczeń
        :param parent: (MainWindow) : okno rodzic
        """
        super(Config, self).__init__()

        self.parent = parent  # wskaźnik na rodzica
        self.parent.method = "TOPSIS"  # nazwa metody

        layout = QVBoxLayout()  # układ główny
        layout_config = QVBoxLayout()  # rozmieszczenie konfiguracji
        layout_choose_file = QHBoxLayout()  # rozmieszczenie układu z wyborem pliku
        layout_choose_method = QHBoxLayout()  # rozmieszczenie układu z wyborem metody
        layout_choose_categories = QHBoxLayout() #rozmieszczenie wyboru kryteriów z listy

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

        label_crits = QLabel("Wybór kryteriów:")  # etykieta
        font_crits = label_crits.font()
        font_crits.setPointSize(12)
        label_crits.setFont(font_crits)  # ustawienie wielkości czcionki
        layout_choose_categories.addWidget(label_crits)  # dodanie widżetu do układu

        checkboxes = [QCheckBox(f'Kryterium {i + 1}') for i in range(7)]
        for checkbox in checkboxes:
            layout_choose_categories.addWidget(checkbox)
            checkbox.clicked.connect(self.on_checkbox_clicked)
        layout_config.addLayout(layout_choose_categories)

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

    @pyqtSlot()
    def choose_file(self) -> None:
        """
        Wybranie pliku z danymi
        :return: None
        """
        self.parent.file_name = QFileDialog.getOpenFileName(self, filter="*.xlsx")[0]  # nazwa pliku
        self.label_file_name.setText("Wybrany plik: " + self.parent.file_name)  # aktualizacja etykiety

    @pyqtSlot(str)
    def choose_method(self, method: str) -> None:
        """
        Wybranie metody
        :param method: (str) : metoda z ComboBox
        :return: None
        """
        self.parent.method = method  # nazwa metody

    def on_checkbox_clicked(self):
        """
        Wybór kryteriów - kiedy przycisk wciśnięty, numer kryterium (nie indeks!) dodaje się do listy
        :return: None
        """
        sender_checkbox = self.sender()
        checkbox_text = sender_checkbox.text()
        checkbox_state = True if sender_checkbox.isChecked() else False
        if checkbox_state:
            self.parent.crit_numbers.append(int(checkbox_text[-1]))
        else:
            self.parent.crit_numbers.remove(int(checkbox_text[-1]))

    @pyqtSlot()
    def compute(self) -> None:
        """
        Wyliczenie rankingu
        :return: None
        """
        if self.parent.file_name is not None:
            if self.parent.method == "TOPSIS":
                rank, self.parent.n, self.parent.N, self.parent.p_ideal, self.parent.p_anti_ideal, \
                    self.parent.criteria, self.parent.items_names = \
                    compute_topsis(self.parent.file_name, self.parent.crit_numbers)
            elif self.parent.method == "RSM":
                rank, self.parent.n, self.parent.N, self.parent.p_ideal, self.parent.p_anti_ideal, \
                    self.parent.quo_point_median, self.parent.quo_point_mean, \
                    self.parent.criteria, self.parent.items_names = \
                    compute_rsm(self.parent.file_name, self.parent.crit_numbers)
            elif self.parent.method == "SP-CS":
                rank, self.parent.n, self.parent.data_0, self.parent.data_1, self.parent.quo_point_mean, \
                    self.parent.quo_point_median, self.parent.quo_point_random, self.parent.dap1, self.parent.dap2, \
                    self.parent.dap3, self.parent.criteria, self.parent.items_names = \
                    compute_sp_cs(self.parent.file_name, self.parent.crit_numbers)
                if self.parent.n != 2:
                    rank = "UWAGA! Metoda bierze pod uwagę tylko 2 pierwsze kryteria.\n" + rank
            else:
                rank, self.parent.n, self.parent.N, self.parent.p_ideal, self.parent.p_anti_ideal, \
                    self.parent.criteria, self.parent.items_names = compute_topsis(self.parent.file_name)
            self.results.setText(rank)
        else:
            QMessageBox.warning(self, "Brak danych", "Najpierw załaduj dane w oknie Konfiguracja",
                                buttons=QMessageBox.StandardButton.Ok)


class Sheet(QWidget):

    def __init__(self, parent: MainWindow):
        """
        Zakładka z arkuszem danych
        :param parent: (MainWindow) : okno rodzic
        """
        super(Sheet, self).__init__()

        self.parent = parent  # wskaźnik na rodzica

        layout = QVBoxLayout()  # układ
        self.setLayout(layout)

        self.table = QTableWidget()  # widżet tabela
        layout.addWidget(self.table)

        self.button = QPushButton("Załaduj arkusz")  # przycisk na załadowanie arkusza
        self.button.clicked.connect(self.load_excel_data)  # przypisanie akcji
        layout.addWidget(self.button)

    @pyqtSlot()
    def load_excel_data(self) -> None:
        """
        Załadowanie danych z arkusza Excel
        :return: None
        """
        if self.parent.file_name is not None:  # gdy jest ścieżka
            df = pd.read_excel(self.parent.file_name)  # załadowanie danych

            df.fillna(" ", inplace=True)  # zastąpienie NaN pustym str
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

    def __init__(self, parent: MainWindow):
        """
        Zakładka z wykresem
        :param parent: (MainWindow) : okno rodzic
        """
        super(Chart, self).__init__()

        self.parent = parent  # wskaźnik na rodzica

        self.figure = plt.figure()  # wykres
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.button = QPushButton("Narysuj wykres")  # przycisk na rysowanie wykresu
        self.button.clicked.connect(self.plot_graph)

        layout = QVBoxLayout()  # układ
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

    @pyqtSlot()
    def plot_graph(self) -> None:
        """
        Rysowanie wykresu
        :return: None
        """
        if self.parent.file_name is not None and self.parent.n != 0:
            if self.parent.method == "TOPSIS" and self.parent.n == 2:  # rysowanie wykresu 2 zmiennych
                self.figure.clear()
                ax = self.figure.add_subplot()
                ax.clear()
                for i in range(len(self.parent.items_names)):
                    ax.scatter(self.parent.N[0][i], self.parent.N[1][i], label=self.parent.items_names[i])
                ax.scatter(self.parent.p_ideal[0], self.parent.p_ideal[1], marker="s", label="Punkt idealny")
                ax.scatter(self.parent.p_anti_ideal[0], self.parent.p_anti_ideal[1], marker="s",
                           label="Punkt antyidealny")
                ax.set(xlabel=self.parent.criteria[0], ylabel=self.parent.criteria[1],
                       title="Parametry sprzętów na tle punktów idealnych metody TOPSIS")
                ax.legend()
                self.canvas.draw()
            elif self.parent.method == "TOPSIS" and self.parent.n != 2:
                criterion_choice = CriterionChoiceDialog(self, self.parent.criteria)  # wybór kryteriów do wyrysowania
                criterion_choice.exec()
                for idx, name in enumerate(self.parent.criteria):
                    if criterion_choice.criterion1 == name:
                        idx1 = idx
                    if criterion_choice.criterion2 == name:
                        idx2 = idx
                self.figure.clear()
                ax = self.figure.add_subplot()
                ax.clear()
                for i in range(len(self.parent.items_names)):  # rysowanie wykresu dla wybranych kryteriów
                    ax.scatter(self.parent.N[idx1][i], self.parent.N[idx2][i], label=self.parent.items_names[i])
                ax.scatter(self.parent.p_ideal[idx1], self.parent.p_ideal[idx2], marker="s", label="Punkt idealny")
                ax.scatter(self.parent.p_anti_ideal[idx1], self.parent.p_anti_ideal[idx2], marker="s",
                           label="Punkt antyidealny")
                ax.set(xlabel=criterion_choice.criterion1, ylabel=criterion_choice.criterion2,
                       title="Parametry sprzętów na tle punktów idealnych metody TOPSIS")
                ax.legend()
                self.canvas.draw()
            elif self.parent.method == "SP-CS":
                self.figure.clear()
                ax = self.figure.add_subplot()
                ax.clear()
                ax.plot([self.parent.quo_point_mean[0], self.parent.dap1[0]],
                        [self.parent.quo_point_mean[1], self.parent.dap1[1]])
                ax.plot([self.parent.quo_point_median[0], self.parent.dap2[0]],
                        [self.parent.quo_point_median[1], self.parent.dap2[1]])
                ax.plot([self.parent.quo_point_random[0], self.parent.dap3[0]],
                        [self.parent.quo_point_random[1], self.parent.dap3[1]])
                ax.scatter(self.parent.quo_point_mean[0], self.parent.quo_point_mean[1], label="punkt quo średnia", marker="s")
                ax.scatter(self.parent.quo_point_median[0], self.parent.quo_point_median[1], label="punkt quo mediana", marker="s")
                ax.scatter(self.parent.quo_point_random[0], self.parent.quo_point_random[1], label="punkt quo losowy", marker="s")
                ax.scatter(
                    [self.parent.dap1[0], self.parent.dap2[0], self.parent.dap3[0]],
                    [self.parent.dap1[1], self.parent.dap2[1], self.parent.dap3[1]],
                    label="punkt aspiracji", marker="s")

                for idx in range(len(self.parent.data_0)):
                    ax.scatter(self.parent.data_0[idx], self.parent.data_1[idx], label=self.parent.items_names[idx])
                ax.set(xlabel=self.parent.criteria[0], ylabel=self.parent.criteria[1],
                       title="Krzywa szkieletowa dla metody SP-CS")
                ax.legend()
                self.canvas.draw()
            elif self.parent.method == "RSM" and self.parent.n == 2:
                self.figure.clear()
                ax = self.figure.add_subplot()
                ax.clear()
                d = [0. for _ in range(2)]
                for i in range(len(self.parent.N[0])):
                    for j in range(2):
                        d[j] = self.parent.N[j][i]
                    ax.scatter(d[0], d[1], label=self.parent.items_names[i])
                ax.scatter(self.parent.p_ideal[0], self.parent.p_ideal[1],
                           marker="s", label="Punkt idealny")
                ax.scatter(self.parent.p_anti_ideal[0], self.parent.p_anti_ideal[1],
                           marker="s", label="Punkt antyidealny")
                ax.scatter(self.parent.quo_point_mean[0], self.parent.quo_point_mean[1],
                           label="punkt quo średnia", marker="s")
                ax.scatter(self.parent.quo_point_median[0], self.parent.quo_point_median[1],
                           label="punkt quo mediana", marker="s")
                ax.set(xlabel=self.parent.criteria[0], ylabel=self.parent.criteria[1],
                       title="Wykres elementów dla metody RSM")
                ax.legend()
                self.canvas.draw()
            elif self.parent.method == "RSM" and self.parent.n == 3:
                self.figure.clear()
                ax = self.figure.add_subplot(111, projection='3d')
                ax.clear()
                d = [0. for _ in range(3)]
                for i in range(len(self.parent.N[0])):
                    for j in range(3):
                        d[j] = self.parent.N[j][i]
                    ax.scatter(d[0], d[1], d[2], label=self.parent.items_names[i])
                ax.scatter(self.parent.p_ideal[0], self.parent.p_ideal[1], self.parent.p_ideal[2],
                           marker="s", label="Punkt idealny")
                ax.scatter(self.parent.p_anti_ideal[0], self.parent.p_anti_ideal[1], self.parent.p_anti_ideal[2],
                           marker="s", label="Punkt antyidealny")
                ax.scatter(self.parent.quo_point_mean[0], self.parent.quo_point_mean[1], self.parent.quo_point_mean[2],
                           label="punkt quo średnia", marker="s")
                ax.scatter(self.parent.quo_point_median[0], self.parent.quo_point_median[1],
                           self.parent.quo_point_median[2], label="punkt quo mediana", marker="s")
                ax.set(xlabel=self.parent.criteria[0], ylabel=self.parent.criteria[1], zlabel=self.parent.criteria[2],
                       title="Wykres elementów dla metody RSM")
                ax.legend(prop={'size': 5})
                self.canvas.draw()
        else:
            QMessageBox.warning(self, "Brak danych", "Najpierw załaduj i wylicz dane w oknie Konfiguracja",
                                buttons=QMessageBox.StandardButton.Ok)  # ostrzeżenie


class CriterionChoiceDialog(QDialog):

    def __init__(self, parent: MainWindow, criteria: List[str]):
        """
        Okno dialogowe, które pyta o kryteria do wyrysowania
        :param parent: (MainWindow) : okno rodzic
        :param criteria: (List[str]) : lista kryteriów dostępnych do wyboru
        """
        super().__init__(parent)

        self.setModal(False)
        self.setFixedSize(300, 150)
        self.setWindowTitle("Wybór kryteriów")

        self.criteria = criteria
        self.criterion1 = self.criteria[0]
        self.criterion2 = self.criteria[0]

        QBtn = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        label = QLabel("Wybierz dwa kryteria do narysowania wykresu")
        self.layout.addWidget(label)

        self.layout_choice1 = QHBoxLayout()
        self.layout_choice2 = QHBoxLayout()

        criterion1 = QLabel("Kryterium 1: ")
        combo_criterion1 = QComboBox()  # lista wyboru metod
        combo_criterion1.addItems(self.criteria)  # dostępne metody
        combo_criterion1.currentTextChanged.connect(self.choose_criterion1)  # przypisanie akcji

        self.layout_choice1.addWidget(criterion1)
        self.layout_choice1.addWidget(combo_criterion1)

        criterion2 = QLabel("Kryterium 2: ")
        combo_criterion2 = QComboBox()  # lista wyboru metod
        combo_criterion2.addItems(self.criteria)  # dostępne metody
        combo_criterion2.currentTextChanged.connect(self.choose_criterion2)  # przypisanie akcji

        self.layout_choice2.addWidget(criterion2)
        self.layout_choice2.addWidget(combo_criterion2)

        self.layout.addLayout(self.layout_choice1)
        self.layout.addLayout(self.layout_choice2)

        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

        self.show()

    ### Akcje ###

    @pyqtSlot(str)
    def choose_criterion1(self, criterion: str) -> None:
        """
        Ustawienie pierwszego kryteriów
        :param criterion: (str) : kryterium pierwsze na wykresie
        :return: None
        """
        self.criterion1 = criterion

    @pyqtSlot(str)
    def choose_criterion2(self, criterion: str) -> None:
        """
        Ustawienie drugiego kryteriów
        :param criterion: (str) : kryterium drugie na wykresie
        :return:
        """
        self.criterion2 = criterion


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    try:
        app.exec()
    except Exception:
        QMessageBox.critical(window, "Krytyczny błąd", "Aplikacja napotkała straszny błąd",
                             buttons=QMessageBox.StandardButton.Abort)
