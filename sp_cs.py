from typing import List, Tuple, Optional, Union
import random
import pandas as pd
from math import sqrt

Number = Union[float, int]


def sp_cs(D: List[List[Number]], W_max: Optional[List[bool]]) -> Tuple[List[float], List[Number], List[Number],
                                                                       List[float], List[Number], List[float],
                                                                       List[float], List[float], List[float]]:
    """
    Funkcja wyliczająca ranking metodą SP-CS
    :param D: (List[List[Number) : macierz elementów
    :param W_max: (List[bool]) : wektor maksymalizacji kryteriów
    :return: (Tuple[str, int, List[Number], List[Number], List[float], List[Number], List[float], List[float],
     List[float], List[float], List[str], List[str]]) : wektor współczynników skoringowych,
     punkty elementów x, punkty elementów y, punkty quo, punkty aspiracji
    """
    m = len(D[0])  # liczba elementów
    n = len(D)  # liczba kryteriow

    aspiration_idx_set = set()  # zbiór indeksów punktu aspiracji
    aspiration_value = []  # wartości punktu aspiracji
    quo_point_mean = []  # punkt quo średnia
    quo_point_median = []  # punkt quo mediana
    quo_point_random = []  # punkt quo losowo
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
        aspiration_value.append(best_value)
        quo_point_mean.append(abs(best_value - worst_value) / 2)
        quo_point_median.append(elements_sorted[m // 2][1])
        quo_point_random.append(abs(best_value - worst_value) * random.random() + worst_value)
        best_idxs.append(elements_sorted[0][0])
        k = 1
        while best_value == elements_sorted[k][1]:
            best_idxs.append(elements_sorted[k][0])  # zebranie punktów o najlepszych wartościach
            k += 1
        for idx in best_idxs:
            aspiration_idx_set.add(idx)

    aspiration_idx = list(aspiration_idx_set)

    threshold_value = []  # wyznaczenie granicy do znalezienia punktów zdominowanych
    for j in range(n):
        if W_max[j]:
            worst_value = float('inf')
            for i in aspiration_idx:
                if D[j][i] < worst_value:
                    worst_value = D[j][i]
        else:
            worst_value = 0
            for i in aspiration_idx:
                if D[j][i] > worst_value:
                    worst_value = D[j][i]
        threshold_value.append(worst_value)

    not_dominated_idx = []  # wyznaczenie punktów niezdominowanych
    for i in range(m):
        dominated = True
        for j in range(n):
            if W_max[j]:
                if D[j][i] >= threshold_value[j]:
                    dominated = False
                    break
            else:
                if D[j][i] <= threshold_value[j]:
                    dominated = False
                    break
        if not dominated:
            not_dominated_idx.append(i)

    disrupted_aspiration_point1 = [coord * (0.9 + random.random() * 0.2) for coord in aspiration_value]
    disrupted_aspiration_point2 = [coord * (0.85 + random.random() * 0.3) for coord in aspiration_value]
    disrupted_aspiration_point3 = [coord * (0.8 + random.random() * 0.4) for coord in aspiration_value]

    data_0 = []
    data_1 = []
    for idx in not_dominated_idx:
        data_0.append(D[0][idx])
        data_1.append(D[1][idx])

    score_sum = [0. for _ in range(len(data_0))]
    for quo_point, aspiration_point in [(quo_point_mean, disrupted_aspiration_point1),
                                        (quo_point_median, disrupted_aspiration_point2),
                                        (quo_point_random, disrupted_aspiration_point3)]:
        a = (quo_point[1] - aspiration_point[1]) / (quo_point[0] - aspiration_point[0])
        b = quo_point[1] - a * quo_point[0]
        d = sqrt((quo_point[0] - aspiration_point[0]) ** 2 + (quo_point[1] - aspiration_point[1]) ** 2)
        score1 = []  # odległość znormalizowana rzutu między punktem quo a aspiracji
        score2 = []  # odległość nieznormalizowana od prostej między quo a aspiracji
        for point_idx in range(len(data_0)):
            a_p = -1 / a
            b_p = data_1[point_idx] - a_p * data_0[point_idx]
            x = (b_p - b) / (a - a_p)
            y = a * x + b
            d1 = sqrt((quo_point[0] - x) ** 2 + (quo_point[1] - y) ** 2)
            d2 = sqrt((x - aspiration_point[0]) ** 2 + (y - aspiration_point[1]) ** 2)
            if 0.99 * d < d1 + d2 < 1.01 * d:
                score1.append(d1 / d)
            elif d1 > d2:
                score1.append(1 + d2 / d)
            elif d2 > d1:
                score1.append(-d1 / d)
            h = sqrt((x - data_0[point_idx]) ** 2 + (y - data_1[point_idx]) ** 2)
            score2.append(h)
        score2 = [-el / max(score2) for el in score2]  # normalizacja score2

        for i in range(len(score_sum)):
            score_sum[i] += score1[i] + score2[i]

    score = [el / 3 for el in score_sum]
    return score, data_0, data_1, quo_point_mean, quo_point_median, quo_point_random, disrupted_aspiration_point1, \
           disrupted_aspiration_point2, disrupted_aspiration_point3


def compute_sp_cs(file_name: str) -> Tuple[str, int, List[Number], List[Number], List[float], List[Number], List[float],
                                           List[float], List[float], List[float], List[str], List[str]]:
    """
    Funkcja wyliczająca z pliku ranking metodą sp-cs
    :param file_name: (str) : nazwa pliku
    :return: (Tuple[str, int, List[Number], List[Number], List[float], List[Number], List[float], List[float],
     List[float], List[float], List[str], List[str]]) : wektor współczynników skoringowych jako str, liczba kryetriów,
     punkty elementów x, punkty elementów y, punkty quo, punkty aspiracji, lista nazw kryteriów i lista nazw elementów
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

    score, data_0, data_1, quo_point_mean, quo_point_median, quo_point_random, disrupted_aspiration_point1, \
    disrupted_aspiration_point2, disrupted_aspiration_point3 = sp_cs(D, W_max)  # tworzenie rankingu

    rank = []
    for i in range(len(D[0])):
        rank.append((items_names[i], score[i]))

    rank.sort(key=lambda tup: tup[1], reverse=True)  # posortowanie rankingu

    rank_str = ''
    for name, score in rank:
        rank_str += name + ' : ' + '{0:1.3f}'.format(score) + '\n'  # zapis rankingu jako str

    return rank_str, n, data_0, data_1, quo_point_mean, quo_point_median, quo_point_random, \
           disrupted_aspiration_point1, disrupted_aspiration_point2, disrupted_aspiration_point3, c_names, items_names
