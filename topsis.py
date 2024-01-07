from typing import List, Union, Optional, Tuple
from math import sqrt
import pandas as pd
import numpy as np
from scipy.spatial.distance import braycurtis, chebyshev, canberra, cityblock

Number = Union[float, int]


def euclid_norm(D: List[List], j: int) -> float:
    """
    Norma euklidesowa kolumny j z macierzy D
    :param D: (List[List[Number]]) : macierz decyzyjna
    :param j: (int) : indeks kolumny kryterium
    :return: pierwiastek sumy kwadratów
    """
    s = 0.0  # suma kwadratów elementów z kolumny
    for i in range(len(D)):
        s += D[j][i] ** 2
    return sqrt(s)


def topsis(D: List[List[Number]], W: List[Number], metric: str, W_max: Optional[List[bool]] = None) \
        -> Tuple[List[float], int, List[List[float]], List[float], List[float]]:
    """
    Metoda topsis tworząca ranking produktów
    :param D: (List[List[Number]]) : macierz decyzjna D[m x N]
    :param W: (List[Number]) : wektor wag
    :param W_max: (List[bool]) : wektor logiczny określający, które maksymalizujemy kryterium (domyślnie każde)
    :param metric: str : nazwa wykorzystywanej metryki
    :return: (Tuple[List[float], int, List[List[float]], List[float], List[float]]) : wektor współczynników skoringowych
    liczba kryetriów, macierz znormalizowana, punkty idealne, punkty antyidealne
    """
    print(D)
    m = len(D[0])  # liczba elementów
    n = len(D)  # liczba kryteriow
    N = [[0.0 for _ in range(m)] for _ in range(n)]  # macierz znormalizowana
    p_ideal = [0.0 for _ in range(n)]  # tablica punktów idealnych
    p_anti_ideal = [float('inf') for _ in range(n)]  # tablica punktów antyidealnych
    d_star = [0.0 for __ in range(m)]  # tablica odległości od punktu idealnego
    d_minus = [0.0 for __ in range(m)]  # tablica odległości od punktu nieidealnego
    c = [0.0 for __ in range(m)]  # współczynnik skoringowy

    if W_max is not None:  # minimalizacja czy maksymalizacja kryterium
        for i in range(len(W_max)):
            if not W_max[i] and i < n:
                p_ideal[i] = float('inf')
                p_anti_ideal[i] = 0
    else:
        W_max = [True for _ in range(n)]  # uzupełnienie parametru domyślnego


    for j in range(n):
        en = euclid_norm(D, j)
        for i in range(m):
            N[j][i] = W[j] * D[j][i] / en  # normalizacja macierzy
            if W_max[j] and p_ideal[j] < N[j][i]:  # znalezienie punktów idealnych
                p_ideal[j] = N[j][i]
            if not W_max[j] and p_ideal[j] > N[j][i]:
                p_ideal[j] = N[j][i]
            if W_max[j] and p_anti_ideal[j] > N[j][i]:
                p_anti_ideal[j] = N[j][i]
            if not W_max[j] and p_anti_ideal[j] < N[j][i]:
                p_anti_ideal[j] = N[j][i]

    if metric == "Default":
        for i in range(m):  # obliczenie odległości
            s_star = 0.0  # suma kwadratów róznicy punktu od punktu idealnego
            s_minus = 0.0  # suma kwadratów róznicy punktu od punktu antyidealnego
            for j in range(n):
                s_star += (N[j][i] - p_ideal[j]) ** 2
                s_minus += (N[j][i] - p_anti_ideal[j]) ** 2
            d_star[i] = sqrt(s_star)
            d_minus[i] = sqrt(s_minus)
            c[i] = d_minus[i] / (d_minus[i] + d_star[i])

    elif metric == "Bray-Curtis":
        N_as_array = np.asarray(N)
        p_ideal_as_vector = np.asarray(p_ideal)
        p_anti_ideal_as_vector = np.asarray(p_anti_ideal)
        for i in range(m):
            d_star[i] = braycurtis(N_as_array[:, i], p_ideal_as_vector)
            d_minus[i] = braycurtis(N_as_array[:, i], p_anti_ideal_as_vector)
            c[i] = d_minus[i] / (d_minus[i] + d_star[i])

    elif metric == "Canberra":
        N_as_array = np.asarray(N)
        p_ideal_as_vector = np.asarray(p_ideal)
        p_anti_ideal_as_vector = np.asarray(p_anti_ideal)
        for i in range(m):
            d_star[i] = canberra(N_as_array[:, i], p_ideal_as_vector)
            d_minus[i] = canberra(N_as_array[:, i], p_anti_ideal_as_vector)
            c[i] = d_minus[i] / (d_minus[i] + d_star[i])

    elif metric == "Chebyshev":
        N_as_array = np.asarray(N)
        p_ideal_as_vector = np.asarray(p_ideal)
        p_anti_ideal_as_vector = np.asarray(p_anti_ideal)
        for i in range(m):
            d_star[i] = chebyshev(N_as_array[:, i], p_ideal_as_vector)
            d_minus[i] = chebyshev(N_as_array[:, i], p_anti_ideal_as_vector)
            c[i] = d_minus[i] / (d_minus[i] + d_star[i])

    elif metric == "City Block":
        N_as_array = np.asarray(N)
        p_ideal_as_vector = np.asarray(p_ideal)
        p_anti_ideal_as_vector = np.asarray(p_anti_ideal)
        for i in range(m):
            d_star[i] = cityblock(N_as_array[:, i], p_ideal_as_vector)
            d_minus[i] = cityblock(N_as_array[:, i], p_anti_ideal_as_vector)
            c[i] = d_minus[i] / (d_minus[i] + d_star[i])

    return c, n, N, p_ideal, p_anti_ideal


def compute_topsis(file_name: str, criteria: List[int], metric: str, weights: List[float]) -> Tuple[str, int, List[List[float]], List[float], List[float], List[str], List[str]]:
    """
    Funkcja wyliczająca z pliku ranking metodą topsis
    :param file_name: (str) : nazwa pliku
    :param criteria: (List[int]) : lista wybranych kryteriów
    :param metric: str : metryki
    :param weights: List[float] : lista wag podana przez użytkownika
    :return: (Tuple[str, int, List[List[float]], List[float], List[float]], str, str, List[str]) : wektor współczynników
    skoringowych jako str, liczba kryetriów, macierz znormalizowana, punkty idealne, punkty antyidealne,
    lista nazw kryetriów, lista nazw sprzętów
    """
    df = pd.read_excel(file_name)  # wczytanie excel z bazą słuchawek

    if not weights or weights is None:  # jeśli użytkownik nie podał wag (na razie się tak nie da) to wybierz je z pliku
        W = df['Wagi'].dropna().tolist()  # wektor wag
    else:
        W = weights

    W_max = df['Maksymalizacja'].dropna().tolist()  # wektor logiczny określający, które maksymalizujemy kryterium
    D = []  # macierz decyzyjna
    c_names = []  # wektor nazw kryteriów
    criteria = sorted(criteria)
    for j in df.columns:

        if j == 'Lp.' or j == 'Nazwa' or df.columns.get_loc(j) - 1 not in criteria:
            continue
        if j == 'Wagi':
            break
        D.append(df[j].tolist())
        c_names.append(j)

    c, n, N, p_ideal, p_anti_ideal = topsis(D, W, metric, W_max)  # tworzenie rankingu

    rank = []
    items_names = []
    for i in range(len(D[0])):
        rank.append((df['Nazwa'][i], c[i]))
        items_names.append(df['Nazwa'][i])

    rank.sort(key=lambda tup: tup[1], reverse=True)  # posortowanie rankingu

    rank_str = ''
    for name, score in rank:
        rank_str += name + ' : ' + '{0:1.3f}'.format(score) + '\n'  # zapis rankingu jako str

    return rank_str, n, N, p_ideal, p_anti_ideal, c_names, items_names
