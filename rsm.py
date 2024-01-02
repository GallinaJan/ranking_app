from typing import List, Tuple, Optional, Union

import numpy as np
import pandas as pd
from math import sqrt
from scipy.spatial.distance import braycurtis, chebyshev, canberra, cityblock

Number = Union[float, int]


def rsm(D: List[List[Number]], W_max: Optional[List[bool]], metric: str) -> Tuple[List[float], List[Number], List[Number],
                                                                    List[Number], List[Number]]:
    """
    Funkcja wyliczająca ranking metodą SP-CS
    :param D: (List[List[Number) : macierz elementów
    :param W_max: (List[bool]) : wektor maksymalizacji kryteriów
    :param metric: (str) : nazwa wykorzystywanej metryki
    :return: (Tuple[str, int, List[Number], List[Number], List[Number], List[Number]) : wektor współczynników
    skoringowych, punkt aspiracji, punkt antyidealny, punkt quo mediana, punkt quo średnia
    """
    m = len(D[0])  # liczba elementów
    n = len(D)  # liczba kryteriow

    aspiration_idx_set = set()  # zbiór indeksów punktu aspiracji
    aspiration_value = []  # wartości punktu aspiracji
    anti_ideal_point = []  # punkt antyidealny
    opt_threshold = []  # punkt graniczny
    quo_point_mean = []  # punkt quo średnia
    quo_point_median = []  # punkt quo mediana
    for j in range(n):  # dla każdego kryterium
        best_idxs = []
        if W_max[j]:  # posorotwanie od wartości
            elements_sorted = [(idx, v) for idx, v in enumerate(D[j])]
            elements_sorted.sort(key=lambda tup: tup[1], reverse=True)
        else:
            elements_sorted = [(idx, v) for idx, v in enumerate(D[j])]
            elements_sorted.sort(key=lambda tup: tup[1])
        best_value = elements_sorted[0][1]
        worst_value = elements_sorted[-1][1]
        if W_max[j]:
            opt_threshold.append(abs(best_value - worst_value) * 0.25 + worst_value)
        else:
            opt_threshold.append(abs(best_value - worst_value) * 0.25 + best_value)
        anti_ideal_point.append(worst_value)
        aspiration_value.append(best_value)
        quo_point_mean.append(abs(best_value - worst_value) / 2)
        quo_point_median.append(elements_sorted[m // 2][1])
        best_idxs.append(elements_sorted[0][0])
        k = 1
        while best_value == elements_sorted[k][1]:
            best_idxs.append(elements_sorted[k][0])  # zebranie punktów o najlepszych wartościach
            k += 1
        for idx in best_idxs:
            aspiration_idx_set.add(idx)

    pareto = []  # wyznaczenie punktów niezdominowanych
    for i in range(m):
        dominated = True
        for j in range(n):
            if W_max[j]:
                if D[j][i] >= opt_threshold[j]:
                    dominated = False
                    break
            else:
                if D[j][i] <= opt_threshold[j]:
                    dominated = False
                    break
        if not dominated:
            pareto.append(i)

    """
    # sprawodzenie czy punkty quo nie są zdominowane
    median_is_greater = []
    for i in range(n):
        median_is_greater.append(quo_point_median[i] > quo_point_mean[i])
    if len(set(median_is_greater)) == 1:
        raise ValueError("Punkty quo zdominowane")
    """

    data = []  # wyznaczenie współrzędnych punktów niezdominowanych
    for i in range(n):
        criterion = []
        for idx in pareto:
            criterion.append(D[i][idx])
        data.append(criterion)

    if metric == "Default":
        d_square_aspiration = [0. for _ in range(len(data[0]))]  # wyznaczenie odległości punktów od punktu aspiracji
        for i in range(n):
            for j in range(len(data[0])):
                d_square_aspiration[j] += (data[i][j] - aspiration_value[i]) ** 2
        d_aspiration = [sqrt(elem) for elem in d_square_aspiration]
        d_aspiration_n = [elem / max(d_aspiration) for elem in d_aspiration]

        d_square_quo_mean = [0. for _ in range(len(data[0]))]  # wyznaczenie odległości punktów od punktu quo średniej
        for i in range(n):
            for j in range(len(data[0])):
                d_square_quo_mean[j] += (data[i][j] - quo_point_mean[i]) ** 2
        d_quo_mean = [sqrt(elem) for elem in d_square_quo_mean]
        d_quo_mean_n = [elem / max(d_quo_mean) for elem in d_quo_mean]

        d_square_quo_median = [0. for _ in range(len(data[0]))]  # wyznaczenie odległości punktów od punktu quo mediana
        for i in range(n):
            for j in range(len(data[0])):
                d_square_quo_median[j] += (data[i][j] - quo_point_median[i]) ** 2
        d_quo_median = [sqrt(elem) for elem in d_square_quo_median]
        d_quo_median_n = [elem / max(d_quo_median) for elem in d_quo_median]

    elif metric == "Bray-Curtis":
        d_aspiration = []
        d_quo_mean = []
        d_quo_median = []
        data_as_array = np.asarray(data)
        for i in range(len(data[0])):
            aspiration_value_as_vector = np.asarray(aspiration_value)
            quo_mean_as_vector = np.asarray(quo_point_mean)
            quo_median_as_vector = np.asarray(quo_point_median)
            d_aspiration.append(braycurtis(data_as_array[:, i], aspiration_value_as_vector))
            d_quo_mean.append(braycurtis(data_as_array[:, i], quo_mean_as_vector))
            d_quo_median.append(braycurtis(data_as_array[:, i], quo_median_as_vector))

        d_aspiration_n = [elem / max(d_aspiration) for elem in d_aspiration]    # normalizacja
        d_quo_mean_n = [elem / max(d_quo_mean) for elem in d_quo_mean]
        d_quo_median_n = [elem / max(d_quo_median) for elem in d_quo_median]

    elif metric == "Canberra":  # każda kolejna metryka tak samo tylko, że zmienia się funkcja scipy
        d_aspiration = []
        d_quo_mean = []
        d_quo_median = []
        data_as_array = np.asarray(data)
        for i in range(len(data[0])):
            aspiration_value_as_vector = np.asarray(aspiration_value)
            quo_mean_as_vector = np.asarray(quo_point_mean)
            quo_median_as_vector = np.asarray(quo_point_median)
            d_aspiration.append(canberra(data_as_array[:, i], aspiration_value_as_vector))
            d_quo_mean.append(canberra(data_as_array[:, i], quo_mean_as_vector))
            d_quo_median.append(canberra(data_as_array[:, i], quo_median_as_vector))

        d_aspiration_n = [elem / max(d_aspiration) for elem in d_aspiration]
        d_quo_mean_n = [elem / max(d_quo_mean) for elem in d_quo_mean]
        d_quo_median_n = [elem / max(d_quo_median) for elem in d_quo_median]

    elif metric == "Chebyshev":
        d_aspiration = []
        d_quo_mean = []
        d_quo_median = []
        data_as_array = np.asarray(data)
        for i in range(len(data[0])):
            aspiration_value_as_vector = np.asarray(aspiration_value)
            quo_mean_as_vector = np.asarray(quo_point_mean)
            quo_median_as_vector = np.asarray(quo_point_median)
            d_aspiration.append(chebyshev(data_as_array[:, i], aspiration_value_as_vector))
            d_quo_mean.append(chebyshev(data_as_array[:, i], quo_mean_as_vector))
            d_quo_median.append(chebyshev(data_as_array[:, i], quo_median_as_vector))

        d_aspiration_n = [elem / max(d_aspiration) for elem in d_aspiration]
        d_quo_mean_n = [elem / max(d_quo_mean) for elem in d_quo_mean]
        d_quo_median_n = [elem / max(d_quo_median) for elem in d_quo_median]

    elif metric == "City Block":

        d_aspiration = []
        d_quo_mean = []
        d_quo_median = []
        data_as_array = np.asarray(data)
        for i in range(len(data[0])):
            aspiration_value_as_vector = np.asarray(aspiration_value)
            quo_mean_as_vector = np.asarray(quo_point_mean)
            quo_median_as_vector = np.asarray(quo_point_median)
            d_aspiration.append(cityblock(data_as_array[:, i], aspiration_value_as_vector))
            d_quo_mean.append(cityblock(data_as_array[:, i], quo_mean_as_vector))
            d_quo_median.append(cityblock(data_as_array[:, i], quo_median_as_vector))

        d_aspiration_n = [elem / max(d_aspiration) for elem in d_aspiration]
        d_quo_mean_n = [elem / max(d_quo_mean) for elem in d_quo_mean]
        d_quo_median_n = [elem / max(d_quo_median) for elem in d_quo_median]

    score = []  # wyznaczenie współczynnika scoringowego jako różnica odległości
    for j in range(len(data[0])):
        score.append(d_aspiration_n[j] - min(d_quo_median_n[j], d_quo_mean_n[j]))
    for j in range(m):
        if j not in pareto:
            score.insert(j, float('inf'))

    return score, aspiration_value, anti_ideal_point, quo_point_median, quo_point_mean


def compute_rsm(file_name: str, metric: str) -> Tuple[str, int, List[List[Number]], List[Number], List[Number], List[Number],
                                         List[Number], List[str], List[str]]:
    """
    Funkcja wyliczająca z pliku ranking metodą sp-cs
    :param file_name: (str) : nazwa pliku
    :param metric: (str) : nazwa wykorzystywanej metryki (przekazywana z gui)
    :return: (Tuple[str, int, List[List[Number]], List[Number], List[Number], List[Number], List[Number], List[str],
    List[str]]) : wektor współczynników skoringowych jako str, liczba kryetriów, punkty elementów, punkt aspiracji,
     punkt quo mediana, punkt quo średnia, lista nazw kryteriów i lista nazw elementów
    """
    df = pd.read_excel(file_name)  # wczytanie excel z bazą słuchawek
    W_max = df['Maksymalizacja'].dropna().tolist()  # wektor logiczny określający, które maksymalizujemy kryterium
    D = []  # macierz decyzyjna
    c_names = []  # wektor nazw kryteriów
    for j in df.columns:
        if j == 'Lp.' or j == 'Nazwa':
            continue
        if j == 'Wagi':
            break
        D.append(df[j].tolist())
        c_names.append(j)
    n = len(c_names)

    items_names = []
    for i in range(len(D[0])):
        items_names.append(df['Nazwa'][i])

    score, aspiration_value, anti_ideal_point, quo_point_median, quo_point_mean = rsm(D, W_max, metric)  # tworzenie rankingu

    rank = []
    for i in range(len(D[0])):
        rank.append((items_names[i], score[i]))

    rank.sort(key=lambda tup: tup[1])  # posortowanie rankingu

    rank_str = ''
    for name, score in rank:
        rank_str += name + ' : ' + '{0:1.3f}'.format(score) + '\n'  # zapis rankingu jako str

    return rank_str, n, D, aspiration_value, anti_ideal_point, quo_point_median, quo_point_mean, c_names, items_names
