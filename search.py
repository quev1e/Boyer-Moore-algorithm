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


def shift_table(sub_string: str) -> dict[str, int]:
    """Последняя позиция каждого символа в шаблоне."""
    return {
        symbol: index
        for index, symbol in enumerate(sub_string)
    }


def search_one(
    string: str,
    sub_string: str,
    case_sensitivity: bool = True
):
    """Поиск всех вхождений одной подстроки в строку."""

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

    result = []
    start = 0

    while start <= n - m:
        j = m - 1

        while j >= 0 and sub_string[j] == string[start + j]:
            j -= 1

        if j < 0:
            result.append(start)
            start += 1
        else:
            bad_symbol = string[start + j]
            last_index = table.get(bad_symbol, -1)
            start += max(1, j - last_index)

    return tuple(result) if result else None

def search_many(
    string: str,
    sub_string: list[str] | tuple[str, ...],
    case_sensitivity: bool = True,
    method: str = 'first',
    count: int | None = None
    ) -> dict[str, tuple[int, ...] | None] | None:
    """Поиск нескольких подстрок."""

    result_list = [
        (element, position)
        for element in sub_string
        for position in (search_one(string, element, case_sensitivity) or ())
    ]
    result_list.sort(key=lambda x: x[1], reverse=method == "last")
    if count is not None:
        result_list = result_list[:count]

    result_dict = {element: [] for element in sub_string}
    for element, position in result_list:
        result_dict[element].append(position)

    return {
        element: tuple(positions) if positions else None
        for element, positions in result_dict.items()
    }

@log_time
def search(
    string: str,
    sub_string: str | list[str] | tuple[str, ...],
    case_sensitivity: bool = True,
    method: str = 'first',
    count: int | None = None
    ) -> tuple[int, ...] | dict[str, tuple[int, ...] | None] | None:
    """Шаблон функции поиска"""
    if not string or not sub_string:
        return None

    if isinstance(sub_string, (list, tuple)):
        return search_many(
            string, tuple(sub_string), case_sensitivity, method, count
        )

    result = search_one(string, sub_string, case_sensitivity)
    if not result:
        return None

    if method == "last":
        result.reverse()
        result = tuple(result)
    if count is not None:
        result = result[:count]
    return result
