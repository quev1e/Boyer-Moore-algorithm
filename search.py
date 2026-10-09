"""Поиск вхождений подстроки в строку."""

import time
import sys
from functools import wraps


def log_time(func):
    """Логирование времени выполнения алгоритма."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[log_time] {func.__name__} -> {elapsed:.6f} сек.", file=sys.stderr)
        return result
    return wrapper


def shift_table(sub_string: str):
    """Построение таблицы сдвигов"""

    m = len(sub_string)
    shift_table = {}

    for index in range(m - 2, -1, -1):
        # не считаем последний символ подстроки
        symbol = sub_string[index]
        if symbol not in shift_table:
            shift_table[symbol] = m - 1 - index

    return shift_table


def search_one(string, sub_string, case_sensitivity):
    """Поиск схождения одной подстроки в строку"""

    if not string or not sub_string:
        return None

    if case_sensitivity is False:
        string = string.lower()
        sub_string = sub_string.lower()

    table = shift_table(sub_string)

    n = len(string)
    m = len(sub_string)

    if m > n:
        return None

    start = 0
    result = []

    while start <= n - m:

        j = m - 1 # индекс последнего элемента в подстроке

        while j >= 0 and sub_string[j] == string[start + j]:
            j -= 1

        if j < 0:
            result.append(start)
            start += 1

        else:
            bad_symbol = string[start + j]
            shift = table.get(bad_symbol, m)
            start += shift

    if not result:
        return None

    return tuple(result)


@log_time
def search(string, sub_string, case_sensitivity, method, count):
    """Шаблон функции поиска"""
    if not string or not sub_string:
        return None

    if isinstance(sub_string, tuple):

        result_list = []
        result_dict = {element: [] for element in sub_string}

        for element in sub_string:
            result = search_one(string, element, case_sensitivity)

            if result:
                for position in result:
                    result_list.append((element, position))

        if method == "first":
            result_list.sort(key=lambda x: x[1])
        else:
            result_list.sort(key=lambda x: x[1], reverse=True)

        if count is not None:
            result_list = result_list[:count]

        for element, position in result_list:
            result_dict[element].append((position))

        for element in result_dict:
            if result_dict[element]:
                result_dict[element] = tuple(result_dict[element])
            else:
                result_dict[element] = None

        return result_dict

    result = search_one(string, sub_string, case_sensitivity)

    if not result:
        return None

    if method == "first":
        result = result[:count]
    else:
        result = reversed(result)
        result = list(result)[:count]

    return tuple(result)
